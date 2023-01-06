import sys
import socket
import time
from PIL import Image
import pickle

pos = (0,0)
size = (50,50)


def recv_rect(sock):
    global pos
    global size
    while True:
        data = b''
        while '###' not in data:
            data += sock.recv_data(1)       
        data = data[:-3]
        data = data.split(b'|')
        if data[0] == 'req':
            

def image_to_pixel(picture : Image):
    px = picture.load()

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

    
    

def send_photo(sock, picture):
    while True:
        pass
        


def main():
    picture = Image.open('cool_image.jpg')
    data = image_to_pixel(picture)
    print(data)
    # connecting to the server



if __name__ == '__main__':
    st = 'abcdefghijkl'
    print(st[3:-3])
    
    ###main()

