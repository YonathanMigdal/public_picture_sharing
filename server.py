import pygame
import threading
import socket
import pickle
RUNNING = True
LENGTH, HEIGHT = 600,600
LENS = pygame.Rect(LENGTH/2-50,HEIGHT/2-50,100,100)
CLIENTS = {}
CLOCK, FPS = pygame.time.Clock(), 60
SRV_SOCKET = socket.socket()

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
        message = f"REQ|{pos[0]}|{pos[1]}|{size[0]}|{size[1]}###ID={self.id}"
        print(message)
        #self.sock.send(message.encode())
    def draw(self):
        for y,row in enumerate(self.matrix):
            for x,value in enumerate(row):
                # 1 is left-top, 2 is right-top, 3 is left-down, 4 is right-down
                #if even adds half-length to x
                # need to describe about y
                SCREEN.fill(value,(((LENGTH/2)*((self.id+1)%2)+x,(HEIGHT/2)*((self.id+1)/3)+y),(1,1)))
    def exit(self):
        global CLIENTS
        self.thread.join()
        del CLIENTS[self.id]

def get_lens():
    if LENS.left < LENGTH/2:
        if LENS.y<HEIGHT/2: # ID=1
            x_pos,y_pos = LENS.x,LENS.y
            length = min(LENS.width,LENGTH/2-x_pos)
            height = min(LENS.height,HEIGHT/2-y_pos)
            #CLIENTS[1].ask_rect((x_pos,y_pos),(length,height))
        if LENS.bottom>HEIGHT/2: # ID = 3
            x_pos,y_pos = LENS.x,max(LENS.y,HEIGHT/2)
            length = min(LENS.width,LENGTH/2-x_pos)
            height = LENS.bottom-y_pos
            #CLIENTS[3].ask_rect((x_pos,y_pos),(length,height))
    if LENS.right > LENGTH/2:
        if LENS.y<HEIGHT/2: # ID=2
            x_pos,y_pos = max(LENS.x,LENGTH/2),LENS.y
            length = min(LENS.width,LENGTH/2-x_pos)
            height = min(LENS.height,HEIGHT/2-y_pos)
            #CLIENTS[2].ask_rect((x_pos,y_pos),(length,height))
            print((x_pos,y_pos),(length,height))
        if LENS.bottom>HEIGHT/2: # ID = 4
            x_pos,y_pos = LENS.x,max(LENS.y,HEIGHT/2)
            length = min(LENS.width,LENGTH/2-x_pos)
            height = LENS.bottom-y_pos
            #CLIENTS[4].ask_rect((x_pos,y_pos),(length,height))
            #print((x_pos,y_pos),(length,height)) 


def accept_connections():
    global CLIENTS, SRV_SOCKET
    SRV_SOCKET = socket.socket()
    SRV_SOCKET.bind(("0.0.0.0",8168))
    SRV_SOCKET.listen(4)
    threads = []
    while RUNNING:
        if len(CLIENTS)<4:
            try:
                sock, address = SRV_SOCKET.accept()
                client = Client(len(CLIENTS)+1,sock)
                CLIENTS[client.id]+=1
            except Exception as e:
                print(f"ERROR!! {e}")
def graphics():
    global LENS, RUNNING
    movement = [0,0,2]
    while RUNNING:
        CLOCK.tick(FPS)
        SCREEN.fill((0,0,0))
        ## needs to go through all clients here
        LENS.x += movement[0]*movement[2]
        LENS.y += movement[1]*movement[2]
        pygame.draw.rect(SCREEN,(255,255,255),LENS,1)
        pygame.display.flip()
        get_lens()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
                SRV_SOCKET.close()
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
