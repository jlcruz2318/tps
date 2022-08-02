import boto3
import cv2
from PIL import Image # ImageFile
# ImageFile.LOAD_TRUNCATED_IMAGES = True
from imutils import paths
import imutils
import numpy as np
import socket
import threading
import time

# Socket Connection
HEADER = 64
PORT = 10500 # VERIFY WHICH PORT TO USE
SERVER = ''
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
REQUEST_KEY = 'V*ESK~_DYH89hc?T'
DISCONNECT_MESSAGE = "!TRANSMISSION_COMPLETE"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Node Data
PARENT_NODE = '2' # THIS NEEDS TO BE FILLED IN FOR EACH MONITOR
SECTION_NODE_ID = '2' # THIS NEEDS TO BE FILLED IN FOR EACH MONITOR
NODE_ID = f'{PARENT_NODE}-{SECTION_NODE_ID}'

# Section and Node Constants
SECTION_NODES = ['192.168.0.16']
node_communication_time = {}


# Define will be used for data processsing
SECTION_PIXEL_WIDTH = int()
# SCALE_FACTOR = 

def capture_image_as_parent(time_stamp):
    # Establish Time of Capture
    node_communication_time[NODE_ID] = time_stamp

    #Capture and Save Image
    cam = cv2.VideoCapture(0)
    retval, frame = cam.read()
    if retval != True:
        raise ValueError("Can't read frame")
    cv2.imwrite(f'images/{NODE_ID}.jpeg', frame)
    # cv2.imshow("img1", frame); cv2.waitKey() # Debug Line to view Image

def request_child_data(CHILD_IP, PORT=PORT, REQUEST_KEY=REQUEST_KEY, REQUEST_TIME = f'{time.localtime().tm_min}:{time.localtime().tm_sec}'):
    server.connect((CHILD_IP, PORT))
    request_message = f'{REQUEST_KEY} {REQUEST_TIME}'.encode(FORMAT)
    request_message += b' ' * (HEADER - len(request_message))
    server.send(request_message)
    server.close()
    


def receive_child_data(conn,addr):

    print(f"[RECEIVING DATA] PARENT NODE CONNECTED TO {addr} [END MESSAGE]")
    if addr[0] in SECTION_NODES:
        connected = True

        while connected:
            incoming_message = conn.recv(HEADER).decode(FORMAT)
            if incoming_message: 
                img_size, child_node_id, time_stamp = incoming_message.rstrip(' ').split(' ')

                image_as_bytes = bytearray()

                while True:
                    msg = conn.recv(4096)
                    image_as_bytes += msg
                    
                    if int(len(image_as_bytes)) == int(img_size):
                        print(f'[TRANSFER COMPLETE] {image_as_bytes} total bytes transferred.')
                        break

                file_jpeg_name = f'images/{child_node_id}.jpeg'
                with open(file_jpeg_name, 'wb') as f:
                    f.write(image_as_bytes)

                connected = False

    conn.close()
    print(f"[TRANSMISSION COMPLETE] PARENT NODE DISCONNECTED FROM {addr} [END MESSAGE]")


def stitch_images():

    print('[STITCH PROCESS STARTED')
    imagePaths = sorted(list(paths.list_images('images')))
    images = []

    for imagePath in imagePaths:
        image = cv2.imread(imagePath)
        images.append(image)
        
    print(f'{len(images)} images loaded.\n [STITCHING IMAGES]')

    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    (status, stitched) = stitcher.stitch(images)

    if status == 0:

        cv2.imwrite(f'{PARENT_NODE}.png', stitched)
        return f'{PARENT_NODE}.png'

        # #Debug 
        cv2.imshow('Stitched Image', stitched)
        cv2.waitKey(0)

    else:
        print('[STITCHING PROCESS FAILED')


def detect_vehicles(image_name):
    client = boto3.client('rekognition')
    received_image = image_name

    with open(received_image, 'rb') as source_image:
        source_bytes = source_image.read()

    response = client.detect_labels(Image={'Bytes': source_bytes}, MaxLabels=1)

    car_detection_data = {}
    for label in response['Labels']:
        for boundingbox in label['Instances']:
            width, left = boundingbox['BoundingBox']['Width'], boundingbox['BoundingBox']['Left']
            print(f'Width : {width} , Left: {left}')
            
            car_detection_data




def determine_parking():
    # numpy
    pass






def start():
    # Capture Image

    request_child_data('192.168.0.16')
    while True:
        server.listen()
        conn, addr = server.accept()
        thread = threading.Thread(target=receive_child_data, args=(conn,addr))
        thread.start()




if __name__ == '__main__':
    start()
