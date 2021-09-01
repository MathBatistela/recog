import grpc
import cv2
import pika
import logging
from pb_python import frame_pb2_grpc, frame_pb2

# alert codes
ALERTS = {
    1 : "person"
}

# const config
IP = "127.0.0.1"
PORT = 50051
EXCHANGE = "alerts"
DEVICE_ID = ""

# logger config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


# setting up RabbitMQ config
connection = pika.BlockingConnection(pika.ConnectionParameters(host=IP))
channel = connection.channel()


# runs the streaming channel
def run():
    grpc_channel = grpc.insecure_channel(f"{IP}:{PORT}")
    stub = frame_pb2_grpc.ImageStreamStub(grpc_channel)
    logging.info(f"connected on {IP} port {PORT}")

    # bidirectional stream. While the clients is sending data,
    # it is also receiving the replies from server
    for response in stub.Analyse(get_live_frame()):
        if response.reply in ALERTS.keys():
            channel.basic_publish(exchange=EXCHANGE, routing_key=ALERTS[response.reply], body=bytes(DEVICE_ID, 'utf-8'))
            logging.info(f"sending '{ALERTS[response.reply]}' alert from device: {DEVICE_ID}")



def get_live_frame():
    # open webcam video stream
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        cv2.imshow("live", frame)
        # resizing for faster detection
        frame = cv2.resize(frame, (640, 480))
    
        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break

        encoded_frame = cv2.imencode(".bmp", frame)[1].tobytes()
        yield frame_pb2.MsgRequest(img=encoded_frame)

    cap.release()
    cv2.destroyAllWindows()
    logging.info(f"stopping video capturing from device: {DEVICE_ID}")

if __name__ == "__main__":
    print("\nPlease, set a name for your device:")

    DEVICE_ID = input("> ")

    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')
    run()
