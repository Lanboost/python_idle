from astar_python.astar import Astar
import time
import random

import action_handle

from shared import *
from server import Server
import draw

import pygame


view = {"x":0,"y":0,"z":0,"width":16*32*2,"height":16*32*2,"zoom":1, "px":0, "py":0}


class MapHandler(object):

    def __init__(self, game):
        self.chunks = {}
        self.loading = {}
        self.game = game

    def __add_loading(self, x, y):
        d = [x,y]
        temp = self.loading
        for c in d:
            if c in temp:
                temp = temp[c]
            else:
                temp[c] = {}
                temp = temp[c]

        if not temp:
            temp['request'] = self.game['rpc'].request_chunk(x,y)
            

    def get_chunk(self, x, y):
        d = [x,y]
        temp = self.chunks
        for c in d:
            if c in temp:
                temp = temp[c]
            else:
                self.__add_loading(x,y)
                return None
        return temp

    def set_chunk(self, x, y, data):
        if not x in self.chunks:
            self.chunks[x] = {}

        if not y in self.chunks[x]:
            self.chunks[x][y] = {}
        self.chunks[x][y] = data

    def update(self):
        delete = []
        for x in self.loading: 
            for y in self.loading[x]:
                if self.loading[x][y]['request'].done():
                    self.set_chunk(x, y, self.loading[x][y]['request'].data())
                    delete.append((x,y))

        for d in delete:
            del self.loading[d[0]][d[1]]
            if not self.loading[d[0]]:
                del self.loading[d[0]]
            self.game['force_tile_render'] =True

class Client_Rpc(object):
    def __init__(self, game):
        self.game = game

    def connected(self):
        self.game['connected'] = True
        self.game['connecting'] = False

    def spawn_self(self, id):
        self.game['online'] = True
        self.game['loggin'] = False
        self.game['self'] = id
        print("You logged in with id:",id)

    def despawn_self(self, obj):
        self.game['online'] = False

    def spawn(self, obj):
        pass

    def despawn(self, obj):
        pass

    def move(self, obj, from_pos, to_pos):
        pass

    def send_chunk(self, chunk):
        pass

    def regen(self, obj):
        pass
    
    def spawn_entity(self, entity):
        self.game['tick_data']['spawned_entites'].append(entity)

    def despawn_entity(self, entity):
        self.game['tick_data']['despawned_entites'].append(entity)

    def tick(self, tick_id):
        self.game['tick_data']['tick_id'] = tick_id
        self.game['ticks'].append(self.game['tick_data'])

        self.game['tick_data'] = {
            'tick_id':None,
            'spawned_entites':[],
            'despawned_entites':[]
        }

class Game_Api(object):
    def move_to(self, pos):
        pass

    def use_tile(self, tile):
        pass

    def use_item(self, item):
        pass

    def login(self, username, password):
        pass

    def stop(self):
        pass

    def message(self, msg):
        pass

game = {}
game["player"] = with_health(with_position(create_entity()))
game["view"] = view
game["map"] = MapHandler(game)
game["online"] = False
game['connected'] = False
game['connecting'] = False
game['loggin'] = False

game['rpc'] = DirectRPC()
game['endpoint'] = Client_Rpc(game)

game['force_tile_render'] = True

game['entities'] = {}
game['selected_entity'] = None
game['tick_data'] = {
    'tick_id':None,
    'spawned_entites':[],
    'despawned_entites':[]
}


renderer = draw.Renderer(game)


server = Server()

game['rpc'].init(server.endpoint(), game['endpoint'])

stop_client = False

game['moving'] = 0

def run():
    global stop_client

    if not game['online']:
        if not game['connected']:
            if not game['connecting']:
                game['connecting'] = True
                game['rpc'].connect()
        else:
            if not game['loggin']:
                game['loggin'] = True
                game['rpc'].login("","")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop_client = True  # Be interpreter friendly
        if event.type == pygame.KEYDOWN:
            pass
        if event.type == pygame.KEYUP:
            pass
    game['moving'] = 0
    pressed  = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
        game['moving'] += 1
    if pressed[pygame.K_d]:
        game['moving'] += 2
    if pressed[pygame.K_s]:
        game['moving'] += 4
    if pressed[pygame.K_a]:
        game['moving'] += 8

    if game['moving'] & 1:
        game["player"]['position']['y'] -= 1
    if game['moving'] & 2:
        game["player"]['position']['x'] += 1
    if game['moving'] & 4:
        game["player"]['position']['y'] += 1
    if game['moving'] & 8:
        game["player"]['position']['x'] -= 1

    

    game["view"]['x'] = int(game["player"]['position']['x']-game["view"]['width']/const_tile_size/2)
    game["view"]['y'] = int(game["player"]['position']['y']-game["view"]['height']/const_tile_size/2)
    time1 = time.time()
    renderer.render(tiles, game)
    time2 = time.time()
    #print(' function took {:.3f} ms'.format((time2-time1)*1000.0))

    game['map'].update()
    server.run()

if __name__ == "__main__":
    while not stop_client:
        run()
        time.sleep(0.01)
    pygame.quit()