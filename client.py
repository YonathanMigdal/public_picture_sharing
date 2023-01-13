import sys
import socket
import time
from PIL import Image
import pickle
import threading
import numpy as np

IP = "192.168.99.14"
PORT = 8168

pos = (0,0)
size = (0,0)


CHANGE = False



def recv_rect(sock,):
    global pos
    global size
    global CHANGE
    while True:
        data = b''
        while b'###' not in data:
            data += sock.recv(1)  
        #print(b"recv --------> " + data)     
        data = data[:-3]
        data = data.decode()
        data = data.split('|')
        if data[0].lower() == 'req':
            pos = (int(data[1]), int(data[2]))
            size = (int(data[3]), int(data[4]))
            CHANGE = True



def image_to_pixel(px):
    x = pos[0]
    y = pos[1]

    height = size[0]
    width = size[1]

    pix_picture = []

    for i in range(x, x+ height):
        row = []
        for j in range(y, y + width):
            pixle = px[i,j]
            row.append(pixle)
        pix_picture.append(row)
    return pix_picture

    

def send_photo(sock : socket.socket, px):
    global CHANGE
    while True:
        #print(pos, size)
        if CHANGE:
            CHANGE = False
            pix_picture = image_to_pixel(px)
            pickled_picture = pickle.dumps(pix_picture)
            data_to_send = b"img|" + pickled_picture + b"###"
            #print(data_to_send)
            sock.send(data_to_send)
        


def main():
    """picture = Image.open('cool_picture.jpg')
    data = image_to_pixel(picture)
    print(data)"""
    picture = Image.open("cool_picture.png")
    px = picture.load()
    sock = socket.socket()
    sock.connect((IP, PORT))
    t = threading.Thread(target=recv_rect, args=(sock,))
    t.start()
    send_photo(sock, px)

    # connecting to the server



if __name__ == '__main__':
    if (len(sys.argv) > 2):
        IP = sys.argv[1]
        PORT = sys.argv[2]
    main()
    st = 'abcdefghijkl'
    print(st[3:-3])
    

