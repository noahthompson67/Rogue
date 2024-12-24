import random
from environment_objects import Rock, Fire, Hole, MushroomPatch
from items import TreasureChest
from enemies import MobGenerator, Bat, Shooter
from boss import Golem
from pygame import Rect
from biome_map_generators.biome import Biome
import config_files.screen_size as ss

class CaveBiome(Biome):
    def __init__(self, player):
        super().__init__(player, 'cave')

    def generate_random_map(self, map):
        rock_wall_count = random.randrange(4,10)
        for _ in range(rock_wall_count):
            first_rock = Rock(self.player, map)
            first_rock_pos = first_rock.rect.center
            rock_spawn_count = random.randrange(10, 20)
            vertical_wall = random.choice([True, False])
            for i in range(rock_spawn_count):
                rock = Rock(self.player, map)
                if vertical_wall:
                    rock.rect.center = (first_rock_pos[0], first_rock_pos[1] + i * 30)

                else:
                    rock.rect.center = (first_rock_pos[0] + i * 30, first_rock_pos[1])
                rock.health = random.randrange(1, 5)
                rock.block_rect.center = rock.rect.center
                rock.drops = []
                map.add_entity(rock)
        map.add_entity(MobGenerator(self.player, map, Bat, 10000))

    def generate_map(self, map):
        n = map.north_map is not None
        s = map.south_map is not None
        e = map.east_map is not None
        w = map.west_map is not None
        map.entities = []
        for _ in range(random.randrange(1,5)):
            mushroom = MushroomPatch(self.player, map)
            map.entities.append(mushroom)
        self.build_hallways(n, s, e, w, map)
        map.add_entity(MobGenerator(self.player, map, Bat, 15000))
        if n and s and not e and not w:
            left_fire = Fire(self.player, map)
            right_fire = Fire(self.player, map)
            left_fire.rect.center = (ss.SCREEN_WIDTH/ 4, ss.SCREEN_HEIGHT / 2)
            right_fire.rect.center = (ss.SCREEN_WIDTH * 0.75, ss.SCREEN_HEIGHT / 2)
            left_hole = Hole(self.player, map)
            right_hole = Hole(self.player, map)
            left_hole.rect = Rect(0, ss.HUD_HEIGHT, ss.SCREEN_WIDTH*.2, ss.SCREEN_HEIGHT)
            left_hole.block_rect = left_hole.rect
            right_hole.rect = Rect(ss.SCREEN_WIDTH-ss.SCREEN_WIDTH*.2, 0, ss.SCREEN_WIDTH*.2, ss.SCREEN_HEIGHT)
            right_hole.block_rect = right_hole.rect
            map.add_entity(left_hole)
            map.add_entity(right_hole)
            map.add_entity(left_fire)
            map.add_entity(right_fire)
        elif not n and not s and e and w:
            left_fire = Fire(self.player, map)
            right_fire = Fire(self.player, map)
            left_fire.rect.center = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 4 + ss.HUD_HEIGHT)
            right_fire.rect.center = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT * 0.75)
            left_hole = Hole(self.player, map)
            right_hole = Hole(self.player, map)
            left_hole.rect = Rect(0, ss.HUD_HEIGHT, ss.SCREEN_WIDTH, ss.SCREEN_HEIGHT*.2)
            left_hole.block_rect = left_hole.rect
            right_hole.rect = Rect(0, ss.SCREEN_HEIGHT-ss.SCREEN_HEIGHT*.2, ss.SCREEN_WIDTH, ss.SCREEN_HEIGHT*.2)
            right_hole.block_rect = right_hole.rect
            map.add_entity(left_hole)
            map.add_entity(right_hole)
            map.add_entity(left_fire)
            map.add_entity(right_fire)

        for i in range(1,4):
            shooter = Shooter(self.player, map)
            map.add_entity(shooter)



    def generate_boss_map(self, map):
        map.entities = []
        golem = Golem(self.player, map)
        left_fire = Fire(self.player, map)
        right_fire = Fire(self.player, map)
        left_fire.rect.center = ss.SCREEN_WIDTH / 4, ss.SCREEN_HEIGHT / 2
        right_fire.rect.center = ss.SCREEN_WIDTH * 0.75, ss.SCREEN_HEIGHT / 2
        map.add_entity(MobGenerator(self.player, map, Bat, 1000))
        map.add_entity(golem)
        map.add_entity(left_fire)
        map.add_entity(right_fire)

    def build_hallways(self, n, s, e, w, map):
        vert_count = 10
        horiz_count = 15
        if n:
            self.build_wall(ss.SCREEN_WIDTH * .45, ss.HUD_HEIGHT, 10, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH*.55, ss.HUD_HEIGHT, 10, map, 0, 1)
        if s:
            self.build_wall(ss.SCREEN_WIDTH * .45, ss.SCREEN_HEIGHT-vert_count*30, 10, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH * .55, ss.SCREEN_HEIGHT-vert_count*30, 10, map, 0, 1)
        if e:
            self.build_wall(ss.SCREEN_WIDTH - horiz_count * 30, ss.SCREEN_HEIGHT * .56+ss.HUD_HEIGHT/2, 15, map, 1, 0)
            self.build_wall(ss.SCREEN_WIDTH - horiz_count * 30, ss.SCREEN_HEIGHT * .44+ss.HUD_HEIGHT/2, 15, map, 1, 0)
        if w:
            self.build_wall(30, ss.SCREEN_HEIGHT * .56+ss.HUD_HEIGHT/2, horiz_count, map, 1, 0)
            self.build_wall(30, ss.SCREEN_HEIGHT * .44+ss.HUD_HEIGHT/2, horiz_count, map, 1, 0)

    def build_wall(self, x, y, count, map, horizontal=0, vertical=0):
        for i in range(count):
            one = Rock(self.player, map, 0, 0)
            one.rect.center = (x + (i * 30 * horizontal), y + (i * 30 * vertical))
            one.block_rect.center = one.rect.center
            map.add_entity(one)

    def generate_boss_entrance(self, map, dir):
        if dir == 'n':
            self.build_wall(ss.SCREEN_WIDTH*.45, ss.SCREEN_HEIGHT*0.1+ss.HUD_HEIGHT, 7, map, 1, 0)
            self.build_wall(ss.SCREEN_WIDTH*.45, ss.SCREEN_HEIGHT*0.05+ss.HUD_HEIGHT-30, 3, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH * .55, ss.SCREEN_HEIGHT * 0.05 + ss.HUD_HEIGHT - 30, 3, map, 0, 1)
        elif dir == 's':
            self.build_wall(ss.SCREEN_WIDTH * .45, ss.SCREEN_HEIGHT * 0.75 + ss.HUD_HEIGHT, 7, map, 1, 0)
            self.build_wall(ss.SCREEN_WIDTH * .45, ss.SCREEN_HEIGHT * 0.8 + ss.HUD_HEIGHT - 30, 3, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH * .55, ss.SCREEN_HEIGHT * 0.8 + ss.HUD_HEIGHT - 30, 3, map, 0, 1)
        elif dir == 'e':
            self.build_wall(ss.SCREEN_WIDTH*0.932, ss.SCREEN_HEIGHT*0.34+ss.HUD_HEIGHT, 7, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH*0.95, ss.SCREEN_HEIGHT*0.34+ss.HUD_HEIGHT, 3, map, 1, 0)
            self.build_wall(ss.SCREEN_WIDTH * 0.95, ss.SCREEN_HEIGHT*0.5+ss.HUD_HEIGHT, 3, map, 1, 0)
        elif dir == 'w':
            self.build_wall(ss.SCREEN_WIDTH * 0.06, ss.SCREEN_HEIGHT * 0.34 + ss.HUD_HEIGHT, 7, map, 0, 1)
            self.build_wall(ss.SCREEN_WIDTH * 0.01, ss.SCREEN_HEIGHT * 0.34 + ss.HUD_HEIGHT, 3, map, 1, 0)
            self.build_wall(ss.SCREEN_WIDTH * 0.01, ss.SCREEN_HEIGHT * 0.5 + ss.HUD_HEIGHT, 3, map, 1, 0)

    def generate_challenge_room(self, map):
        map.entities = []
        treasure_chest = TreasureChest(self.player, map)
        map.add_entity((Shooter(self.player, map, (0, 0))))
        map.add_entity((Shooter(self.player, map, (0, 1))))
        map.add_entity((Shooter(self.player, map, (1, 0))))
        map.add_entity((Shooter(self.player, map, (1, 1))))
        for _ in range(4):
            map.add_entity(MobGenerator(self.player, map, Bat, 60, 8))
        map.add_entity(treasure_chest)
