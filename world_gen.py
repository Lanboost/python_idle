from perlin import *

from shared import *

import random
import zlib

RETRY_MAX = 14
CELL_SIZE = 1




class NoiseGen(object):
    def __init__(self, seed, persistance, octave):
        random.seed(0)
        self.noisegen = SimplexNoise()
        self.persistance = persistance
        self.octave = octave
        self.scale = 0.01

    def get(self, x, y):
        return self.sumOcatave(1, x, y, self.persistance, self.scale, -1, 1)

    def sumOcatave(self, num_iterations, x, y, persistence, scale, low, high):
        maxAmp = 0
        amp = 1
        freq = scale
        noise = 0

        #add successively smaller, higher-frequency terms
        for i in range(num_iterations):
            noise += self.noisegen.noise2(x * freq, y * freq) * amp
            maxAmp += amp
            amp *= persistence
            freq *= 2

        #take the average value of the iterations
        noise /= maxAmp

        #normalize the result
        noise = noise * (high - low) / 2 + (high + low) / 2

        return noise

class World(object):
    def initialize(self, seed, chunk_size=32):
        print(f"generating world for seed {seed}, .")
        self.seed = seed
        self.width = chunk_size
        self.height = chunk_size
        self.terrain = {}
        self.objects = {}
        
        self.chunk_size = chunk_size

        self.v_persistence = 1.34 + 0.25
        self.update_octave(1)
        self.update_generator()

    def persistence(self, v_persistence):
        self.v_persistence = v_persistence
        print(f"new persistence value {self.v_persistence}")
        self.update_generator()

    def update_octave(self,octave):
        self.octave = max(octave, 1)
        self.update_generator()

    def update_generator(self):
        print(f"new generator: seed: {self.seed}, persistence: {self.v_persistence}, octave: {self.octave}")
        self.multiplier_noise_generator = NoiseGen(self.seed, self.v_persistence, self.octave)
        self.noise_generator = NoiseGen(self.seed, self.v_persistence, self.octave)

    def has_chunk(self, x,y):
        return self.terrain and x in self.terrain and y in self.terrain[x]


    def get_as_chunk(self, x, y, param):
        chunk_x = int(x/self.chunk_size)
        chunk_y = int(y/self.chunk_size)
        return param[chunk_x][chunk_y]

    def get_as_local(self, x, y, param):
        local_x = x%self.chunk_size
        local_y = y%self.chunk_size
        return param[local_x][local_y]

    def get_as_world(self, x, y, param):
        return self.get_as_local(x, y, self.get_as_chunk(x, y, param))

    def tile_for_world_coord(self, x,y):
        chunk_x = x / CELL_SIZE / self.chunk_size
        chunk_y = y / CELL_SIZE / self.chunk_size
        chunk_size_in_pixels = CELL_SIZE * self.chunk_size
        chunk_hash = self.terrain[chunk_x][chunk_y]
        chunk_hash[(x-chunk_x*chunk_size_in_pixels)/CELL_SIZE][(y-chunk_y*chunk_size_in_pixels)/CELL_SIZE]

    def chunk_for_world_coord(self,x,y):
        chunk_x = x / CELL_SIZE / self.chunk_size
        chunk_y = y / CELL_SIZE / self.chunk_size
        return [chunk_x, chunk_y]

    def place_object(self, x, y, obj):        
        self.get_as_world(x, y, self.objects).append(obj)

    def objects_for_world_coord(self,x,y):
        chunk_x = x / CELL_SIZE / self.chunk_size
        chunk_y = y / CELL_SIZE / self.chunk_size
        chunk_size_in_pixels = CELL_SIZE * self.chunk_size
        chunk_objs = self.objects[chunk_x][chunk_y]
        chunk_objs[(x-chunk_x*chunk_size_in_pixels)/CELL_SIZE][(y-chunk_y*chunk_size_in_pixels)/CELL_SIZE]

    def generate_chunk(self, chunk_x=0,chunk_y=0):
        local_seed = chunk_x*1000+chunk_y
        random.seed(local_seed)

        if not chunk_x in self.terrain:
            self.terrain[chunk_x] = {}
            self.objects[chunk_x] = {}
            
        if not chunk_y in self.terrain[chunk_x]:
            self.terrain[chunk_x][chunk_y] = [[0 for i in range(self.chunk_size)]for j in range(self.chunk_size)]
            self.objects[chunk_x][chunk_y] = [[[] for i in range(self.chunk_size)]for j in range(self.chunk_size)]
            
        chunk = self.terrain[chunk_x][chunk_y]

        interval = 1 #chunk_size/600.0
        #x = int(chunk_x*self.chunk_size*interval)
        #y = int(chunk_y*self.chunk_size*interval)
        print(f"generating #{chunk_x},#{chunk_y}")
        #noise = self.noise_generator.get(x,y)
        #multiplier_noise = self.multiplier_noise_generator.get(x,y)#0.08)

        # puts "[#{chunk_x},#{chunk_y}] => noise row size: #{noise.size}x#{noise.first.size} vs chunksize: #{chunk_size}"
        deep_sea_level = -0.7
        sea_level = -0.3
        grass_height = -0.1
        mountain_height = 1.5
        snow_height = 2.2

        for x in range(self.width):
            for y in range(self.height):
                #multiplier = max( (multiplier_noise + 1), 0) / 2.5
                sample = self.noise_generator.get(chunk_x*32+x,chunk_y*32+y)
                if sample > snow_height:
                    tiletype = const_tile_snow
                elif sample > mountain_height:
                    tiletype = const_tile_mountain
                elif sample > grass_height:
                    tiletype = const_tile_grass
                    if random.randint(0,99) < 1:
                        
                        self.place_object(chunk_x+x,chunk_y+y, const_object_tree)

                elif sample > sea_level:
                    tiletype = const_tile_sand
                elif sample > deep_sea_level:
                    tiletype = const_tile_shallow_water
                else:
                    tiletype = const_tile_water
                chunk[x][y] = tiletype

        #if self.generate_town(chunk, chunk_x, chunk_y):
        #    pass
        #else:
        #    if(random.randint(0, 100) < 20):
        #        self.generate_cave(chunk, chunk_x, chunk_y)


    def generate_cave(self, chunk_terrain, chunk_x, chunk_y):
        chunk_size = chunk_terrain.size
        entrance_x = random.randint(0, chunk_size)
        entrance_y = random.randint(0, chunk_size)

        print("generating cave at [#{entrance_x},#{entrance_y}] [#{chunk_x}, #{chunk_y}]!")
        chunk_objects[entrance_x][entrance_y].append(const_tile_cave)

    def largest_flat_space(self,chunk, cx,cy, times):
        if not self.flat(chunk, cx, cy):
            return 0
            
        for r in range(times):
            for x in range(cx-r, cx+r+1):
                for y in range(cy-r, cy+r+1):
                    if not self.flat(chunk, x, y):
                        return r-1 
                        #iterate other way
        return times

    def flat(self,chunk, x, y):
        return chunk[x][y] == const_tile_sand or chunk[x][y] == const_tile_grass

    def generate_town(self, chunk, chunk_x, chunk_y):
        cx = int(self.chunk_size / 2)
        cy = int(self.chunk_size / 2)

        largest_safe_radius = self.largest_flat_space(chunk, cx, cy, int(self.chunk_size / 2))
        # puts "generating town! safe radius: #{largest_safe_radius}"

        if largest_safe_radius > 9:
            radius = random.randint(9, largest_safe_radius)
            print(f"generating town with radius of #{radius} at [#{chunk_x}, #{chunk_y}]!")
            
            # pick gates
            # hardcoded for now, width of 1
            gates = [[cx+4,cy-radius,1], [cx-radius, cy,1]] 

            # build walls
            for x in range(cx-radius, cx+radius+1):
                for y in [cy-radius, cy+radius]:
                    if gates[0] != x or gates[1] != y:
                        self.place_object(x, y, const_object_wall)

            for y in range(cy-radius, cy+radius+1):
                for x in [cx-radius, cx+radius]:
                    if gates[0] != x or gates[1] != y:
                        self.place_object(x, y, const_object_wall)
            
            plaza_loc = self.place_plaza(cx, cy, radius)

            road_nodes = gates
            road_nodes.append(plaza_loc)
            road_nodes.append(self.place_town_hall(cx, cy, radius))
            for hut in self.place_huts(cx, cy, radius):
                road_nodes.append(hut)

            # place barracks

            # place roads
            #map = CityPlannerMap.new terrain, objects
            #pather = Polaris.new map

            #ordered_nodes = road_nodes.compact.sort_by{|n|n[3]}.reverse
            #ordered_nodes.each_cons(2) do |a,b|
            #  path = pather.guide(a, b)
            #  pave_path(objects, path) if path

            return True
        else:
            return False

    def pave_path(self,path):
        for path_el in path:
          cell = path_el.location
          self.place_object(cell.x, cell.y, ROAD)

    def place_town_hall(self,cx, cy, radius):
        for i in range(RETRY_MAX):
            hut_w = random.randint(3, 6)
            hut_h = random.randint(3, 6)
            th_cx = cx+random.randint(-6, 6)
            th_cy = cy+random.randint(-6, 6)
            if self.place_building( cx, cy, radius, hut_w, hut_h):
                return True
        return False

    def place_plaza(self,cx, cy, radius):
        plaza_cx = cx + random.randint(-5,5)
        plaza_cy = cy + random.randint(-5,5)
        plaza_w = random.randint(radius/4, radius/2)
        plaza_h = random.randint(radius/4, radius/2)
        plaza_x = plaza_cx-plaza_w/2
        plaza_y = plaza_cy-plaza_h/2
        for ix in range(plaza_x, plaza_x+plaza_w):
            for iy in range(plaza_y, plaza_y+plaza_h):
                self.place_object(ix, iy, ROAD)

        return [plaza_cx, plaza_cy]

    def place_huts(self, cx, cy, radius):
        num_huts = random.randint(1, radius/3)
        huts = []
        retry_count = 0
        while len(huts) < num_huts and retry_count < RETRY_MAX:
          retry_count += 1
          hut_w = random.randint(1, 2)
          hut_h = random.randint(1, 2)
          hut = self.place_building(cx, cy, radius, hut_w, hut_h)
          if hut:
            huts.append(hut)
        return huts

    def place_building(self, cx, cy, radius, hut_w, hut_h):
        hut_cx = random.randint(cx-radius+2+hut_w, cx+radius-2-hut_w)
        hut_cy = random.randint(cy-radius+2+hut_h, cy+radius-2-hut_h)
        hut_x = hut_cx-hut_w
        hut_y = hut_cy-hut_h
        hut_fits = self.room_for_building(hut_cx-hut_w, hut_cy-hut_h, hut_w*2+1, hut_h*2+1)

        all_doors = [[hut_cx,hut_cy-hut_h],[hut_cx,hut_cy+hut_h],[hut_cx-hut_w,hut_cy],[hut_cx+hut_w,hut_cy]] 
        return None
        '''
        doors = all_doors.select{|d|random.randint(10) < 2}
        doors = [all_doors[rand(all_doors.size)]] if doors.empty?

        if hut_fits
          (hut_cx-hut_w, hut_cx+hut_w).each do |x|
            [hut_cy-hut_h,hut_cy+hut_h].each do |y|
              objects[x][y] ||= []
              if doors.any?{|g|g[0]==x && g[1]==y}
                objects[x][y] << Road.new 
              else
                objects[x][y] << Wall.new 
              end
            end
          end
          (hut_cy-hut_h+1, hut_cy+hut_h-1).each do |y|
            [hut_cx-hut_w,hut_cx+hut_w].each do |x|
              objects[x][y] ||= []
              if doors.any?{|g|g[0]==x && g[1]==y}
                objects[x][y] << Road.new 
              else
                objects[x][y] << Wall.new 
              end
            end
          end
        end
        hut_fits ? doors[0] + [hut_w*hut_h] : nil
        '''

    

    def can_place_wall(self, x, y):
        return len(self.get_as_world(x,y,self.objects)) == 0

    def room_for_building(self,x, y, w, h):
        for ix in range(x-1, x+2):
            for iy in range(y-1, y+2):
                if self.can_place_wall(ix, iy):
                    return False
        return True





