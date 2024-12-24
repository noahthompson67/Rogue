
from pygame import Rect
import config_files.screen_size as ss
import pygame
import colors as c
import random
import config



class Entity:
    def __init__(self, player, entity_map=None, position=None):
        self.player = player
        self.health_time = 0
        self.health = 10
        self.default_color = c.BLACK
        self.color = self.default_color
        self.invincible = False
        self.visible = True
        self.x_pos = 0
        self.y_pos = 0
        self.state = "alive"
        self.entities = []
        self.map = entity_map
        self.image = None
        self.rect = Rect(0, 0, 10, 10)
        if position is not None:
            self.rect.center = position
        self.drops = [("coin", 5), ("healthpickup", 5)]
        self.xp = 1
        self.knockback = True
        self.impassable = False
        self.health_timeout = 0.5
        self.light_source = False

    def set_entities(self, entities):
        self.entities = entities

    def is_alive(self):
        return self.health > 0

    def update_health(self, num):
        if pygame.time.get_ticks() - self.health_time > self.health_timeout:
            self.invincible = True
            self.color = c.RED
            self.health += num
            self.health_time = pygame.time.get_ticks()
            if self.knockback:
                if self.player.sword_hitbox.left > self.player.rect.left:
                    self.x_pos += 50
                elif self.player.sword_hitbox.left < self.player.rect.left:
                    self.x_pos -= 50
                if self.player.sword_hitbox.top > self.player.rect.top:
                    self.y_pos += 50
                elif self.player.sword_hitbox.top < self.player.rect.top:
                    self.y_pos -= 50

    def update_health_override(self, num):
        self.health += num

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
            return

    def collide(self):
        if self.player.sword_active and self.rect.colliderect(self.player.sword_hitbox):
            self.player.weapon.collide(self)

    def draw(self, screen):
        if self.image is not None and self.state != 'dead':
            screen.blit(self.image, self.rect)
        elif self.state != "dead" and self.visible:
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
            Rect(
                7, ss.SCREEN_HEIGHT - 48, (self.health / self.max_health) * 95, 15
            ),
        )

    def move_towards_player(self):
        if self.player.x_pos > self.x_pos:
            self.x_pos += self.speed
        elif self.player.x_pos < self.x_pos:
            self.x_pos -= self.speed
        if self.player.y_pos > self.y_pos:
            self.y_pos += self.speed
        elif self.player.y_pos < self.y_pos:
            self.y_pos -= self.speed
        self.rect.center = self.x_pos, self.y_pos

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
                to_add = entity(self.player, self.map, position=(self.rect.centerx, self.rect.centery))
                self.map.add_entity(to_add)
                break
        self.player.update_xp(self.xp)

    def generate_nearby_location(self):
        self.x_pos = random.randrange(
            min(self.player.x_pos - 40, 0),
            max(self.player.x_pos + 40, ss.SCREEN_HEIGHT),
        )
        self.y_pos = random.randrange(
            min(self.player.y_pos - 40, 0),
            max(self.player.y_pos + 40, ss.SCREEN_WIDTH),
        )
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
            if self.player.rect.centery > self.rect.centery and abs(
                    self.player.rect.centerx - self.rect.centerx) < self.rect.width / 2:
                if 'N' not in self.player.blocked_directions:
                    self.player.blocked_directions.append('N')
            elif self.player.rect.centery < self.rect.centery and abs(
                    self.player.rect.centerx - self.rect.centerx) < self.rect.width / 2:
                if 'S' not in self.player.blocked_directions:
                    self.player.blocked_directions.append('S')
            elif self.player.rect.centerx < self.rect.centerx and abs(
                    self.player.rect.centery - self.rect.centery) < self.rect.height / 2:
                if 'E' not in self.player.blocked_directions:
                    self.player.blocked_directions.append('E')
            elif self.player.rect.centerx > self.rect.centerx and abs(
                    self.player.rect.centery - self.rect.centery) < self.rect.height / 2:
                if 'W' not in self.player.blocked_directions:
                    self.player.blocked_directions.append('W')

    def set_random_position(self):
        positioned = False
        while not positioned:
            for entity in self.map.entities:
                if self.rect.colliderect(entity.rect):
                    x = random.randrange(50, ss.SCREEN_WIDTH-50)
                    y = random.randrange(ss.HUD_HEIGHT + 50, ss.SCREEN_HEIGHT-50)
                    self.rect.center = x, y
                    positioned = False
                    break
                positioned = True

