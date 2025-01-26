
import colors as c
import pygame
from pygame import Rect
import config
import enemies
import environment_objects

class Weapon:
    def __init__(self, player, name):
        self.player = player
        self.damage = self.player.damage
        self.name = name
        self.color = c.GREEN
        self.display_color = self.color
        self.range = 30
        self.active_timeout = 200
        self.start_time = 0
        self.active = False
        self.dir_down = None
        self.dir_up = None
        self.hitbox = Rect(
            self.player.y_pos, self.player.x_pos, config.PLAYER_SIZE, config.PLAYER_SIZE
        )
        self.projectiles = []

    def collide(self, entity):
        if self.active and self.hitbox.colliderect(entity.rect):
            entity.update_health(-self.damage)
        for projectile in self.projectiles:
            projectile.collide(entity)

    def update(self):
        if self.active:
            self.handle_direction()
            if pygame.time.get_ticks() - self.start_time > self.active_timeout:
                self.active = False

    def key_up(self, key):
        if key == pygame.K_UP:
            self.dir_up = 'up'
        elif key == pygame.K_DOWN:
            self.dir_up = 'down'
        elif key == pygame.K_LEFT:
            self.dir_up = 'left'
        elif key == pygame.K_RIGHT:
            self.dir_up = 'right'


    def key_down(self, key):
        if key == pygame.K_UP:
            self.dir_down = 'up'
            self.active = True
            self.start_time = pygame.time.get_ticks()
        elif key == pygame.K_DOWN:
            self.dir_down = 'down'
            self.active = True
            self.start_time = pygame.time.get_ticks()
        elif key == pygame.K_LEFT:
            self.dir_down = 'left'
            self.active = True
            self.start_time = pygame.time.get_ticks()
        elif key == pygame.K_RIGHT:
            self.dir_down = 'right'
            self.active = True
            self.start_time = pygame.time.get_ticks()

    def handle_direction(self):
        if self.dir_down == 'up':
                self.hitbox = Rect(self.player.rect.left, self.player.rect.top - self.range, config.PLAYER_SIZE, self.range)
                self.hitbox.centerx = self.player.rect.centerx
        elif self.dir_down == 'down':
            self.hitbox = Rect(self.player.rect.left, self.player.rect.bottom, config.PLAYER_SIZE, self.range)
            self.hitbox.centerx = self.player.rect.centerx
        elif self.dir_down == 'left':
            self.hitbox = Rect(self.player.rect.left-self.range, self.player.rect.bottom, self.range, config.PLAYER_SIZE)
            self.hitbox.centery = self.player.rect.centery
        elif self.dir_down == 'right':
            self.hitbox = Rect(self.player.rect.right, self.player.rect.bottom, self.range, config.PLAYER_SIZE)
            self.hitbox.centery = self.player.rect.centery
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.hitbox)
        for projectile in self.projectiles:
            projectile.draw(screen)



class Pickaxe(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = self.player.damage / 2
        self.color = (100, 100, 3)
        self.display_color = self.color
        self.range = 15

    def collide(self, entity):
        if isinstance(entity, environment_objects.Rock) and self.player.energy > 0:
            entity.update_health(-100)
        elif isinstance(entity, enemies.BadRock) and self.player.energy > 0:
            entity.update_health(-100)
        elif self.player.energy > 0:
            entity.update_health(-1)
        self.player.energy -= 1
        self.player.energy = max(0, self.player.energy)


class CursedBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 1000
        self.color = (120, 0, 0)
        self.display_color = self.color
    def collide(self, entity):
        super().collide(entity)
        self.player.health = min(self.player.health, 1)


class GhostBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.color = (120, 120, 120)
        self.display_color = self.color

    def collide(self, entity):
        super().collide(entity)
        entity.update_health_override(-1)
        self.player.energy -= 1

class Laser(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.default_damage = 0
        self.color = (255, 20, 20)
        self.display_color = self.color
        self.charge_level = 0
        self.charged = False
        self.range = 5
        self.default_range = self.range

    def collide(self, entity):
        super().collide(entity)
        entity.update_health_override(-1)
        self.player.energy -= 1
 

    def update(self):
        if self.charged:
            self.range = 150
            self.handle_direction()
            self.dir_up = None
            self.charge_level = 0
            if pygame.time.get_ticks() - self.start_time > 300:
                self.range = self.default_range
                self.active = False
                self.charged = False
        elif self.active:
            self.handle_direction()
            self.charge_level += 5
            self.color = (min(self.charge_level, 255), 20, 20)

        if self.dir_up == self.dir_down and self.dir_up is not None:
            if self.charge_level > 200:
                self.dir_up = None
                self.charge_level = 1
                self.charged = True
                self.player.energy -= 1
                self.start_time = pygame.time.get_ticks()
            else:
                self.charge_level = 1
                self.active = False
                self.dir_up = None
                self.dir_down = None

class Bow(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.default_damage = 0
        self.color = (120, 120, 0)
        self.display_color = self.color
        self.charge_level = 0
        self.charged = False
        self.range = 5
        self.default_range = self.range
        self.arrows = [] 

    def update(self):
        if self.charged:
            arrow = Projectile(self, self.dir_up)
            arrow.speed = min(self.charge_level / 10 + 1, 10)
            self.projectiles.append(arrow)
            self.dir_up = None
            self.charge_level = 1
            self.active = False
            self.charged = False
        elif self.active:
            self.handle_direction()
            self.charge_level += 5
        if self.dir_up == self.dir_down and self.dir_up is not None:
            if self.charge_level > 50:
                self.charged = True
                self.start_time = pygame.time.get_ticks()
            else:
                self.charge_level = 1
                self.active = False
                self.dir_up = None
                self.dir_down = None
        for arrow in self.projectiles:
            arrow.update()


        

class Projectile():
    def __init__(self, owner, direction):
        self.owner = owner
        if direction == 'up':
            self.x_dir = 0
            self.y_dir = -1
        elif direction == 'down':
            self.x_dir = 0
            self.y_dir = 1
        elif direction == 'left': 
            self.x_dir = -1
            self.y_dir = 0
        elif direction == 'right':
            self.x_dir = 1
            self.y_dir = 0
        self.rect = Rect(owner.hitbox)
        if self.x_dir != 0:
            self.rect.height *= 0.5
            self.rect.width *= 3
        elif self.y_dir != 0:
            self.rect.width *= 0.5
            self.rect.height *= 3
        self.rect.center = owner.hitbox.center
        self.color = (120, 120, 0)
        self.speed = 5

    def update(self):
        self.rect.centerx += self.x_dir * self.speed
        self.rect.centery += self.y_dir * self.speed
 
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def collide(self, entity):
        print('aaaa')
        if self.rect.colliderect(entity.rect):
            entity.update_health(-1)
            self.owner.projectiles.remove(self)
            return True
        return False
           






