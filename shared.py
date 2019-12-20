const_chunk_size = 32
const_chunk_depth = 10
const_tile_size = 16


const_tile_grass = 0
const_tile_water = 1
const_tile_shallow_water = 2
const_tile_snow = 3
const_tile_cave = 4
const_tile_mountain = 5
const_tile_sand = 6

const_object_tree = 1000
const_object_wall = 1001


tiles = [
    {
        "sprite":["basictiles_2.png", (3,1)],
    },
    {
        "blocking":True,
        "sprite":["basictiles_2.png", (5,1)],
        "resource":"food"
    },
    {
        "sprite":["basictiles_2.png", (5,2)],
    },
    {
        "sprite":["basictiles_2.png", (5,3)],
    },
    {
        "sprite":["basictiles_2.png", (7,3)],
    },
    {
        "sprite":["basictiles_2.png", (7,7)],
    },
    {
        "sprite":["basictiles_2.png", (2,1)],
    }
]

objects = {
    const_object_tree:{
        "blocking":True,
        "sprite":["basictiles_2.png", (4,9)],
        "resource":"food"
    },
    const_object_wall:{
        "blocking":True,
        "sprite":["basictiles_2.png", (0,0)],
        "resource":"food"
    },

}

def create_entity():
    return {}

def with_position(obj):
    obj["position"] = {'x':100, 'y':100, 'z':0}
    return obj

def with_health(obj):
    obj["health_regen"] = 1
    obj["max_health"] = 10
    obj["health"] = obj["max_health"]
    return obj

class AsyncRCP(object):
    def __init__(self, value):
        self.value = value

    def done(self):
        return True

    def data(self):
        return self.value

class DirectRPC(object):
    def __init__(self):
        pass

    def init(self, endpoint, selfendpoint):
        self.endpoint = endpoint
        self.selfendpoint = selfendpoint

    def __getattr__(self, name):
        print("X is calling:",name)
        def rcp(*args):
            print("X is calling with args:",args)
            return AsyncRCP(getattr(self.endpoint, name)(self.selfendpoint, *args))
        return rcp