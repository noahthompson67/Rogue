import random

import pygame.time

from entity import Entity
from environment_objects import Rock, Hole
from enemies import Projectile
import colors as c
from pygame import Rect
import config_files.screen_size as ss
import numpy as np
from items import Coin
from enemies import BoomerangProjectile
import config
import utils
class Boss(Entity):
    def __init__(self, player, map, size=75, position=None):
        super().__init__(player, map, position, size=size)

    def draw(self, screen):
        super().draw(screen)
        super().draw_boss_health_bar(screen)


class Telekinetic(Boss):
    def __init__(self, player, entity_map):
        super().__init__(player, entity_map, size=50)
        self.last_shot_time = 0
        self.action_rect = self.rect.inflate(500, 500)
        self.speed = 0.2
        self.default_color = c.SHOOTER_COLOR
        self.color = c.SHOOTER_COLOR
        self.projectile_count = 0
        self.radius = 100
        self.projectile_layer = 0
        self.max_health = 4
        self.health = 4
        self.frame_count = 0
        self.projectile_layer_maxes = [6, 13, 20]
        self.invincible = False
        self.knockback = False

    def update(self):
        if (
            pygame.time.get_ticks() - self.last_shot_time > 1
            and self.map.is_active()
            and self.projectile_layer < len(self.projectile_layer_maxes)
        ):
            if (
                self.projectile_count
                > self.projectile_layer_maxes[self.projectile_layer]
            ):
                self.projectile_layer += 1
                self.radius += 75
            if self.projectile_layer < len(self.projectile_layer_maxes):
                self.map.add_entity(
                    OrbitalProjectile(
                        self.player, self.map, self.radius, self.projectile_layer, self
                    )
                )
            self.projectile_count += 1
            self.last_shot_time = pygame.time.get_ticks()
        if self.frame_count > 255 or self.frame_count == 0:
            self.target_x = random.randrange(
                ss.SCREEN_WIDTH / 2 - 10, ss.SCREEN_WIDTH / 2 + 10
            )
            self.target_y = random.randrange(
                ss.SCREEN_HEIGHT / 2 - 10, ss.SCREEN_HEIGHT / 2 + 10
            )
            self.frame_count = 1
        if self.target_x > self.rect.centerx:
            self.rect.centerx += self.speed
        else:
            self.rect.centerx -= self.speed
        if self.target_y > self.rect.centery:
            self.rect.centery += self.speed
        else:
            self.rect.centery -= self.speed
        self.frame_count += 1

    def set_not_invincible(self):
        self.invincible = False
        self.color = self.default_color

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if (
                self.player.weapon.active
                and self.rect.colliderect(self.player.weapon.hitbox)
                and not self.invincible
            ):
                self.player.weapon.collide(self)
                self.check_health()
                self.invincible = True
                if self.state != "dead":
                    self.map.add_entity(TelekineticShard(self.player, self.map, self))


class OrbitalProjectile(Entity):
    def __init__(self, player, map, radius, layer, owner):
        super().__init__(player, map)
        self.owner = owner
        t_degrees = np.arange(0, 361)
        t_radians = np.radians(t_degrees)
        self.x_values = radius * np.cos(t_radians)
        self.y_values = radius * np.sin(t_radians)
        if layer & 1 == 1:
            self.x_values = self.x_values[::-1]
            self.y_values = self.y_values[::-1]
        self.rect.center = self.x_values[0], self.y_values[0]
        self.arc_index = 1
        self.speed = 0.5
        self.color = c.RED

    def update(self):
        if self.map.is_active() and self.owner.state != "dead":
            self.arc_index += 1
            if self.arc_index > 360:
                self.arc_index = 0
        elif self.owner.state == "dead" and self.state == "alive":
            self.player.update_xp(1)
            self.state = "dead"
        self.rect.center = self.x_values[self.arc_index] + self.owner.rect.centerx, self.y_values[self.arc_index] + self.owner.rect.centery

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
                if self.player.last_direction == "N":
                    self.player.rect.centery += 100
                elif self.player.last_direction == "S":
                    self.player.rect.centery -= 100
                elif self.player.last_direction == "E":
                    self.player.rect.centerx += 100
                elif self.player.last_direction == "W":
                    self.player.rect.centerx -= 100


class TelekineticShard(Entity):
    def __init__(self, player, map, owner):
        x = random.randrange(0, ss.SCREEN_WIDTH - 50)
        y = random.randrange(ss.HUD_HEIGHT + 50, ss.SCREEN_HEIGHT - 50)
        super().__init__(player, map, size=75, position=(x,y))
        self.owner = owner
        self.health = 1

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if (self.player.weapon.active and self.rect.colliderect(
                self.player.weapon.hitbox
            )):
                self.player.weapon.collide(self)

    def update(self):
        super().update()
        if self.state == "dead":
            self.owner.set_not_invincible()
            self.map.remove_dead_entities()


class Golem(Boss):
    def __init__(self, player, entity_map):
        x = random.randrange(100, ss.SCREEN_WIDTH - 100)
        y = random.randrange(100, ss.SCREEN_HEIGHT - 100)
        super().__init__(player, entity_map, position=(x,y), size=50)
        self.spritesheet = pygame.image.load("assets/golem.png")
        self.image = utils.get_sprite(self.spritesheet, (0, 0), 32, 32, 2)
        self.frame_index = 0
        self.ability_active = False
        self.animation_complete = False
        self.default_color = (120, 120, 120)
        self.color = self.default_color
        self.speed = 0.75
        self.last_shot_time = 0
        self.max_health = 10
        self.health = 10
        self.frame_count = 0
        self.health_timeout = 3
        self.knockback = False
        self.projectiles = []
        self.invincible = True
        self.xp = 15

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
            return
        if self.invincible and not self.ability_active:
            self.move_towards_player()
            self.__check_rock_collisions()
        else:
            if random.random() < 0.003:
                self.invincible = True
        if (
            pygame.time.get_ticks() - self.last_shot_time > 10000
            and self.map.is_active()
        ):
            if not self.ability_active:
                self.ability_active = True
            if self.ability_active and self.animation_complete:
                self.ability_active = False
                self.animation_complete = False
                self.__spawn_environment_objects()
        self.check_damage_timeout(False)
        for proj in self.projectiles:
            if proj.rect.colliderect(self.rect) and proj.reflected:
                self.invincible = False
        self.__handle_sprites()


    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if (
                self.player.weapon.active
                and self.rect.colliderect(self.player.weapon.hitbox)
                and not self.invincible
            ):
                self.player.weapon.collide(self)
                self.check_health()
                self.invincible = True

    def end(self):
        self.state = "dead"
        to_add = Coin(self.player, self.map, (self.rect.centerx, self.rect.centery), 10)
        self.map.add_entity(to_add)

        self.player.update_xp(self.xp)

    def __spawn_environment_objects(self):
        rock_wall_count = random.randrange(1, 5)
        hole_spawn_count = random.randrange(1, 5)
        for _ in range(rock_wall_count):
            first_rock = Rock(self.player, self.map)
            first_rock_pos = first_rock.rect.center
            rock_spawn_count = random.randrange(1, 10)
            vertical_wall = random.choice([True, False])
            for i in range(rock_spawn_count):
                rock = Rock(self.player, self.map)
                if vertical_wall:
                    rock.rect.center = (
                        first_rock_pos[0],
                        first_rock_pos[1] + i * 30,
                    )

                else:
                    rock.rect.center = (
                        first_rock_pos[0] + i * 30,
                        first_rock_pos[1],
                    )
                rock.health = random.randrange(1, 10)
                rock.block_rect.center = rock.rect.center
                rock.drops = []
                self.map.add_entity(rock)
        for _ in range(hole_spawn_count):
            hole = Hole(self.player, self.map)
            if (
                abs(hole.rect.x - self.player.rect.centerx) > 10
                and abs(hole.rect.y - self.player.rect.centery) > 10
            ):
                self.map.add_entity(Hole(self.player, self.map))
        self.last_shot_time = pygame.time.get_ticks()

    def __check_rock_collisions(self):
        for entity in self.map.entities:
            if self.rect.colliderect(entity.rect):
                if isinstance(entity, Rock):
                    self.map.entities.remove(entity)
                    proj = Projectile(
                        self.player, self.map, position=(self.rect.centerx + 16, self.rect.centery)
                    )
                    proj.speed = 8
                    proj.reflectable = True
                    self.map.add_entity(proj)
                    self.projectiles.append(proj)

    def __handle_sprites(self):
        flip_h = self.rect.centerx > self.player.rect.centerx
        if self.ability_active and not self.animation_complete:
             if self.frame_count % 5 == 0:
                if self.frame_index == 4:
                    self.image = utils.get_sprite(self.spritesheet, (32,32), 32, 32, 2, flip_h=flip_h)
                    self.frame_index = 5
                elif self.frame_index == 5:
                    self.image = utils.get_sprite(self.spritesheet, (32,32), 32, 32, 2, flip_h=flip_h)
                    self.frame_index = 6
                elif self.frame_index == 6:
                    self.image = utils.get_sprite(self.spritesheet, (64,32), 32, 32, 2, flip_h=flip_h)
                    self.frame_index = 0
                    self.animation_complete = True
                    self.ability_active = False
                else:
                    self.image = utils.get_sprite(self.spritesheet, (0,32), 32, 32, 2, flip_h=flip_h)
                    self.frame_index = 4
        else:
            if self.frame_count % 5 == 0:
                if self.frame_index == 0:
                    self.frame_index = 1
                    self.image = utils.get_sprite(self.spritesheet, (32,0), 32, 32, 2, flip_h=flip_h)
                elif self.frame_index == 1:
                    self.image = utils.get_sprite(self.spritesheet, (64,0), 32,  32, 2, flip_h=flip_h)
                    self.frame_index = 0
        self.frame_count += 1
        if self.frame_count > 99999:
            self.frame_count = 0

class Reaper(Boss):
    def __init__(self, player, map):
        super().__init__(player, map, size=50)
        self.max_health = 50
        self.health = 50
        self.path = self.generate_loopy_path(length=100, step_range=(1, 1), loopiness=1, x_bounds=(50, ss.SCREEN_WIDTH*.95), y_bounds=(ss.HUD_HEIGHT+50, ss.SCREEN_HEIGHT*.95))
        self.rect.center = self.path[0]
        self.path_index = 0
        self.lunge_frames = 0
        self.default_color = (0, 0, 0)
        self.frame_count = 0
        self.speed = 4
        self.action = 'idle'
        self.projectiles = []
        self.projectile = None
        self.spritesheet = pygame.image.load("assets/reaper.png")
        self.animation_complete = False
        self.frame_index = 0

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
        if self.frame_count % 100 == 0:
            r = random.randrange(10, 200)
            self.color = (r, r, r)
        if self.frame_count > 1000:
            self.frame_count = 0
        if self.action == 'idle' and random.random() < 0.05:
                self.action = random.choice(['throw', 'throw', 'lunge', 'lunge', 'spawn', 'spawn', 'idle', 'idle', 'teleport'])
                if self.action == 'lunge':
                    self.lunge_frames = 80
        elif self.action == 'idle':
            if self.path_index == len(self.path) - 1:
                self.reverse = True
            elif self.path_index == 0:
                self.reverse = False
            self.rect.center = self.path[self.path_index]
            if self.reverse:
                self.path_index -= 1
            else:
                self.path_index += 1
        elif self.action == 'teleport':
            self.color = (250, 250, 250)
            self.invincible = True
            if self.animation_complete:
                self.animation_complete = False
                self.path = self.generate_loopy_path(length=100, step_range=(1, 1), loopiness=1, x_bounds=(50, ss.SCREEN_WIDTH*.95), y_bounds=(ss.HUD_HEIGHT+50, ss.SCREEN_HEIGHT*.95))
                self.path_index = 0
                self.action = 'idle'
                r = random.randrange(10, 200)
                self.color = (r, r, r)
                self.invincible = False
        elif self.action == 'throw':   
            if len(self.projectiles) > 0:
                self.action = 'idle'
                return
            proj = BoomerangProjectile(self.player, self.map, (self.rect.centerx, self.rect.centery))
            proj.speed = 0.2
            self.map.add_entity(proj)
            self.projectiles.append(proj)
            self.action = 'idle'
        elif self.action == 'spawn':
            spawn_count = random.randrange(1, 5)
            for i in range(spawn_count):
                spawn_type = random.choice(['zombie', 'ghost', 'orb'])
                mob = config.mob_registry.get(spawn_type)(self.player, self.map)
                mob.drops = []
                self.map.add_entity(mob)
            self.action = 'idle'
        elif self.action == 'lunge':
            self.move_towards_player()
            self.lunge_frames -= 1
            if self.lunge_frames == 0:
                self.action = 'teleport'

        for proj in self.projectiles:
            if proj.state == 'dead':
                self.projectiles.remove(proj)
        self.frame_count += 1
        self.__handle_sprites()

    def draw(self, screen):
        super().draw(screen)

    def __handle_sprites(self):
        if self.frame_count % 10 == 0:
            looking_up = self.rect.centery > self.player.rect.centery
            flip_h = self.rect.centerx > self.player.rect.centerx
            if self.action == "idle":
                if self.frame_index == 0:
                    if looking_up:
                        self.image = utils.get_sprite(self.spritesheet, (0,64), 32,  32, 2, flip_h=flip_h)
                    else:
                        self.image = utils.get_sprite(self.spritesheet, (0,0), 32,  32, 2, flip_h=flip_h)
                    self.frame_index = 1
                else:
                    if looking_up:
                        self.image = utils.get_sprite(self.spritesheet, (32,64), 32,  32, 2, flip_h=flip_h)
                    else:
                        self.image = utils.get_sprite(self.spritesheet, (32,0), 32,  32, 2, flip_h=flip_h)
                    self.frame_index = 0
            elif self.action == "teleport":
                if self.frame_index == 11:
                    self.image = utils.get_sprite(self.spritesheet, (32,128), 32,  32, 2)
                    self.frame_index = 12
                elif self.frame_index == 12:
                    self.image = utils.get_sprite(self.spritesheet, (64,128), 32,  32, 2)
                    self.frame_index = 0
                    self.animation_complete = True
                else:
                    self.image = utils.get_sprite(self.spritesheet, (0,128), 32,  32, 2)
                    self.frame_index = 11
            elif self.action == "lunge":
                if self.frame_index == 4:
                    if looking_up:
                        self.image = utils.get_sprite(self.spritesheet, (96,32), 32,  32, 2, flip_h=flip_h)
                    else:
                        self.image = utils.get_sprite(self.spritesheet, (32,32), 32,  32, 2, flip_h=flip_h)
                    self.frame_index = 0
                else:
                    if looking_up:
                        self.image = utils.get_sprite(self.spritesheet, (96,32), 32,  32, 2, flip_h=flip_h)
                    else:
                        self.image = utils.get_sprite(self.spritesheet, (0,32), 32,  32, 2, flip_h=flip_h)
                    self.frame_index = 4
