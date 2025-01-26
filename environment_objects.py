from entity import Entity
import pygame
from pygame import Rect
import random
import colors as c
import math
import resources
import config_files.screen_size as ss


class Hole(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.x_pos = random.randrange(
            min(player.x_pos - 40, 0), max(player.x_pos + 40, ss.SCREEN_HEIGHT)
        )
        self.y_pos = random.randrange(
            min(player.y_pos - 40, 0), max(player.y_pos + 40, ss.SCREEN_WIDTH)
        )
        self.rect = Rect(0, 0, 45, 45)
        self.block_rect = Rect(0, 0, 30, 30)
        self.rect.center = self.x_pos, self.y_pos
        self.block_rect.center = self.x_pos, self.y_pos

        self.color = c.BLACK
        self.state = "alive"

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=15)
        pygame.draw.rect(screen, self.color, self.block_rect)

    def collide(self):
        if self.state != "dead":
            self.block_path()


class Fire(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.x_pos = random.randrange(
            min(player.x_pos - 40, 0), max(player.x_pos + 40, ss.SCREEN_HEIGHT)
        )
        self.y_pos = random.randrange(
            min(player.y_pos - 40, 0), max(player.y_pos + 40, ss.SCREEN_WIDTH)
        )
        self.rect = Rect(0, 0, 30, 30)
        self.rect.center = self.x_pos, self.y_pos
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
        self.state = "alive"
        self.color_index = 0
        self.light_source = True
        self.colors = [
            (200, 0, 0),
            (250, 0, 0),
        ]
        self.flicker = True

    def update(self):
        if self.frame_count % 10 == 0:
            if self.color_index == len(self.colors):
                self.color_index = 0
            self.color = self.colors[self.color_index]
            self.color_index += 1

        if self.frame_count > 1000000:
            self.frame_count = 0
        self.frame_count += 1

    def collide(self):
        if self.rect.colliderect(self.player.rect):
            self.player.add_status("fire", 2)


class Water(Entity):
    def __init__(self, player, map, x_pos=200, y_pos=200):
        super().__init__(player, map)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = Rect(0, 0, 100, 100)
        self.points = []
        size = 150
        for i in range(100):
            x = random.randrange(self.x_pos - size, self.x_pos + size)
            y = random.randrange(self.y_pos - size, self.y_pos + size)
            if len(self.points) == 0:
                self.points.append((x, y))
            elif abs(self.points[-1][0] - x) > 25 and abs(self.points[-1][1] - y) > 25:
                self.points.append((x, y))
        self.points = nearest_neighbor_path(self.points)
        self.health = 1

        for i in range(len(self.points)):
            self.points[i] = (self.points[i][0], self.points[i][1] + 200)
        self.rect.center = self.x_pos, self.y_pos
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
        self.state = "alive"
        self.color_index = 0
        self.colors = [
            (0, 0, 50),
            (0, 0, 70),
        ]

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points)

    def update(self):
        if self.frame_count % 10 == 0:
            if self.color_index == len(self.colors):
                self.color_index = 0
            self.color = self.colors[self.color_index]
            self.color_index += 1
        if self.frame_count > 1000000:
            self.frame_count = 0
        self.frame_count += 1

    def collide(self):
        if self.point_in_polygon(self.player.rect.center, self.points):
            self.player.speed_modifier = 0.1
            self.player.status = [x for x in self.player.status if x[0] != "fire"]
        else:
            self.player.speed_modifier = 1


class Grass(Entity):
    def __init__(self, player, map, x_pos=100, y_pos=100):
        super().__init__(player, map)
        self.x_pos = random.randrange(
            min(player.x_pos - 40, 0), max(player.x_pos + 40, ss.SCREEN_HEIGHT)
        )
        self.y_pos = random.randrange(
            min(player.y_pos - 40, 0), max(player.y_pos + 40, ss.SCREEN_WIDTH)
        )
        self.rect = Rect(0, 0, 30, 30)
        self.image = pygame.transform.scale(
            resources.grass, (self.rect.width, self.rect.height)
        )
        self.health = 1
        self.rect.center = self.x_pos, self.y_pos
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
        self.state = "alive"
        self.xp = 0
        self.color_index = 0
        self.color = (0, 250, 0)

    def collide(self):
        if self.rect.colliderect(self.player.rect):
            self.player.speed_modifier = 0.8
        else:
            self.player.speed_modifier = 1    
        self.player.weapon.collide(self)


def generate_cartesian_outline(start=(200, 200), point_count=100, max_distance=50):
    points = []
    points.append(start)
    current_point_count = 1
    move_direction = True  # True for x, False for Y
    while current_point_count < point_count:
        if move_direction:
            pt = (
                points[current_point_count - 1][0]
                + random.randrange(-max_distance, max_distance),
                points[current_point_count - 1][1],
            )
        else:
            pt = (
                points[current_point_count - 1][0],
                points[current_point_count - 1][1]
                + random.randrange(-max_distance, max_distance),
            )
        points.append(pt)
        move_direction = not move_direction
        current_point_count += 1
    return points


class Rock(Entity):
    def __init__(self, player, map, x_pos=100, y_pos=100):
        super().__init__(player, map)

        self.x_pos = random.randrange(
            min(player.x_pos - 40, 75), max(player.x_pos + 40, ss.SCREEN_HEIGHT - 75)
        )
        self.y_pos = random.randrange(
            min(player.y_pos - 40, 75), max(player.y_pos + 40, ss.SCREEN_WIDTH - 75)
        )
        self.rect = Rect(0, 0, 50, 50)
        self.block_rect = Rect(0, 0, 60, 60)
        self.health = 1
        self.image = pygame.transform.scale(
            resources.rock, (self.rect.width, self.rect.height)
        )
        self.rect.center = self.x_pos, self.y_pos
        self.block_rect.center = self.x_pos, self.y_pos
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
        self.state = "alive"
        self.xp = 0
        self.color_index = 0
        self.color = (100, 100, 100)

    def collide(self):
        if self.state == "dead":
            return
        self.block_path()

        if self.player.weapon.active and self.rect.colliderect(self.player.weapon.hitbox):
            if "Pickaxe" in self.player.weapon.name:
                self.player.weapon.collide(self)


def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def nearest_neighbor_path(points):
    """
    Sort points to create a non-intersecting path using the nearest neighbor heuristic.

    Args:
        points (list of tuples): List of (x, y) coordinates.

    Returns:
        list of tuples: Ordered points.
    """
    if not points:
        return []

    points = list(points)  # Create a copy of the points to avoid modifying the original
    path = [points.pop(0)]  # Start with the first point (arbitrarily chosen)

    while points:
        # Find the nearest unvisited point
        last_point = path[-1]
        next_point = min(points, key=lambda p: distance(last_point, p))
        path.append(next_point)
        points.remove(next_point)

    result = []
    for i in range(len(path) - 1):
        result.append(path[i])
        if path[i][0] != path[i + 1][0]:
            result.append((path[i][0], path[i + 1][1]))
    result.append((path[0][0], path[-1][1]))

    return result


class MushroomPatch(Entity):
    def __init__(self, player, map, x_pos=100, y_pos=100):
        super().__init__(player, map)
        self.x_pos = random.randrange(30, ss.SCREEN_WIDTH - 30)
        self.y_pos = random.randrange(ss.HUD_HEIGHT + 30, ss.SCREEN_HEIGHT - 30)
        self.rect = Rect(0, 0, 30, 30)
        self.image = pygame.transform.scale(
            resources.mushroom, (self.rect.width, self.rect.height)
        )
        self.health = 1
        self.rect.center = self.x_pos, self.y_pos
        self.action_rect = self.rect.inflate(15, 15)
        self.action_rect.center = self.x_pos, self.y_pos
        self.drops = [("healthpickup", 5), ("energy", 5), ("coin", 5)]
        self.frame_count = 0
        self.state = "alive"
        self.xp = 0
        self.color_index = 0
        self.color = (0, 250, 0)

    def collide(self):
        if self.rect.colliderect(self.player.rect):
            self.player.speed_modifier = 0.8
        else:
            self.player.speed_modifier = 1
        self.player.weapon.collide(self)


class HotSpring(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.rect = Rect(0, 0, 50, 50)
        self.rect.center = ss.SCREEN_WIDTH / 2, (ss.SCREEN_HEIGHT + ss.HUD_HEIGHT) / 2
        self.frame_count = 0
        self.state = "alive"
        self.color = c.HOTSPRING

    def collide(self):
        if self.rect.colliderect(self.player.rect):
            self.frame_count += 1
            if self.frame_count % 100 == 0:
                self.player.update_health(1)
                self.player.energy = min(self.player.energy_max, self.player.energy + 1)
                self.frame_count = 0
