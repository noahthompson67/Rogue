import random
from enum import Enum
import pygame.draw
from enemies import Projectile
from pygame import Rect
import colors as c
import config
import config_files.screen_size as ss
from enemies import Enemy
WHITE = (255, 255, 255)
WARP_COLOR = (150, 0, 255)


class MapName(Enum):
    DEAD_END_WEST = 1
    DEAD_END_EAST = 2
    HORIZONTAL_HALL = 3
    DEAD_END_SOUTH = 4
    SOUTH_WEST_CORNER = 5
    SOUTH_EAST_CORNER = 6
    SOUTH_TEE = 7
    DEAD_END_NORTH = 8
    NORTH_WEST_CORNER = 9
    NORTH_EAST_CORNER = 10
    NORTH_TEE = 11
    VERTICAL_HALL = 12
    WEST_TEE = 13
    EAST_TEE = 14
    CROSS = 15




class Map:
    def __init__(self, name, screen, player, location=(0, 0)):
        self.screen = screen
        self.player = player
        self.name = name
        self.location = location
        self.init_warp_pos(config)
        self.active = False
        if isinstance(name, Enum):
            self.set_directions(name.value)
        elif isinstance(name, int):
            self.set_directions(int(name))

        self.north, self.south, self.east, self.west = False, False, False, False

        self.north_warp = None
        self.south_warp = None
        self.east_warp = None
        self.west_warp = None

        self.north_map = None
        self.south_map = None
        self.east_map = None
        self.west_map = None

        self.warps = []
        self.entities = []
        self.generate_random_enemies()

    def generate_warps(self):
        if self.north:
            self.warps.append(
                Warp(
                    self.get_north_map(),
                    self.NORTH_WARP_POS,
                    self.player,
                    self.NORTH_WARP_PLAYER_POS,
                )
            )
        if self.south:
            self.warps.append(
                Warp(
                    self.get_south_map(),
                    self.SOUTH_WARP_POS,
                    self.player,
                    self.SOUTH_WARP_PLAYER_POS,
                )
            )
        if self.east:
            self.warps.append(
                Warp(
                    self.get_east_map(),
                    self.EAST_WARP_POS,
                    self.player,
                    self.EAST_WARP_PLAYER_POS,
                )
            )
        if self.west:
            self.warps.append(
                Warp(
                    self.get_west_map(),
                    self.WEST_WARP_POS,
                    self.player,
                    self.WEST_WARP_PLAYER_POS,
                )
            )

    def draw_map(self, screen):
        for warp in self.warps:
            warp.draw(self.screen)

    def get_warps(self):
        result = []
        if self.north_warp:
            result.append(self.north_warp)
        if self.south_warp:
            result.append(self.south_warp)
        if self.east_warp:
            result.append(self.east_warp)
        if self.west_warp:
            result.append(self.west_warp)

        return result

    def set_inactive(self):
        self.active = False

    def set_active(self):
        self.active = True

    def is_active(self):
        return self.active

    def set_north_map(self, map):
        self.north_map = map

    def set_south_map(self, map):
        self.south_map = map

    def set_east_map(self, map):
        self.east_map = map

    def set_west_map(self, map):
        self.west_map = map

    def get_north_map(self):
        return self.north_map

    def get_south_map(self):
        return self.south_map

    def get_east_map(self):
        return self.east_map

    def get_west_map(self):
        return self.west_map

    def get_entities(self):
        return self.entities

    def add_entity(self, entity):
        self.entities.append(entity)

    def set_entities(self, entities):
        self.entities = entities

    def remove_dead_entities(self):
        temp = []
        for entity in self.entities:
            if entity.state != "dead":
                temp.append(entity)
        self.entities = temp

    def remove_temporary_entities(self):
        temp = []
        for entity in self.entities:
            if not isinstance(entity, Projectile):
                temp.append(entity)
        self.entities = temp

    def set_directions(self, num):
        self.north = bool(num & 8)
        self.south = bool(num & 4)
        self.east = bool(num & 2)
        self.west = bool(num & 1)
        self.generate_warps()

    def generate_random_enemies(self, spawn_count=0):
        mobs = list(config.mob_registry.values())
        for _ in range(spawn_count):
            try:
                mob = mobs[random.randrange(0, len(mobs))]
                to_add = mob(self.player, self)
                self.add_entity(to_add)
            except TypeError:
                continue

    def init_warp_pos(self, config):
        self.NORTH_WARP_POS = ss.SCREEN_WIDTH / 2, config.WARP_SIZE / 2 + ss.HUD_HEIGHT
        self.SOUTH_WARP_POS = (
            ss.SCREEN_WIDTH / 2,
            ss.SCREEN_HEIGHT - config.WARP_SIZE / 2,
        )
        self.WEST_WARP_POS = config.WARP_SIZE / 2, ss.SCREEN_HEIGHT / 2 + ss.HUD_HEIGHT / 2
        self.EAST_WARP_POS = ss.SCREEN_WIDTH - config.WARP_SIZE / 2, ss.SCREEN_HEIGHT / 2 + ss.HUD_HEIGHT / 2

        self.NORTH_WARP_PLAYER_POS = (
            self.SOUTH_WARP_POS[0],
            self.SOUTH_WARP_POS[1] - config.PLAYER_SIZE,
        )
        self.SOUTH_WARP_PLAYER_POS = (
            self.NORTH_WARP_POS[0],
            self.NORTH_WARP_POS[1] + config.PLAYER_SIZE * 1.5,
        )
        self.EAST_WARP_PLAYER_POS = (
            self.WEST_WARP_POS[0] + config.PLAYER_SIZE * 1.5,
            self.WEST_WARP_POS[1],
        )
        self.WEST_WARP_PLAYER_POS = (
            self.EAST_WARP_POS[0] - config.PLAYER_SIZE * 1.5,
            self.EAST_WARP_POS[1],
        )

    def get_enemies_remaining(self):
        count = 0
        for entity in self.entities:
            if isinstance(entity, Enemy) and entity.state == 'alive':
                count += 1
        return count

class Warp:
    def __init__(self, map, position, player, player_pos, location=(-1, -1)):
        self.map = map  # What map this warps towards
        self.player = player
        self.player_pos = player_pos
        self.location = location
        self.position = position  # Where its drawn
        self.locked = False
        self.color = c.WARP
        self.rect = Rect(position[0], position[1], config.WARP_SIZE, config.WARP_SIZE)
        self.rect.center = position[0], position[1]
        if self.map is None:
            print(f"no map for warp: {self.location}\n{self.position}")

    def translate_player(self):
        self.player.x_pos = self.player_pos[0]
        self.player.y_pos = self.player_pos[1]

    def lock(self):
        if self.locked:
            self.locked = False
            self.color = c.WARP
        else:
            self.locked = True
            self.color = c.LOCKED_WARP

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

