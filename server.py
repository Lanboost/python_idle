import math
from shared import *

from world_gen import World

const_player_aware_dist = 30


class Map(object):
    def __init__(self):
        self.chunks = {}
        self.world_gen = World()
        self.world_gen.initialize(0)

    def create(self, x, y):
        self.world_gen.generate_chunk(x,y)

        #print(self.world_gen.terrain[x][y])
        #print(self.world_gen.objects[x][y])

        if not x in self.chunks:
            self.chunks[x] = {}

        if not y in self.chunks[x]:
            self.chunks[x][y] = {}

        self.chunks[x][y] = [[[{"layers":[0]} if z == 0 else {"layers":[]} for y in range(const_chunk_size)] for x in range(const_chunk_size)] for z in range(const_chunk_depth)]

        for ix in range(const_chunk_size):
            for iy in range(const_chunk_size):
                self.chunks[x][y][0][ix][iy]["layers"][0] = self.world_gen.terrain[x][y][ix][iy]


    def get_chunk(self, x, y):
        d = [x,y]
        temp = self.chunks
        for c in d:
            if c in temp:
                temp = temp[c]
            else:
                return None
        return temp

def get_distance(obj1, obj2, ignore_z = False):
    if not ignore_z and obj1['position']['z'] != obj2['position']['z']:
        return 1000000
    
    dx = obj1['position']['x']-obj2['position']['x']
    dy = obj1['position']['y']-obj2['position']['y']
    return math.sqrt(dx**2, dy**2)

def wrap_pos(pos):
    return {'position':pos}

def get_new_aware_players(server, obj, old_pos, new_pos):
    aware = []
    for pid in server['players']:
        p = server['players'][pid]
        if p['id'] != obj['id']:
            old_dist = get_distance(wrap_pos(old_pos), p)
            new_dist = get_distance(wrap_pos(new_pos), p)
            if old_dist > const_player_aware_dist and new_dist <= const_player_aware_dist:
                aware.append(p)
    return aware

def get_aware_players(server, obj = None):
    aware = []
    for pid in server['players']:
        p = server['players'][pid]
        if obj == None or pid != obj['id']:
            dist = get_distance(obj, p)
            if dist <= const_player_aware_dist:
                aware.append(p)
    return aware

def get_in_range(objs, from_pos, distance=32, filter=None):
    aware = []
    for pid in objs:
        p = objs[pid]
        if filter == None or filter(pid):
            dist = get_distance(from_pos, p)
            if dist <= distance:
                aware.append(p)
    return aware


class Server_Rpc(object):
    def __init__(self, server):
        self.server = server

    def connect(self, endpoint):
        print("Endpoint is connecting:",endpoint)
        self.server['connections'].append(endpoint)
        endpoint.connected()

    def login(self, endpoint, username, password):
        self.server['api'].start_player(endpoint)

    def request_chunk(self, endpoint, x, y):
        return self.server["map"].get_chunk(x, y)


class Server_Api(object):

    def __init__(self, server):
        self.server = server
    
    def move(self, obj, pos):
        #should other players become aware?
        old_pos = obj['position']
        new_pos = pos
        new_aware = get_new_aware_players(self.server, obj, old_pos, new_pos)
        obj['position'] = pos

        for n_a in new_aware:
            n_a['rpc'].spawn(obj)
            n_a['rpc'].move(obj, old_pos, new_pos)

        if obj['player']:
            for n_a in new_aware:
                obj['rpc'].spawn(n_a)

        #update player position to aware players
        aware = get_aware_players(self.server, obj)
        for a in aware:
            a['rpc'].move(obj, old_pos, new_pos)

        #update self
        obj['rpc'].move(obj, old_pos, new_pos)

    def regen(self, obj):
        pass

    def start_player(self, endpoint):
        id = 0
        player = {'id':id, 'player':True}
        player = with_health(with_position(player))
        player['rpc'] = endpoint
        player['rpc'].spawn_self(id)

        aware = get_aware_players(self.server, player)
        for a in aware:
            a['rpc'].spawn(player)
            player['rpc'].spawn(a)

        ent_in_range = get_in_range(self.server['entities'], player['position'], const_player_aware_dist)
        for e in ent_in_range:
            player['rpc'].spawn_entity(e)


        self.server['players'][id] = player
        return id

    def stop_player(self):
        pass

    def spawn_entity(self, e):
        id = 0
        e['id'] = id
        self.server["entities"][id] = e
        aware = get_aware_players(self.server)
        for a in aware:
            a['rpc'].spawn_entity(e)

    def despawn_entity(self, e):
        id = e['id']
        del self.server["entities"][id]
        aware = get_aware_players(self.server)
        for a in aware:
            a['rpc'].despawn_entity(e)


class Server(object):
    def __init__(self):
        self.server = {}
        self.server["map"] = Map()
        self.server['connections'] = []
        self.server["players"] = {}

        self.server["entities"] = {}

        for x in range(10):
            for y in range(10):
                self.server["map"].create(x,y)

        

        self.server['api'] = Server_Api(self.server)
        self.server['rpc'] = Server_Rpc(self.server)

        ent = with_health(with_position({'is_creature':True}))
        self.server['api'].spawn_entity(ent)


    def endpoint(self):
        return self.server['rpc']

    def run(self):
        for pid, p in self.server["players"].items():
            #update movement


            p['rpc'].tick()
