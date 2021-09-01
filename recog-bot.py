import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
import requests
import re
import json
import pika
import _thread

# setting up RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host="127.0.0.1"))
channel = connection.channel()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

watch_list = []
bot = Bot(token='')

# Send a message when the command /start is issued
def start(update, context):
    update.message.reply_text(f"Welcome {update.message.chat.first_name} to Recog AI Bot !\n\n - Use /help to know the possible commands")


def help(update, context):
    update.message.reply_text("Use /watch deviceName for receiving alerts from the specified device")

def watch(update, context):
    watch_list.append(
        {
            "name":f"{update.message.chat.first_name} {update.message.chat.last_name}",
            "user":update.message.chat.username,
            "chat_id":update.message.chat.id,
            "device":context.args[0]
        }
    )
    update.message.reply_text(f"Your name has been added on watch list for device: {context.args[0]}")

# sends a message for users that are watching an device 
def send_broadcast_by_device(device):
    global bot
    filtered_users = [ user for user in watch_list if user["device"] == str(device) ] 
    for user in filtered_users:
        bot.send_message(text=f"Device {user['device']} has detected human presence", chat_id=user["chat_id"])


def echo(update, context):
    update.message.reply_text(update.message.text)

# queue callback function
def queue_callback(ch, method, properties, body):
    send_broadcast_by_device(body.decode('utf-8'))

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start_queue():
    channel.exchange_declare(exchange="alerts", exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    # starts consuming from the selected topic
    channel.queue_bind(exchange="alerts", queue=queue_name, routing_key="person")
    channel.basic_consume(queue=queue_name, on_message_callback=queue_callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    updater = Updater("", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('watch', watch, pass_args=True))
    
    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # start the queue
    _thread.start_new_thread(start_queue, ())

    # Start the Bot
    updater.start_polling()

    updater.idle()
