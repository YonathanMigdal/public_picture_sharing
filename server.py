import pygame
import threading
import socket
import pickle
RUNNING = True
LENGTH, HEIGHT = 600,600
LENS = pygame.Rect(LENGTH/2-50,HEIGHT/2-50,100,100)
CLIENTS = {}
CLOCK, FPS = pygame.time.Clock(), 60

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

def get_lens():
    pass


def accept_connections():
    global CLIENTS
    srv_socket = socket.socket()
    srv_socket.bind(("0.0.0.0",8168))
    srv_socket.listen(4)
    threads = []
    while RUNNING:
        if len(CLIENTS)<4:
            sock, address = srv_socket.accept()
            client = Client(len(CLIENTS)+1,sock)
            CLIENTS[client.id]+=1
def graphics():
    global LENS
    movement = [0,0,2]
    while RUNNING:
        CLOCK.tick(FPS)
        SCREEN.fill((0,0,0))
        ## needs to go through all clients here
        LENS.x += movement[0]*movement[2]
        LENS.y += movement[1]*movement[2]
        pygame.draw.rect(SCREEN,(255,255,255),LENS,1)
        pygame.display.flip()
        print(movement)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    movement[1] =+ 1
                elif event.key == pygame.K_UP:
                    movement[1] =- 1
                elif event.key == pygame.K_LEFT:
                    movement[0] =- 1
                elif event.key == pygame.K_RIGHT:
                    movement[0] =+ 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    movement[1] = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    movement[0] = 0 

def main():
    t = threading.Thread(target=accept_connections)
    t.start()
    graphics()
main()
