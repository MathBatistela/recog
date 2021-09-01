# Recog

Recog is an application that uses AI algorithms to classify real time video streaming from a video spot, using gRPC + Protocol buffers with the power of the HTTP/2.0 protocol.
At the moment, the app is capable to recognize people appearing in the camera's field of view. It also publishes a message in a topic over the RabbitMQ that replicate to all topic subscribers. In this repo we uses an Telegram bot as an example of subscriber, we send a message to an alert topic from video-spot with the video device ID, and the bot notify those who have declared interest in following the alerts of that device.  

### Application architecture

- Overview

![Recog diagram](../main/.media/recog-diagram.png)

- Protocol Buffers structure

```
syntax = "proto3";

service ImageStream {
  rpc Analyse (stream MsgRequest) returns (stream MsgReply) {}
}

message MsgRequest {
  bytes img = 1;
}

message MsgReply {
  int32 reply = 1;
}
```
Notice that the MsgRequest carries an image in bytes, what represents 1 video frame and the ImageStream services makes the bidirectional data stream explicit.

### External modules

- [Opencv-python](https://pypi.org/project/opencv-python/) - Pre-built CPU-only OpenCV packages for Python.

- [Pika](https://pika.readthedocs.io/en/stable/) - Pika is a pure-Python implementation of the AMQP 0-9-1 protocol that tries to stay fairly independent of the underlying network support library.
- [Grpc](https://grpc.github.io/grpc/python/) - gRPC implementation for Python.
- [Numpy](https://numpy.org/) - The fundamental package for scientific computing with Python.
- [Python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/) - Pure Python interface for the Telegram Bot API.

### Setting up
```
$ sudo apt install libopencv-dev python3-opencv   

$ python3 -m pip install -r requirements.txt
```

### Running
```
$ python3 recog-bot.py

$ python3 recog-classifier.py

$ python3 recog-video-spot.py
```
