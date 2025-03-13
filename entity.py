from pygame import Rect
import config_files.screen_size as ss
import pygame
import colors as c
import random
import config
import math
import utils

class Entity:
    def __init__(self, player, entity_map=None, position=None, size=10):
        self.player = player
        self.action = "idle"
        self.spritesheet = None
        self.health_time = 0
        self.frame_count = 0
        self.frame_index = 0
        self.speed = 1
        self.health = 10
        self.default_color = c.BLACK
        self.color = self.default_color
        self.invincible = False
        self.visible = True
        self.state = "alive"
        self.entities = []
        self.map = entity_map
        self.image = None
        self.update_health_color = c.RED
        self.rect = Rect(0, 0, size, size)
        if position is not None:
            self.rect.center = position
        else:
            self.generate_random_location()
        self.drops = [("coin", 5), ("healthpickup", 5)]
        self.xp = 1
        self.knockback = True
        self.impassable = False
        self.health_timeout = 0.5
        self.light_source = False
        self.flicker = False
        self.flicker_radius = 75
        self.interaction_rect = None
        self.block_rect = None
        self.fear = False
    def set_entities(self, entities):
        self.entities = entities

    def is_alive(self):
        return self.health > 0

    def update_health(self, num):
        if pygame.time.get_ticks() - self.health_time > self.health_timeout:
            self.invincible = True
            self.color = self.update_health_color
            self.health += num
            self.health_time = pygame.time.get_ticks()
            if self.knockback:
                self.handle_knockback()

    def handle_knockback(self, val=None):
        if val is None:
            knockback = 50
        else:
            knockback = val
            if self.player.weapon.hitbox.left > self.player.rect.left:
                self.rect.centerx += knockback
            elif self.player.weapon.hitbox.left < self.player.rect.left:
                self.rect.centerx -= knockback
            if self.player.weapon.hitbox.top > self.player.rect.top:
                self.rect.centery += knockback
            elif self.player.weapon.hitbox.top < self.player.rect.top:
                self.rect.centery -= knockback

    def update_health_override(self, num):
        self.health += num
        self.check_health()

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
            return
        self.frame_count += 1
        if self.frame_count > 99999:
            self.frame_count = 0


    def collide(self):
        self.player.weapon.collide(self)

    def draw(self, screen):
        if not self.visible: 
            return
        if self.image is not None and self.state != "dead":
            screen.blit(self.image, self.rect)
        else:
            if self.state != "dead" and self.visible:
                pygame.draw.rect(screen, self.color, self.rect)

    def check_damage_timeout(self, remove_invincibility=True):
        if self.invincible:
            if pygame.time.get_ticks() - self.health_time > self.health_timeout:
                self.color = self.default_color
                if remove_invincibility:
                    self.invincible = False

    def draw_boss_health_bar(self, screen):
        pygame.draw.rect(screen, c.BLACK, Rect(5, ss.SCREEN_HEIGHT - 50, 100, 20))
        pygame.draw.rect(screen, c.WHITE, Rect(7, ss.SCREEN_HEIGHT - 48, 95, 15))
        pygame.draw.rect(
            screen,
            c.RED,
            Rect(7, ss.SCREEN_HEIGHT - 48, (self.health / self.max_health) * 95, 15),
        )


    def add_fear(self, frames):
        self.fear_frames = frames
        self.fear = True


    def move_towards_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:  # Avoid division by zero
            dx /= distance
            dy /= distance
            if self.fear:
                dx = -dx
                dy = -dy
                self.fear_frames -= 1
                if self.fear_frames <= 0:
                    self.fear = False
            self.rect.centerx += dx * self.speed
            self.rect.centery += dy * self.speed

        if self.interaction_rect is not None:
            self.interaction_rect.center = self.rect.center
        if self.block_rect is not None:
            self.block_rect.center = self.rect.center


    def check_contact_damage(self, damage):
        if self.rect.colliderect(self.player.rect):
            self.player.update_health(-damage)

    def interact(self, screen):
        pass

    def check_health(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()

    def end(self):
        self.state = "dead"
        for drop in self.drops:
            r = random.randrange(100)
            if drop[1] >= r:
                entity = config.mob_registry.get(drop[0])
                to_add = entity(
                    self.player,
                    self.map,
                    position=(self.rect.centerx, self.rect.centery),
                )
                self.map.add_entity(to_add)
                break
        self.player.update_xp(self.xp)

    def generate_nearby_location(self):
        x = random.randrange(
            min(self.player.rect.centerx - 40, 0),
            max(self.player.rect.centerx + 40, ss.SCREEN_HEIGHT),
        )
        y = random.randrange(
            min(self.player.rect.centery - 40, 0),
            max(self.player.rect.centery + 40, ss.SCREEN_WIDTH),
        )
        self.rect.center = x, y

    def generate_random_location(self):
        x = random.randrange(40, int(ss.SCREEN_WIDTH*0.95))
        y = random.randrange(ss.HUD_HEIGHT, int(ss.SCREEN_HEIGHT*0.95))
        self.rect.center = x, y
        entity_rects = []
        for entity in self.map.get_entities():
            entity_rects.append(entity.rect)
        while any(self.rect.colliderect(other) for other in entity_rects):
            self.rect.center = (random.randrange(40, int(ss.SCREEN_WIDTH*0.95)), random.randrange(ss.HUD_HEIGHT, int(ss.SCREEN_HEIGHT*0.95)))


    def point_in_polygon(self, point, polygon):
        """
        Check if a point is inside a polygon using the ray-casting method.

        :param point: Tuple (x, y)
        :param polygon: List of (x, y) tuples representing the polygon vertices
        :return: True if the point is inside the polygon, False otherwise
        """
        x, y = point
        n = len(polygon)
        inside = False

        px1, py1 = polygon[0]
        for i in range(n + 1):
            px2, py2 = polygon[i % n]
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2

        return inside

    def block_path(self):
        if self.block_rect.colliderect(self.player.rect):
            if (
                self.player.rect.centery > self.rect.centery
                and abs(self.player.rect.centerx - self.rect.centerx)
                < self.rect.width / 2
            ):
                if "N" not in self.player.blocked_directions:
                    self.player.blocked_directions.append("N")
            elif (
                self.player.rect.centery < self.rect.centery
                and abs(self.player.rect.centerx - self.rect.centerx)
                < self.rect.width / 2
            ):
                if "S" not in self.player.blocked_directions:
                    self.player.blocked_directions.append("S")
            elif (
                self.player.rect.centerx < self.rect.centerx
                and abs(self.player.rect.centery - self.rect.centery)
                < self.rect.height / 2
            ):
                if "E" not in self.player.blocked_directions:
                    self.player.blocked_directions.append("E")
            elif (
                self.player.rect.centerx > self.rect.centerx
                and abs(self.player.rect.centery - self.rect.centery)
                < self.rect.height / 2
            ):
                if "W" not in self.player.blocked_directions:
                    self.player.blocked_directions.append("W")

    def set_random_position(self):
        positioned = False
        if len(self.map.entities) == 0:
            x = random.randrange(50, ss.SCREEN_WIDTH - 50)
            y = random.randrange(ss.HUD_HEIGHT + 50, ss.SCREEN_HEIGHT - 50)
            self.rect.center = x, y
            return
        while not positioned:
            for entity in self.map.entities:
                if self.rect.colliderect(entity.rect):
                    x = random.randrange(50, ss.SCREEN_WIDTH - 50)
                    y = random.randrange(ss.HUD_HEIGHT + 50, ss.SCREEN_HEIGHT - 50)
                    self.rect.center = x, y
                    positioned = False
                    break
                positioned = True


    def generate_loopy_path(self,
            length=100,
            step_range=(1, 5),
            loopiness=2,
            x_bounds=(-100, 100),
            y_bounds=(-100, 100), start=None
    ):
        """
        Generate a fixed-length loopy path with a random starting point.

        Args:
            length (int): Number of points in the path.
            step_range (tuple): Minimum and maximum step size for each point.
            loopiness (float): Determines the amount of curvature. Higher values create tighter loops.
            x_bounds (tuple): Lower and upper bounds for x-coordinates.
            y_bounds (tuple): Lower and upper bounds for y-coordinates.

        Returns:
            list: A list of (x, y) tuples representing the path.
        """
        # Randomly determine the starting point within the bounds
        if start is None:
            start_x = random.uniform(*x_bounds)
            start_y = random.uniform(*y_bounds)
        else:
            start_x = start[0]
            start_y = start[1]
        path = [(start_x, start_y)]

        angle = random.uniform(0, 2 * math.pi)  # Initial random direction

        for _ in range(length - 1):
            # Gradually adjust angle to keep the points near each other
            angle += random.uniform(-math.pi / loopiness, math.pi / loopiness)

            # Random step size
            step_size = random.uniform(*step_range)

            # Calculate new point
            last_x, last_y = path[-1]
            new_x = last_x + step_size * math.cos(angle)
            new_y = last_y + step_size * math.sin(angle)

            # Clamp coordinates to the specified bounds
            new_x = max(x_bounds[0], min(new_x, x_bounds[1]))
            new_y = max(y_bounds[0], min(new_y, y_bounds[1]))

            path.append((new_x, new_y))

        return path
    
    def handle_sprites(self, tile_size, scale, update_rate=5):
        if self.action is None or self.spritesheet == None:
            return
        if self.frame_count % update_rate != 0:
            return
        flip_h = self.rect.centerx > self.player.rect.centerx
        looking_up = self.rect.centery < self.player.rect.centery and abs(self.rect.centerx - self.player.rect.centerx) < 200
        if self.action == "idle" or self.action == 'lunge':
            if self.frame_index == 1:
                if looking_up:
                    self.image = utils.get_sprite(self.spritesheet, (tile_size ,0), tile_size, tile_size, scale, flip_h=flip_h)
                else:
                    self.image = utils.get_sprite(self.spritesheet, (tile_size,tile_size), tile_size, tile_size, scale, flip_h=flip_h)
                self.frame_index = 0
            else:
                if looking_up:
                    self.image = utils.get_sprite(self.spritesheet, (0,0), tile_size, tile_size, scale, flip_h=flip_h)
                else:
                    self.image = utils.get_sprite(self.spritesheet, (0,tile_size), tile_size, tile_size, scale, flip_h=flip_h)
                self.frame_index = 1


    