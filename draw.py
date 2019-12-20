import sys, pygame
import math
import pprint
from shared import *


class Renderer(object):
    def __init__(self, game):
        ##render
        self.images = {}
        pygame.init()
        self.black = 0, 0, 0


        self.tile_surface = pygame.Surface((game["view"]['width'],game["view"]['height']))
        self.tile_surface_pos = [-100,-100]


        self.screen = pygame.display.set_mode((game["view"]['width'],game["view"]['height']))
    
    def get_image(self, path):
        if not path in self.images:
            self.images[path] = pygame.image.load(path).convert()
        return self.images[path]

    def tile_pos(self, game, x, y, z):
        dx = x-game["view"]['x']
        dy = y-game["view"]['y']
        dz = z-game["view"]['z']

        tx = dx*const_tile_size-game["view"]['px']-dz*const_tile_size
        ty = dy*const_tile_size-game["view"]['py']-dz*const_tile_size

        return pygame.Rect(tx*game["view"]['zoom'], ty*game["view"]['zoom'], const_tile_size, const_tile_size)

    def render_tile(self, game, x, y):
        cx = int(x/const_chunk_size)
        cy = int(y/const_chunk_size)
        dx = int(x%const_chunk_size)
        dy = int(y%const_chunk_size)
        chunk = game['map'].get_chunk(cx, cy)
        toblits = []
        torects = []
        if chunk:
            for z in range(const_chunk_depth):
                tile = chunk[z][dx][dy]
                exact_pos = self.tile_pos(game, x, y, z)
                for l in tile["layers"]:
                    tile_style = tiles[l]
                    if "color" in tile_style:
                        torects += [(tile_style["color"], exact_pos)]
                    else:
                        img = self.get_image(tile_style["sprite"][0])
                        toblits += [(  img, 
                                exact_pos, 
                                pygame.Rect(const_tile_size*tile_style["sprite"][1][0],
                                const_tile_size*tile_style["sprite"][1][1],
                                const_tile_size,const_tile_size)
                            )]
        else:
            exact_pos = self.tile_pos(game, x, y, 0)
            torects += [((0,0,0), exact_pos)]
        return (toblits,torects)

    def render(self, tiles, game):
        ###render
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        #self.screen.fill(self.black)


        if not game['online']:
            pass
        else:

            tw = int(math.ceil(game["view"]['width']/const_tile_size))
            th = int(math.ceil(game["view"]['height']/const_tile_size))
            wcx = int(math.ceil(tw/const_chunk_size/game["view"]['zoom']))
            wcy = int(math.ceil(th/const_chunk_size/game["view"]['zoom']))


            if game['force_tile_render']:
                self.tile_surface_pos[0] = game["view"]['x']+tw
                self.tile_surface_pos[1] = game["view"]['y']+th
                game['force_tile_render'] = False

            offset_x = self.tile_surface_pos[0]-game["view"]['x']
            offset_y = self.tile_surface_pos[1]-game["view"]['y']

            if offset_x != 0 or offset_y != 0:
                toblit = []
                torects = []

                self.tile_surface.blit(self.tile_surface, (offset_x*16, offset_y*16))

                if game["view"]['x'] > self.tile_surface_pos[0]:
                    for x in range(min(self.tile_surface_pos[0]+tw,game["view"]['x']+tw), max(self.tile_surface_pos[0]+tw,game["view"]['x']+tw)):
                        for y in range(game["view"]['y'], game["view"]['y']+th+1):
                            blits, rects = self.render_tile(game, x, y)
                            toblit += blits
                            torects += rects
                else:
                    for x in range(min(self.tile_surface_pos[0],game["view"]['x']), max(self.tile_surface_pos[0],game["view"]['x'])):
                        for y in range(game["view"]['y'], game["view"]['y']+th+1):
                            blits, rects = self.render_tile(game, x, y)
                            toblit += blits
                            torects += rects

                if game["view"]['y'] > self.tile_surface_pos[1]:
                    for y in range(min(self.tile_surface_pos[1]+th,game["view"]['y']+th), max(self.tile_surface_pos[1]+th,game["view"]['y']+th)):
                        for x in range(game["view"]['x'], game["view"]['x']+tw+1):
                            blits, rects = self.render_tile(game, x, y)
                            toblit += blits
                            torects += rects
                else:
                    for y in range(min(self.tile_surface_pos[1],game["view"]['y']), max(self.tile_surface_pos[1],game["view"]['y'])):
                        for x in range(game["view"]['x'], game["view"]['x']+tw+1):
                            blits, rects = self.render_tile(game, x, y)
                            toblit += blits
                            torects += rects

                for r in torects:
                    pygame.draw.rect(self.tile_surface, r[0], r[1])
                
                self.tile_surface.blits(toblit)

                self.tile_surface_pos[0] = game["view"]['x']
                self.tile_surface_pos[1] = game["view"]['y']




            self.screen.blit(self.tile_surface, (0,0))
            p_pos = game["player"]['position']
            exact_pos = self.tile_pos(game, p_pos['x'], p_pos['y'], p_pos['z'])

            pygame.draw.rect(self.screen, (255,0,0), exact_pos)

            for ekey in game['entities']:
                e = game['entities'][ekey]
                if 'is_creature' in e:
                    p_pos = e['position']
                    exact_pos = self.tile_pos(game, p_pos['x'], p_pos['y'], p_pos['z'])

                    pygame.draw.rect(self.screen, (255,255,0), exact_pos)


        pygame.display.flip()