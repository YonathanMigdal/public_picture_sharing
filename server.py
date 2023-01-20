import pygame
import threading
import socket
import pickle, json
import numpy as np
import random

RUNNING = True
LENGTH, HEIGHT = 600,600
BUFFER_SIZE = 65000
LENS = pygame.Rect(LENGTH/2-50,HEIGHT/2-50,70,70)
CLIENTS = {}
CLOCK, FPS = pygame.time.Clock(), 60
SRV_SOCKET = socket.socket()

pygame.init()
pygame.display.set_caption("PICTURE")
SCREEN = pygame.display.set_mode((LENGTH,HEIGHT))


class Client:
    def __init__(self,id:int,sock:socket.socket,udp_port:int) -> None:
        self.running = True
        self.sock = sock
        self.udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_sock.bind(("",udp_port))
        self.id = id
        self.matrix = []
        self.pos = (None,None)
        self.thread = threading.Thread(target=self.handle_client)
        self.thread.start()

    def handle_client(self):
        while self.running:
            bdata = b""
            dict = {}
            data = b""
            check = True
            size = 0
            data = self.udp_sock.recvfrom(BUFFER_SIZE)[0]
            
            """            
            print(f"length = {length}")
            bdata = self.udp_sock.recvfrom(BUFFER_SIZE)[0]
            while size<length:
                try:
                    bdata = self.udp_sock.recvfrom(BUFFER_SIZE)[0]
                    size+=1
                    dict[int(bdata[:5])] = bdata[5:]
                except Exception as e:
                    print(e)
                    check = False
            if check:
                sorted(dict)
                for key in dict.keys():
                    data+=dict[key]"""
            try:
                self.matrix = pickle.loads(data)

            except Exception as e:
                print(f"error in udp - {e}")
                
    def ask_rect(self,pos,size):
        self.pos = pos
        if self.id == 2:
            pos = pos[0]-LENGTH/2, pos[1]
        elif self.id == 3:
            pos = pos[0], pos[1]-HEIGHT/2
        elif self.id == 4:
            pos = pos[0]-LENGTH/2, pos[1]-HEIGHT/2
        message = f"REQ|{int(pos[0])}|{int(pos[1])}|{int(size[0])}|{int(size[1])}###"
        self.sock.send(message.encode())
        
    def draw(self):
        for x,row in enumerate(self.matrix):
            for y,value in enumerate(row):
                # 1 is left-top, 2 is right-top, 3 is left-down, 4 is right-down
                #if even adds half-length to x
                # need to describe about y
                try:
                    SCREEN.fill(value,((self.pos[0]+x,self.pos[1]+y),(1,1)))
                except:
                    pass
    def exit(self):
        global CLIENTS
        self.running = False
        self.sock.close()
        self.thread.join()
        del CLIENTS[self.id]


def get_lens():
    whyamidoingthis = []
    if LENS.left < LENGTH/2:
        if LENS.y<HEIGHT/2 and 1 in CLIENTS: # ID=1
            x_pos,y_pos = LENS.x,LENS.y
            length = min(LENS.width,LENGTH//2-x_pos)
            height = min(LENS.height,HEIGHT//2-y_pos)
            CLIENTS[1].ask_rect((x_pos,y_pos),(length,height))
            whyamidoingthis.append(1)
        if LENS.bottom>HEIGHT/2 and 3 in CLIENTS: # ID = 3
            x_pos,y_pos = LENS.x,max(LENS.y,HEIGHT//2)
            length = min(LENS.width,LENGTH//2-x_pos)
            height = LENS.bottom-y_pos
            CLIENTS[3].ask_rect((x_pos,y_pos),(length,height))
            whyamidoingthis.append(3)
    if LENS.right > LENGTH/2:
        if LENS.y<HEIGHT/2 and 2 in CLIENTS: # ID=2
            x_pos,y_pos = max(LENS.x,LENGTH/2),LENS.y
            length = min(LENS.width,LENS.right-LENGTH/2)
            height = min(LENS.height,HEIGHT/2-y_pos)
            CLIENTS[2].ask_rect((x_pos,y_pos),(length,height))
            whyamidoingthis.append(2)
        if LENS.bottom>HEIGHT//2 and 4 in CLIENTS: # ID = 4
            x_pos,y_pos = LENS.x,max(LENS.y,HEIGHT//2)
            length = min(LENS.width,LENGTH//2-x_pos)
            height = LENS.bottom-y_pos
            CLIENTS[4].ask_rect((x_pos,y_pos),(length,height))
            whyamidoingthis.append(4)

def accept_connections():
    global CLIENTS, SRV_SOCKET
    SRV_SOCKET = socket.socket()
    SRV_SOCKET.bind(("0.0.0.0",8168))
    SRV_SOCKET.listen(4)
    threads = []
    udp_port = random.randint(8167,65000)
    while RUNNING:
        if len(CLIENTS)<4:
            try:
                sock, address = SRV_SOCKET.accept()
                print(address)
                udp_port+=1
                sock.send(f"PRT|{udp_port}###".encode())
                client = Client(len(CLIENTS)+1,sock,udp_port)
                CLIENTS[client.id] = client
            except Exception as e:
                print(f"ERROR!! {e}")
                
def graphics():
    global LENS, RUNNING
    movement = [0,0,2]
    while RUNNING:
        CLOCK.tick(FPS)
        SCREEN.fill((0,0,0))
        for key in CLIENTS.keys():
            CLIENTS[key].draw()
        pygame.draw.line(SCREEN, (255,255,0),(0,HEIGHT/2),(LENGTH,HEIGHT/2))
        pygame.draw.line(SCREEN, (255,255,0),(LENGTH/2,0),(LENGTH/2,HEIGHT))
        ## needs to go through all clients here
        LENS.x += movement[0]*movement[2]
        LENS.y += movement[1]*movement[2]
        pygame.draw.rect(SCREEN,(255,255,255),LENS,1)
        pygame.display.flip()
        if movement[0]!=0 or movement[1]!=0:
            get_lens()
        for event in pygame.event.get():   
            if event.type == pygame.QUIT:
                RUNNING = False
                SRV_SOCKET.close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    movement[1] = 1
                elif event.key == pygame.K_UP:
                    movement[1] =- 1
                elif event.key == pygame.K_LEFT:
                    movement[0] =- 1
                elif event.key == pygame.K_RIGHT:
                    movement[0] = 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and movement[1]==1 or event.key == pygame.K_UP and movement[1]==-1:
                    movement[1] = 0
                elif event.key == pygame.K_LEFT and movement[0]==-1 or event.key == pygame.K_RIGHT and movement[0]==1:
                    movement[0] = 0 

def main():
    t = threading.Thread(target=accept_connections)
    t.start()
    graphics()

main()


s = "36FFD"
print(s[:2], s[2:])