import enemies
import environment_objects
import colors as c
import pygame
from pygame import Rect
import config

class Weapon:
    def __init__(self, player, name):
        self.player = player
        self.damage = self.player.damage
        self.name = name
        self.color = c.GREEN
        self.range = 30
        self.active_timeout = 200
        self.start_time = 0
        self.active = False
        self.hitbox = Rect(
            self.player.y_pos, self.player.x_pos, config.PLAYER_SIZE, config.PLAYER_SIZE
        )
    def collide(self, entity):
        entity.update_health(-self.damage)
        # TODO: handle knockback

    def use(self, keys):
        if not self.active:
            self.active = True
            self.start_time = pygame.time.get_ticks()
        if keys[pygame.K_UP]:
            self.hitbox = Rect(self.player.rect.left, self.player.rect.top - self.range, config.PLAYER_SIZE, self.range)
            self.hitbox.centerx = self.player.rect.centerx
        elif keys[pygame.K_DOWN]:
            self.hitbox = Rect(self.player.rect.left, self.player.rect.bottom, config.PLAYER_SIZE, self.range)
            self.hitbox.centerx = self.player.rect.centerx
        elif keys[pygame.K_LEFT]:
            self.hitbox = Rect(self.player.rect.left-self.range, self.player.rect.bottom, self.range, config.PLAYER_SIZE)
            self.hitbox.centery = self.player.rect.centery
        elif keys[pygame.K_RIGHT]:
            self.hitbox = Rect(self.player.rect.right, self.player.rect.bottom, self.range, config.PLAYER_SIZE)
            self.hitbox.centery = self.player.rect.centery


    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.hitbox)



class Pickaxe(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = self.player.damage / 2
        self.color = (100, 100, 3)
        self.range = 15

    def collide(self, entity):
        if isinstance(entity, environment_objects.Rock) and self.player.energy > 0:
            entity.update_health(-100)
        elif isinstance(entity, enemies.Rock) and self.player.energy > 0:
            entity.update_health(-100)
        elif self.player.energy > 0:
            entity.update_health(-1)
        else:
            entity.update_health(0)
        self.player.energy -= 1
        self.player.energy = max(0, self.player.energy)


class CursedBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 1000
        self.color = (120, 0, 0)

    def collide(self, entity):
        super().collide(entity)
        self.player.health = min(self.player.health, 1)


class GhostBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.color = (120, 120, 120)

    def collide(self, entity):
        super().collide(entity)
        entity.update_health_override(-1)
        self.player.energy -= 1

class Laser(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.color = (120, 20, 20)
        self.charge_level = 0

    def collide(self, entity):
        super().collide(entity)
        entity.update_health_override(-1)
        self.player.energy -= 1

    def use(self, keys):
        super().use(keys)
        self.charge_level += 1
        print(f"Charge level: {self.charge_level}")






