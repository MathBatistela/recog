import logging
import grpc
import cv2
import schedule
import numpy as np
from pb_python import frame_pb2_grpc, frame_pb2
from concurrent import futures

# alert codes
ALERT = {
    "PERSON_DETECTED": 1
}

# const config
IP="127.0.0.1"
PORT=50051
EXCHANGE="alerts"

# logger config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)

# instantiate an implementation of HOG (Histogram of Oriented Gradients) descriptor and object detector.
HOGCV = cv2.HOGDescriptor()
# load people detector dataset with SVM algorithm
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


# received frame
frame = bytes()
# detection flag
recognized = False

# used to check if exists one person in a received frame
def detect():
    global recognized, frame
    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)

    if len(bounding_box_cordinates) > 0:
        recognized = True
        logging.info(f"detected on: {bounding_box_cordinates} ")

# detects a frame every 1 second        
schedule.every(0.5).seconds.do(detect)

# grpc frame analyzer service class
class FrameAnalyzer(frame_pb2_grpc.ImageStreamServicer):

    # method that analises video streaming input
    def Analyse(self, request_iterator, context):
        global frame, recognized

        if request_iterator:
            # _thread.start_new_thread(show_screen, (request_iterator,))
            # gets streaming data
            for req in request_iterator:

                # convert an bytearray of frame to a np array
                nparr = np.frombuffer(req.img, np.uint8)

                # convert np array ro image frame
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
                # if recognized, replies the client
                if recognized:
                    yield frame_pb2.MsgReply(reply = 1)
                    recognized = False

                # keep schedulling
                schedule.run_pending()



if __name__ == '__main__':

    # instantiates grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frame_pb2_grpc.add_ImageStreamServicer_to_server(FrameAnalyzer(), server)
    server.add_insecure_port(f"{IP}:{PORT}")

    logging.info(f"Starting up on {IP} port {PORT}")    
    server.start()
    server.wait_for_termination()