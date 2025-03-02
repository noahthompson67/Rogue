from entity import Entity
import pygame
from pygame import Rect
import random
import colors as c
import math
import resources
import config_files.screen_size as ss
import config


class Hole(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        x = random.randrange(
            min(player.rect.centerx - 40, 0), max(player.rect.centery + 40, ss.SCREEN_HEIGHT)
        )
        y = random.randrange(
            min(player.rect.centery - 40, 0), max(player.rect.centery + 40, ss.SCREEN_WIDTH)
        )
        self.block_rect = Rect(0, 0, 30, 30)
        self.rect.center = x, y
        self.block_rect.center = x, y

        self.color = c.BLACK

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=15)
        pygame.draw.rect(screen, self.color, self.block_rect)

    def collide(self):
        if self.state != "dead":
            self.block_path()


class Fire(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        x = random.randrange(
            min(player.rect.centerx - 40, 0), max(player.rect.centerx + 40, ss.SCREEN_HEIGHT)
        )
        y = random.randrange(
            min(player.rect.centery - 40, 0), max(player.rect.centery + 40, ss.SCREEN_WIDTH)
        )
        self.rect.center = x, y
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
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
    def __init__(self, player, map):
        super().__init__(player, map)
        self.points = []
        size = 150
        for i in range(100):
            x = random.randrange(200 - size, 200 + size)
            y = random.randrange(200 - size, 200 + size)
            if len(self.points) == 0:
                self.points.append((x, y))
            elif abs(self.points[-1][0] - x) > 25 and abs(self.points[-1][1] - y) > 25:
                self.points.append((x, y))
        self.points = nearest_neighbor_path(self.points)
        self.health = 1

        for i in range(len(self.points)):
            self.points[i] = (self.points[i][0], self.points[i][1] + 200)
        self.rect.center = 200, 200
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
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
    def __init__(self, player, map):
        super().__init__(player, map, size=30)
        x = random.randrange(
            min(player.rect.centerx - 40, 0), max(player.rect.centery + 40, ss.SCREEN_HEIGHT)
        )
        y = random.randrange(
            min(player.rect.centery - 40, 0), max(player.rect.centery + 40, ss.SCREEN_WIDTH)
        )
        self.image = pygame.transform.scale(
            resources.grass, (self.rect.width, self.rect.height)
        )
        self.health = 1
        self.rect.center = x, y
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
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
    def __init__(self, player, map, location=(0, 0)):
        if location == (0, 0):
            x = random.randrange(
                min(player.rect.centerx - 40, 75), max(player.rect.centery + 40, ss.SCREEN_HEIGHT - 75)
            )
            y = random.randrange(
                min(player.rect.centery - 40, 75), max(player.rect.centery + 40, ss.SCREEN_WIDTH - 75)
            )
        else:
            x = location[0]
            y = location[1]
        super().__init__(player, map, position=(x,y), size=50)

        
        self.block_rect = Rect(0, 0, 60, 60)
        self.health = 1
        self.image = pygame.transform.scale(
            resources.rock, (self.rect.width, self.rect.height)
        )
        self.block_rect.center = x, y
        self.action_rect = self.rect.inflate(15, 15)
        self.frame_count = 0
        self.xp = 0
        self.color_index = 0
        self.color = (100, 100, 100)
        self.knockback = False

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
    def __init__(self, player, map):
        x = random.randrange(30, ss.SCREEN_WIDTH - 30)
        y = random.randrange(ss.HUD_HEIGHT + 30, ss.SCREEN_HEIGHT - 30)
        super().__init__(player, map, position=(x, y), size=30)
        self.image = pygame.transform.scale(
            resources.mushroom, (self.rect.width, self.rect.height)
        )
        self.health = 1
        self.action_rect = self.rect.inflate(15, 15)
        self.drops = [("healthpickup", 5), ("energy", 5), ("coin", 5)]
        self.frame_count = 0
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
        pos = (ss.SCREEN_WIDTH / 2, (ss.SCREEN_HEIGHT + ss.HUD_HEIGHT) / 2)
        super().__init__(player, map, position=pos, size=50)
        self.frame_count = 0
        self.color = c.HOTSPRING

    def collide(self):
        if self.rect.colliderect(self.player.rect):
            self.frame_count += 1
            if self.frame_count % 100 == 0:
                self.player.update_health(1)
                self.player.energy = min(self.player.energy_max, self.player.energy + 1)
                self.frame_count = 0

class Tree(Entity):
    def __init__(self, player, map, pos=None):
        super().__init__(player, map, position=pos, size=50)
        self.color = (0, 120, 0)
        self.health = 5
        self.block_rect = self.rect.inflate(10, 10)
        self.knockback = False
        self.update_health_color = (0, 120, 0)

    def end(self):
        self.rect = self.rect.inflate(-5, -5)
        self.state = "undead"
        self.color = (120, 120, 0)
        self.update_health_color = (120, 120, 0)

    def collide(self):
        if self.player.weapon.name == "Axe":
            self.player.weapon.collide(self)
        if self.state == "alive":
            self.block_path()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, self.rect.width, 15, 15)

class MovableObject(Entity):
    def __init__(self, player, map, pos=None, size=40):
        super().__init__(player, map, position=pos, size=size)
        self.size = size
    
    def collide(self):
        p_x = self.player.rect.centerx
        p_y = self.player.rect.centery
        x = self.rect.centerx
        y = self.rect.centery

        if abs(p_x - x) <= self.player.rect.width and abs(p_y - y) <= self.player.rect.width:
            if self.player.rect.centery < self.rect.centery and abs(p_x - x) <= self.size/2:
                    self.rect.centery += self.player.speed
            elif self.player.rect.centery > self.rect.centery and abs(p_x - x) <= self.size/2:
                    self.rect.centery -= self.player.speed
            elif self.player.rect.centerx < self.rect.centerx and abs(p_y - y) <= self.size/2:
                self.rect.centerx += self.player.speed
            elif self.player.rect.centerx > self.rect.centerx and abs(p_y - y) <= self.size/2:
                self.rect.centerx -= self.player.speed

class Bomb(Entity):
    def __init__(self, player, map, pos=None):
        super().__init__(player, map, position=pos, size=15)
        self.name = "Bomb"
        self.color = (10, 10, 10)
        self.display_color = self.color
        self.charge_frames_max = 200
        self.explode_frames_max = self.charge_frames_max + 5
        self.placed = False
        self.frame_count = 0
        self.drops = []
        self.xp = 0
        self.damage = 10
        self.knockback = False

    def update(self):
        self.frame_count += 1
        if self.frame_count < self.charge_frames_max:
            if self.frame_count % 10 == 0:
                red_amount = min((self.frame_count/self.charge_frames_max) * 250, 200)
                self.color = (red_amount, 10, 10)
        elif self.frame_count < self.explode_frames_max:
            self.rect.inflate_ip(10,10)
            self.check_contact_damage(1)
            for entity in self.map.entities:
                if self.rect.colliderect(entity.rect):
                    entity.update_health(-self.damage)
        else:
            self.end()

    def draw(self, screen):
        if self.state == 'alive':
            pygame.draw.rect(screen, self.color, self.rect, border_radius=15)

class Path(Entity):
    def __init__(self, player, map, pos=None):
        super().__init__(player, map, position=pos, size=15)
        self.rects = []
        self.color = (255, 255, 255)
        if self.map.north:
            pos = self.map.SOUTH_WARP_PLAYER_POS
            rect = Rect(pos[0], pos[1], 30, ss.SCREEN_HEIGHT/2)
            rect.centerx = ss.SCREEN_WIDTH / 2
            self.rects.append(rect)
        if self.map.south:
            pos = self.map.NORTH_WARP_PLAYER_POS
            rect = Rect(pos[0], pos[1]-ss.SCREEN_HEIGHT/2, 30, ss.SCREEN_HEIGHT/2)
            rect.centerx = ss.SCREEN_WIDTH / 2
            self.rects.append(rect)
        if self.map.east:
             pos = self.map.WEST_WARP_PLAYER_POS
             rect = Rect(pos[0]-ss.SCREEN_WIDTH/2+config.WARP_SIZE*2, pos[1], ss.SCREEN_WIDTH/2-config.WARP_SIZE, 30)
             rect.centery = ss.SCREEN_HEIGHT / 2 + ss.HUD_HEIGHT / 2
             self.rects.append(rect)
             
        if self.map.west:
            pos = self.map.EAST_WARP_PLAYER_POS
            rect = Rect(pos[0], pos[1], ss.SCREEN_WIDTH/2+config.WARP_SIZE, 30)
            rect.centery = ss.SCREEN_HEIGHT / 2 + ss.HUD_HEIGHT / 2
            self.rects.append(rect)
                              

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, self.color, rect)

    def update(self):
        pass

