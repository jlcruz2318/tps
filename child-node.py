
import cv2
import socket
import threading
import time



# Open a socket and send the iamge
HEADER = 64
PORT = 10500 # VERIFY WHICH PORT TO USE
SERVER = '' # PARENT HOST
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
REQUEST_KEY= 'V*ESK~_DYH89hc?T'

child_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
child_socket.bind(ADDR)


# Node Data
PARENT_NODE_IP = '192.168.0.16'
PARENT_NODE = '2' # THIS NEEDS TO BE FILLED IN FOR EACH MONITOR
SECTION_NODE_ID = '1' # THIS NEEDS TO BE FILLED IN FOR EACH MONITOR
NODE_ID = f'{PARENT_NODE}-{SECTION_NODE_ID}'
  

def capture_image():
    while True:
        second = time.localtime().tm_sec
        if second % 15 == 0:
            cam = cv2.VideoCapture(0)
            retval, frame = cam.read()
            if retval != True:
                raise ValueError("Can't read frame")

            cv2.imwrite(f'{NODE_ID}.jpeg', frame)
            # cv2.imshow("img1", frame); cv2.waitKey() # Debug Line to view Image


def send_image_to_parent_node(parent_timestamp):

    with open(f"{NODE_ID}.jpeg", "rb") as image_file:
        message = image_file.read()
    
    img_byte_size = len(message)

    outgoing_msg_data = f'{img_byte_size} {NODE_ID} {parent_timestamp}'.encode(FORMAT)
    outgoing_msg_data += b' ' * (HEADER - len(outgoing_msg_data))

    child_socket.send(outgoing_msg_data)
    child_socket.send(message)



def process_request(conn,addr):
    if addr[0] == PARENT_NODE_IP:
        connected = True
        while connected:
            request_msg = conn.recv(HEADER).decode(FORMAT)
            if request_msg:
                request_key, request_time = request_msg.rstrip(' ').split(' ')
                if request_key==REQUEST_KEY:
                    # send_image_to_parent_node(request_time)
                    pass
                connected = False
                # conn.close()
                break
    else:
        pass # Should add logging to log foreign connection attempts







def child_start():
    image_capture_thread = threading.Thread(target=capture_image)
    image_capture_thread.start()

    child_socket.listen()
    while True:
        conn, addr = child_socket.accept()
        image_transfer_thread = threading.Thread(target=process_request,args=(conn,addr))
        image_transfer_thread.start()



if __name__ == '__main__':
    child_start()

