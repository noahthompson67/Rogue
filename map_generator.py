import random

from pygame import Rect

import colors as c
from map import Map
import config
from colors import BLACK, WHITE
import time
from biome_map_generators.biome import Biome
import config_files.screen_size as ss
from environment_objects import HotSpring
import pygame


class MapGenerator:
    def __init__(self, screen, player, name):
        self.screen = screen
        self.player = player
        self.origin_cell = 5, 5
        self.grid_size = 10, 10
        self.biome_name = name
        self.biome = Biome(self.player, self.biome_name)
        self.zone = self.generate_grid(self.grid_size[0], self.grid_size[1])

        self.zone[5][6].warps[1].lock()

        self.current_map = self.zone[self.origin_cell[0]][self.origin_cell[1]]
        self.current_map.set_active()
        self.init_minimap()
        self.visited = []
        self.visited_adjacent = []
        self.generate_special_rooms()

    def warp(self, warp_rect, map_idx=-1):
        if map_idx >= 0:
            if not self.current_map.warps[map_idx].locked:
                warp = self.current_map.warps[map_idx]
                self.set_current_map(warp.map)
                warp.translate_player()
                self.current_map.remove_dead_entities()
                self.current_map.remove_temporary_entities()
            elif self.current_map.warps[map_idx].locked and self.player.keys > 0:
                self.player.keys -= 1
                self.current_map.warps[map_idx].lock()

    def warp_animation(self):
        self.screen.fill(BLACK)
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(60)
        time.sleep(0.05)

    def get_current_map(self):
        return self.current_map

    def warp_command(self, row, col):
        self.set_current_map(self.zone[row][col])

    def set_current_map(self, new_map):
        self.current_map.set_inactive()
        self.current_map = new_map
        self.current_map.set_active()

    def set_map_by_location(self, location):
        self.current_map.set_inactive()
        self.current_map = self.zone[location[0]][location[1]]
        self.current_map.set_active()

    def remove_dead_entities(self):
        self.current_map.remove_dead_entities()

    def init_minimap(self):
        minimap_x_offset = (
            ss.SCREEN_WIDTH - (self.grid_size[0] + 5) * config.MINIMAP_CELL_SIZE
        )
        minimap_y_offset = config.MINIMAP_CELL_SIZE
        self.minimap_outer_rect_border = Rect(
            minimap_x_offset,
            minimap_y_offset,
            (self.grid_size[0] + 4) * config.MINIMAP_CELL_SIZE,
            (self.grid_size[1] + 4) * config.MINIMAP_CELL_SIZE,
        )
        self.minimap_inner_rect_border = Rect(
            minimap_x_offset + config.MINIMAP_CELL_SIZE,
            minimap_y_offset + config.MINIMAP_CELL_SIZE,
            (self.grid_size[0] + 2) * config.MINIMAP_CELL_SIZE,
            (self.grid_size[1] + 2) * config.MINIMAP_CELL_SIZE,
        )

        self.minimap = []
        x_offset = minimap_x_offset + config.MINIMAP_CELL_SIZE * 2
        y_offset = minimap_y_offset + config.MINIMAP_CELL_SIZE * 2
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if self.grid[i][j] != 0:
                    rect = Rect(
                        x_offset + (j * config.MINIMAP_CELL_SIZE),
                        y_offset + (i * config.MINIMAP_CELL_SIZE),
                        config.MINIMAP_CELL_SIZE,
                        config.MINIMAP_CELL_SIZE,
                    )
                    self.minimap.append((rect, (i, j), False))

    def draw_minimap(self, screen):
        pygame.draw.rect(screen, BLACK, self.minimap_outer_rect_border)
        pygame.draw.rect(screen, WHITE, self.minimap_inner_rect_border)
        for map in self.minimap:
            if map[1] == self.current_map.location:
                pygame.draw.rect(screen, c.MAP_POSITION, map[0])
                if map[1] not in self.visited:
                    self.visited.append(map[1])
                    map_x = map[1][0]
                    map_y = map[1][1]
                    if map_x < len(self.grid) - 1 and self.grid[map_x + 1][map_y] != 0:
                        self.visited_adjacent.append((map_x + 1, map_y))
                    if map_x > 0 and self.grid[map_x - 1][map_y] != 0:
                        self.visited_adjacent.append((map_x - 1, map_y))
                    if (
                        map_y < len(self.grid[0]) - 1
                        and self.grid[map_x][map_y + 1] != 0
                    ):
                        self.visited_adjacent.append((map_x, map_y + 1))
                    if map_y > 0 and self.grid[map_x][map_y - 1] != 0:
                        self.visited_adjacent.append((map_x, map_y - 1))
            elif map[1] == self.boss_map and (
                map[1] in self.visited or map[1] in self.visited_adjacent
            ):
                pygame.draw.rect(screen, c.MAP_BOSS, map[0])
            elif map[1] == self.treasure_map and (
                self.treasure_map in self.visited
                or self.treasure_map in self.visited_adjacent
            ):
                pygame.draw.rect(screen, c.MAP_TREASURE, map[0])
            elif map[1] == self.settlement_map and (
                self.settlement_map in self.visited
                or self.settlement_map in self.visited_adjacent
            ):
                pygame.draw.rect(screen, c.MAP_SETTLEMENT, map[0])
            elif map[1] in self.visited:
                pygame.draw.rect(screen, c.MAP_DISCOVERED, map[0])
                if map[1] == self.hotspring_map:
                    pygame.draw.rect(screen, c.HOTSPRING, map[0])
            elif map[1] in self.visited_adjacent:
                pygame.draw.rect(screen, c.MAP_ADJACENT, map[0])

    def set_full_minimap(self):
        for map in self.minimap:
            if map[1] not in self.visited:
                self.visited.append(map[1])

    def generate_grid(self, rows, columns):
        if self.biome_name == "cave":
            spritesheet = pygame.image.load("assets/gfx/cave.png").convert()
        elif self.biome_name == "forest":
            spritesheet = pygame.image.load("assets/gfx/Overworld.png").convert()
        else:
            spritesheet = None
        self.grid = [[0 for _ in range(columns)] for _ in range(rows)]
        zone = [
            [
                Map(f"{row}, {col}", self.screen, self.player, (row, col), self.biome, spritesheet=spritesheet)
                for col in range(columns)
            ]
            for row in range(rows)
        ]
        self.grid = [
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 1, 0, 0, 0],
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 2, 0],
        ]

        # (0,4), (2, 0), (4, 0)

        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if not self.grid[i][j]:
                    continue
                warps = 0
                if i > 0 and self.grid[i - 1][j] != 0:
                    zone[i][j].set_north_map(zone[i - 1][j])
                    warps += 8
                if i < rows - 1 and self.grid[i + 1][j] != 0:
                    zone[i][j].set_south_map(zone[i + 1][j])
                    warps += 4
                if j < columns - 1 and self.grid[i][j + 1] != 0:
                    zone[i][j].set_east_map(zone[i][j + 1])
                    warps += 2
                if j > 0 and self.grid[i][j - 1] != 0:
                    zone[i][j].set_west_map(zone[i][j - 1])
                    warps += 1
                zone[i][j].set_directions(warps)
                self.biome.generate_map(zone[i][j])
        return zone

    def get_zone_ends(self):
        result = []
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if self.grid[i][j] == 0:
                    continue
                if i == 3 and j == 0:
                    pass
                n = i > 0 and self.grid[i - 1][j] == 1
                s = i < len(self.grid) - 1 and self.grid[i + 1][j] == 1
                e = j < len(self.grid[0]) - 1 and self.grid[i][j + 1] == 1
                w = j > 0 and self.grid[i][j - 1] == 1
                if n + s + e + w == 1:
                    result.append((i, j))
        return result

    def generate_special_rooms(self):
        zone_ends = self.get_zone_ends()

        # Place Hotspring
        self.hotspring_map = (
            random.randrange(0, len(self.grid)),
            random.randrange(0, len(self.grid[0])),
        )
        while (
            self.hotspring_map in zone_ends
            or self.grid[self.hotspring_map[0]][self.hotspring_map[1]] == 0
        ):
            self.hotspring_map = (
                random.randrange(0, len(self.grid)),
                random.randrange(0, len(self.grid[0])),
            )
        self.zone[self.hotspring_map[0]][self.hotspring_map[1]].add_entity(
            HotSpring(
                self.player, self.zone[self.hotspring_map[0]][self.hotspring_map[1]]
            )
        )

        # Place Boss
        self.boss_map = zone_ends[random.randrange(0, len(zone_ends))]
        bx = self.boss_map[0]
        by = self.boss_map[1]
        self.biome.generate_boss_map(self.zone[bx][by])
        if bx > 0 and self.grid[bx - 1][by] == 1:
            self.biome.generate_boss_entrance(self.zone[bx - 1][by], "s")
        elif bx < len(self.grid) - 1 and self.grid[bx + 1][by] == 1:
            self.biome.generate_boss_entrance(self.zone[bx + 1][by], "n")
        elif by > 0 and self.grid[bx][by - 1] == 1:
            self.biome.generate_boss_entrance(self.zone[bx][by - 1], "e")
        elif by < len(self.grid[0]) - 1 and self.grid[bx][by + 1] == 1:
            self.biome.generate_boss_entrance(self.zone[bx][by + 1], "w")
        self.zone[8][1].entities = []
        zone_ends.remove(self.boss_map)

        # Place Treasure
        self.treasure_map = zone_ends[random.randrange(0, len(zone_ends))]
        self.biome.generate_challenge_room(
            self.zone[self.treasure_map[0]][self.treasure_map[1]]
        )
        zone_ends.remove(self.treasure_map)

        self.settlement_map = zone_ends[random.randrange(0, len(zone_ends))]
        print(f"settlement: {self.settlement_map}")
        self.biome.generate_settlement(
            self.zone[self.settlement_map[0]][self.settlement_map[1]]
        )
