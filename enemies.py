import resources
from entity import Entity
import random
import config_files.screen_size as ss
import pygame
import colors as c
from pygame import Rect
import math

ZOMBIE_SIZE = 50
ENEMY_HEALTH_TIMEOUT = 0.5
ZOMBIE_SPEED = 0.75

class Enemy:
    def __init__(self):
        pass
class Zombie(Entity, Enemy):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.generate_nearby_location()
        self.action_rect = Rect(
            self.x_pos, self.y_pos, ZOMBIE_SIZE * 5, ZOMBIE_SIZE * 5
        )
        self.health = 3
        self.default_color = c.ZOMBIE_RED
        self.color = self.default_color
        self.speed = 0.75
        self.rect = Rect(self.x_pos, self.y_pos, ZOMBIE_SIZE, ZOMBIE_SIZE)

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
            return
        self.move_towards_player()

        self.check_damage_timeout()

    def collide(self):
        if self.state != "dead":
            self.check_contact_damage(1)
            if self.action_rect.colliderect(self.player.rect):
                self.speed = min(1.5, self.speed + 0.05)
            else:
                self.speed = max(ZOMBIE_SPEED, self.speed - 0.05)
            if self.player.sword_active and self.rect.colliderect(
                self.player.sword_hitbox
            ):
                self.player.weapon.collide(self)


class Shooter(Entity, Enemy):
    def __init__(self, player, map, position=(-1, -1)):
        super().__init__(player, map)

        self.x_pos = random.choice([1, 3]) * ss.SCREEN_WIDTH / 4
        self.y_pos = random.choice([1, 3]) * ss.SCREEN_HEIGHT / 4
        if position != (-1, -1):
            self.x_pos = position[0] * ss.SCREEN_WIDTH / 4
            self.y_pos = position[1] * ss.SCREEN_HEIGHT / 4
        self.rect = Rect(self.y_pos, self.x_pos, 50, 50)
        self.last_shot_time = 0
        self.action_rect = Rect(self.x_pos, self.y_pos, 500, 500)
        self.rect.center = self.x_pos, self.y_pos
        self.action_rect.center = self.x_pos, self.y_pos
        self.color = c.SHOOTER_COLOR
        self.state = 'undead'
        self.sprite = pygame.image.load("gargoyle.png")
        self.sprite = pygame.transform.scale(
            self.sprite, (self.rect.width, self.rect.height)
        )
        self.shot = False

    def update(self):
        if (
            self.action_rect.colliderect(self.player.rect)
            and pygame.time.get_ticks() - self.last_shot_time > 5000
            and self.map.is_active()
        ):
            self.shot = True
            to_add = Projectile(self.player, self.map, self.x_pos + 16, self.y_pos)
            to_add.reflectable = True
            self.map.add_entity(to_add)
            self.last_shot_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)


class Projectile(Entity, Enemy):
    def __init__(self, player, map, x_pos, y_pos):
        super().__init__(player, map)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = Rect(self.x_pos, self.y_pos, 20, 20)
        target_pos = player.rect.center
        self.speed = 1
        self.color = c.RED
        self.creation_time = pygame.time.get_ticks()
        self.direction_x = target_pos[0] - self.x_pos
        self.direction_y = target_pos[1] - self.y_pos
        self.reflectable = False
        self.reflected = False
        distance = math.sqrt(self.direction_x**2 + self.direction_y**2)
        self.sprite = pygame.image.load("projectile.png")
        self.sprite = pygame.transform.scale(
            self.sprite, (self.rect.width, self.rect.height)
        )
        # Normalize the direction vector
        if distance != 0:
            self.direction_x /= distance
            self.direction_y /= distance

    def update(self):
        if pygame.time.get_ticks() - self.creation_time > 10000:
            self.state = "dead"
            self.color = c.BLACK
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            elif (
                self.rect.colliderect(self.player.sword_hitbox)
                and self.reflectable
                and self.player.sword_active
                and not self.reflected
            ):
                self.reflected = True
                upper = self.rect.centery < self.player.rect.centery
                left = self.rect.centerx < self.player.rect.centerx
                middle_x = abs(self.player.rect.centerx - self.rect.centerx) < 10
                middle_y = abs(self.player.rect.centery - self.rect.centery) < 10
                x = self.rect.centerx
                y = ss.SCREEN_HEIGHT - self.rect.centery
                if middle_x and upper:
                    print(12)
                    target_x = self.x_pos
                    target_y = 0
                elif middle_x and not upper:
                    print(6)
                    target_x = self.x_pos
                    target_y = ss.SCREEN_HEIGHT
                elif middle_y and left:
                    print(9)
                    target_x = 0
                    target_y = self.y_pos
                elif middle_y and not left:
                    print(3)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.y_pos
                elif upper and left and not middle_y and not middle_x:
                    if -x > y:
                        print(10)
                    else:
                        print(11)
                    target_x = 0
                    target_y = self.y_pos / self.x_pos
                elif not upper and left and not middle_y and not middle_x:
                    if x < y:
                        print(8)
                    else:
                        print(7)
                    target_x = 0
                    target_y = self.x_pos * self.y_pos
                elif upper and not left and not middle_y and not middle_x:
                    if x < y:
                        print(1)
                    else:
                        print(2)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.y_pos / self.x_pos
                elif not upper and not left and not middle_y and not middle_x:
                    if -x > y:
                        print(4)
                    else:
                        print(5)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.x_pos * self.y_pos

                self.direction_x = target_x - self.x_pos
                self.direction_y = target_y - self.y_pos
                distance = math.sqrt(self.direction_x**2 + self.direction_y**2)
                if distance != 0:
                    self.direction_x /= distance
                    self.direction_y /= distance

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)


class Ghost(Entity, Enemy):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.generate_nearby_location()
        self.action_rect = Rect(
            self.x_pos, self.y_pos, ZOMBIE_SIZE * 5, ZOMBIE_SIZE * 5
        )
        self.health = 3
        self.default_color = c.GHOST_COLOR
        self.color = self.default_color
        self.speed = 0.75
        self.rect = Rect(self.x_pos, self.y_pos, ss.PLAYER_SIZE, ss.PLAYER_SIZE)
        self.frame_count = random.randrange(0, 50)

    def update(self):
        self.frame_count += 1
        if self.frame_count == 100:
            self.visible = False
            self.invincible = True
        elif self.frame_count >= 200:
            self.invincible = False
            self.visible = True
            self.frame_count = 0
        self.move_towards_player()
        self.check_damage_timeout()

    def collide(self):
        self.check_contact_damage(1)


class Bat(Entity, Enemy):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.generate_nearby_location()
        self.x_pos = random.randrange(0, ss.SCREEN_WIDTH)
        self.y_pos = random.randrange(0, ss.SCREEN_HEIGHT)
        self.health = 1
        self.default_color = c.BLACK
        self.color = self.default_color
        self.speed = 1.75

        self.rect = Rect(self.x_pos, self.y_pos, 25, 25)
        self.frame_count = random.randrange(0, 50)
        self.first_frame = True
        self.image = resources.bat_1
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


    def update(self):
        if self.state == 'alive':
            self.move_towards_player()
            self.check_damage_timeout()
            self.frame_count += 1
            if self.frame_count % 10 == 0:
                self.frame_count = 1
                if self.first_frame:
                    self.image = resources.bat_2
                else:
                    self.image = resources.bat_1
                self.first_frame = not self.first_frame
                self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


        super().update()



    def collide(self):
        if self.state == 'alive':
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-2)
                if random.random() < 0.75:
                    self.player.add_status('poison', random.randrange(1, 10)*100)
            if self.player.sword_active and self.rect.colliderect(
                    self.player.sword_hitbox
            ):
                self.player.weapon.collide(self)



class MobGenerator(Entity, Enemy):
    def __init__(self, player, map, mob, freq, mob_count = -1):
        super().__init__(player, map)
        self.generate_nearby_location()
        self.mob_count = mob_count
        self.action_rect = Rect(
            self.x_pos, self.y_pos, 10, 10
        )
        self.health = 1
        self.default_color = c.GOLD
        self.color = self.default_color
        self.rect = Rect(self.x_pos, self.y_pos, 10, 10)
        self.spawn_time = pygame.time.get_ticks()
        self.mob = mob
        self.frequency = freq

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.frequency:
            to_add = self.mob(self.player, self.map)
            distance = ((self.player.rect.centerx - to_add.rect.centerx)**2 + (self.player.rect.centery - to_add.rect.centery)**2)**0.5
            while(distance < 10):
                to_add = self.mob(self.player, self.map)
                distance = ((self.player.rect.centerx - to_add.rect.centerx) ** 2 + (
                            self.player.rect.centery - to_add.rect.centery) ** 2) ** 0.5

            to_add.drops = []
            self.map.add_entity(to_add)
            self.mob_count -= 1
            if self.mob_count == 0:
                self.end()
            self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        pass




