from astar_python.astar import Astar
import time
import random

import action_handle


import draw

tiles = [
    {
        "sprite":["basictiles_2.png", (3,1)],
    },
    {
        "blocking":True,
        "sprite":["basictiles_2.png", (4,9)],
        "resource":"food"
    }
]

def with_inventory(obj):
    obj["inventory"] = {"size":1, "items":[]}
    return obj

def with_state(obj):
    obj["state"] = None
    return obj

def with_action(obj):
    obj["action"] = None
    obj["action_error"] = None
    obj["action_progress"] = None
    return obj

def with_energy(obj):
    obj["energy_regen"] = 1
    obj["max_energy"] = 10
    obj["energy"] = obj["max_energy"]
    return obj

def with_position(obj):
    obj["position"] = [0,0]
    return obj

def create_worker():
    return with_inventory(with_state(with_action(with_energy(
            with_position(
                {
                    "name":"Test"
                })))))

def create_house():
    return {

    }

def create_tile():
    return {"layers":[0], "blocked":False}

def create_map(size):
    
    return [[create_tile() for y in range(size)] for x in range(size)]

def create_town_center():
    return with_action(with_position({}))

def add_worker(game, worker):
    game["workers"].append(worker)

def add_town_center(game, tc):
    game["towncenters"].append(tc)

def add_house(game, house):
    game["houses"].append(house)

def add_item(obj, item):
    if len(obj["inventory"]["items"]) < obj["inventory"]["size"]:
        obj["inventory"]["items"].append(item)
    else:
        raise Exception("No space for item.")
    
def add_tile(game, x, y, id):
    if "blocking" in tiles[id]:
        game["aimap"][x][y] = None
    
    game["map"][x][y]["layers"].append(id)

def set_position(obj,x ,y):
    obj["position"] = [x, y]
    return obj

def update_aimap(game):
    for x in range(len(game["map"])):
        for y in range(len(game["map"][x])):
            game["aimap"][x][y] = None if game["map"][x][y]["blocked"] else 0



def create_game():
    map_size = 50

    game = {
        "food":0,
        "stone":0,
        "wood":0,
        "gold":0,
        "map":create_map(map_size),
        "aimap":[[0 for y in range(map_size)] for x in range(map_size)],
        "towncenters":[],
        "houses":[],
        "workers":[]
    }

    update_aimap(game)

    add_tile(game, 10, 10, 1)

    add_town_center(game, set_position(create_town_center(), 25, 25))
    add_worker(game, set_position(create_worker(), 25, 24))

    return game



###  AI

def find_path(game, obj, to_obj):
    pos = to_obj["position"]
    old = game["aimap"][pos[0]][pos[1]]

    game["aimap"][pos[0]][pos[1]] = 0
    
    path = find_path_positions(game, obj["position"], pos)
    if path and len(path) >= 1:
        if not old:
            path = path[1:-1]
        else:
            path = path[1:]

    game["aimap"][pos[0]][pos[1]] = old
    return path

def find_path_positions(game, from_pos, to_pos):
    astar = Astar(game["aimap"])
    return astar.run(from_pos, to_pos)

def walk_action(game, obj, to_obj):
    def inner_action(cancel = False): 
        path = find_path(game, obj, to_obj)
        while path and len(path) > 0:
            set_position(obj, path[0][0], path[0][1])
            path = path[1:]
            yield True
    return inner_action


def call_and_set_idle(obj, action):
    action()
    obj["action"] = None
    

def add_energy(obj, energy):
    obj["energy"] = max(obj["max_energy"],obj["energy"]+energy)
    
def add_food(game, resource):
    game["food"] += resource
    game

def inventory_full(obj):
    return len(obj["inventory"]["items"]) >= obj["inventory"]["size"]

def insert_resource(game, obj_from, obj_to):
    #check if obj_to is tc if so add to game resource
    for item in obj_from["inventory"]["items"]:
        if item == "food":
            game["food"] += 1
        else:
            raise Exception("Cannot put this item here!")
    obj_from["inventory"]["items"] = []

def combine_actions(action, action_cancel, next_action):
    def inner_action(cancel = False): 
        try:
            for i in action(cancel):
                yield i
            if next_action:
                for v in next_action(cancel):
                    yield v
        except Exception as e:
            if cancel:
                action_cancel()
            raise e
    return inner_action

class InstantBreakIter:
    def __init__(self):
        pass
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

def time_action(caster, time, action = None):
    def inner_action(cancel = False): 
        caster["action_progress"] = 0
        for i in range(time):
            print("Cast time",time-i,"of",time)
            caster["action_progress"] = (i+1)/time
            yield True
        caster["action_progress"] = None
        
    return combine_actions(inner_action, None, action)

def energy_requirement_action(worker, energy, action = None):
    def inner_action(cancel = False):
        if worker["energy"] >= energy:
            worker["energy"] -= energy
            return InstantBreakIter()
        else:
            raise Exception("Not enough energy.")

    def inner_cancel():
        add_energy(worker, energy)

    return combine_actions(inner_action, inner_cancel, action)

def food_requirement_action(game, food_req, action=None):
    def inner_action(cancel = False):
        if game["food"] >= food_req:
            game["food"] -= food_req
            return InstantBreakIter()
        else:
            raise Exception("Not enough energy.")

    def inner_cancel():
        add_food(game, food_req)

    return combine_actions(inner_action, inner_cancel, action)

def create_worker_action(game, tc, action = None):
    food_req = 10
    cast_time = 10

    def inner_action(cancel = False):
        add_worker(game, set_position(create_worker(), tc["position"][0], tc["position"][1]-1))
        return InstantBreakIter()

    return food_requirement_action(game, food_req, time_action(tc, cast_time, inner_action))
    

def collect_resource_action(game, worker, resource):
    energy_req = 4
    cast_time = 10

    def inner_action(cancel = False):
        tile_style = tiles[game["map"][resource[0]][resource[1]]["layers"][resource[2]]]
        if resource[3] == tile_style["resource"]:
            print("Collected resource")
            add_item(worker, "food")
            return InstantBreakIter()

        raise Exception("No resource at that location.")

    return energy_requirement_action(worker, energy_req, time_action(worker, cast_time, inner_action))

def find_closest_resource(game, resource_type):
    for x in range(len(game["map"])):
        for y in range(len(game["map"][x])):
            tile = game["map"][x][y]

            for i in range(len(tile["layers"])):

                tile_style = tiles[tile["layers"][i]]
                if "resource" in tile_style and tile_style["resource"] == resource_type:
                    return (x, y, i)
    return None

def ai(game):
    for w in game["workers"]:
        if not w["action"]:
            
            if not w["state"]:
                food = find_closest_resource(game, "food")
                if food:
                    w["state"] = {"type":"walk", "data":food}
            else:
                if w["state"]["type"] == "walk":
                    w["action"] = walk_action(game, w, set_position(with_position({}), w["state"]["data"][0], w["state"]["data"][1]))()
                    
                    w["state"] = {"type":"gather", "data":(w["state"]["data"][0],w["state"]["data"][1], w["state"]["data"][2], "food")}
                elif w["state"]["type"] == "gather":
                    if inventory_full(w):
                        tc = game["towncenters"][0]

                        w["action"] = walk_action(game, w, tc)()

                        w["state"] = {"type":"return_resource", "data":tc}
                    else:
                        print("Start gather")
                        w["action"] = collect_resource_action(game, w, w["state"]["data"])()
                elif w["state"]["type"] == "return_resource":
                    insert_resource(game, w, w["state"]["data"])
                    w["state"] = None

game = create_game()

renderer = draw.Renderer(game)


def run():
    for w in game["workers"]:
        if w["action"]:
            try:
                action_handle.run_action_once(w)
                #w["action"].next()
            except Exception as e:
                print(e)
                #if not isinstance(e, StopIteration):
                    #raise e
                w["action"] = None
                w["action_error"] = e

        add_energy(w, w["energy_regen"])

    for w in game["towncenters"]:
        if w["action"]:
            try:
                action_handle.run_action_once(w)
                #w["action"].next()
            except Exception as e:
                if not isinstance(e, StopIteration):
                    raise e
                w["action"] = None

    ai(game)

    renderer.render(tiles, game)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(0.1)