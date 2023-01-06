import pygame
import threading
import socket
import pickle
RUNNING = True
LENGTH, HEIGHT = 600,600
LENS = 100
ID = [1,2,3,4]
CLIENTS = []
POS = LENGTH/2-LENS/2,HEIGHT/2-LENS/2,
pygame.init()
pygame.display.set_caption("PICTURE")
SCREEN = pygame.display.set_mode((LENGTH,HEIGHT))

class Client:
    def __init__(self,id:int,sock:socket.socket) -> None:
        self.running = True
        self.sock = sock
        self.id = id
        self.matrix = []
        self.pos = (None,None)
        self.thread = threading.Thread(target=self.handle_client)
        self.thread.start()

    def handle_client(self):
        while self.running:
            bdata = b""
            while b"###" not in bdata:
                bdata += self.sock.recv(1)
            data = bdata[-3].split(b"|")
            if data[0] == "IMG":
                self.matrix = pickle.loads(data[1])

    def ask_rect(self,pos,size):
        message = f"REQ|{pos[0]}|{pos[1]}|{size[0]}|{size[1]}###"
        self.sock.send(message.encode())

    def draw(self):
        for y,row in enumerate(self.matrix):
            for x,value in enumerate(row):
                SCREEN.fill(value,((x,y),(1,1)))
    def exit(self):
        self.thread.join()


def accept_connections():
    global CLIENTS
    srv_socket = socket.socket()
    srv_socket.bind(("0.0.0.0",8168))
    srv_socket.listen(4)
    threads = []
    while RUNNING:
        if len(ID)>0:
            sock, address = srv_socket.accept()
            client = Client(ID.pop(),sock)
            CLIENTS.append(client)


def graphics():
    while RUNNING:
        SCREEN.fill((0,0,0))
        for client in CLIENTS:
            client.draw()
        for event in pygame.event.get():
            pass
def draw_lens():
    pass

def main():
    t = threading.Thread(target=accept_connections)
    t.start()
    graphics()
main()
