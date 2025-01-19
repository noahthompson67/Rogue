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


class Boss(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)

    def draw(self, screen):
        super().draw(screen)
        super().draw_boss_health_bar(screen)


class Telekinetic(Boss):
    def __init__(self, player, entity_map):
        super().__init__(player, entity_map)
        self.x_pos = ss.SCREEN_WIDTH / 2
        self.y_pos = ss.SCREEN_HEIGHT / 2
        self.rect = Rect(self.y_pos, self.x_pos, 50, 50)
        self.last_shot_time = 0
        self.action_rect = self.rect.inflate(500, 500)
        self.action_rect.center = self.x_pos, self.y_pos
        self.speed = 0.2
        self.default_color = c.SHOOTER_COLOR
        self.color = c.SHOOTER_COLOR
        self.projectile_count = 0
        self.radius = 100
        self.projectile_layer = 0
        self.state = "alive"
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
        if self.target_x > self.x_pos:
            self.x_pos += self.speed
        else:
            self.x_pos -= self.speed
        if self.target_y > self.y_pos:
            self.y_pos += self.speed
        else:
            self.y_pos -= self.speed
        self.frame_count += 1
        self.rect.center = self.x_pos, self.y_pos

    def set_not_invincible(self):
        self.invincible = False
        self.color = self.default_color

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if (
                self.player.sword_active
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
        self.x_pos = self.x_values[0]
        self.y_pos = self.y_values[0]
        self.arc_index = 1
        self.rect = Rect(self.x_pos, self.y_pos, 10, 10)
        self.speed = 0.5
        self.color = c.RED
        self.state = "alive"

    def update(self):
        if self.map.is_active() and self.owner.state != "dead":
            self.x_pos = self.x_values[self.arc_index]
            self.y_pos = self.y_values[self.arc_index]
            self.arc_index += 1
            if self.arc_index > 360:
                self.arc_index = 0
        elif self.owner.state == "dead" and self.state == "alive":
            self.player.update_xp(1)
            self.state = "dead"
        self.rect.center = self.x_pos + self.owner.x_pos, self.y_pos + self.owner.y_pos

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
                if self.player.last_direction == "N":
                    self.player.y_pos += 100
                elif self.player.last_direction == "S":
                    self.player.y_pos -= 100
                elif self.player.last_direction == "E":
                    self.player.x_pos += 100
                elif self.player.last_direction == "W":
                    self.player.x_pos -= 100


class TelekineticShard(Entity):
    def __init__(self, player, map, owner):
        super().__init__(player, map)
        self.owner = owner
        self.health = 1

        self.state = "alive"
        self.x_pos = random.randrange(0, ss.SCREEN_WIDTH - 50)
        self.y_pos = random.randrange(0, ss.SCREEN_HEIGHT - 50)
        self.rect = Rect(self.x_pos, self.y_pos, 10, 10)

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if self.player.sword_active and self.rect.colliderect(
                self.player.weapon.hitbox
            ):
                self.player.weapon.collide(self)

    def update(self):
        super().update()
        if self.state == "dead":
            self.owner.set_not_invincible()
            self.map.remove_dead_entities()


class Golem(Boss):
    def __init__(self, player, entity_map):
        super().__init__(player, entity_map)
        self.x_pos = random.randrange(100, ss.SCREEN_WIDTH - 100)
        self.y_pos = random.randrange(100, ss.SCREEN_HEIGHT - 100)
        self.rect = Rect(self.y_pos, self.x_pos, 50, 50)
        self.default_color = (120, 120, 120)
        self.color = self.default_color
        self.speed = 0.75
        self.last_shot_time = 0
        self.max_health = 10
        self.health = 10
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
        if self.invincible:
            self.move_towards_player()
        else:
            if random.random() < 0.003:
                self.invincible = True
        for entity in self.map.entities:
            if self.rect.colliderect(entity.rect):
                if isinstance(entity, Rock):
                    self.map.entities.remove(entity)
                    proj = Projectile(
                        self.player, self.map, self.x_pos + 16, self.y_pos
                    )
                    proj.speed = 8
                    proj.reflectable = True
                    self.map.add_entity(proj)
                    self.projectiles.append(proj)
        if (
            pygame.time.get_ticks() - self.last_shot_time > 10000
            and self.map.is_active()
        ):
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
                    abs(hole.rect.x - self.player.x_pos) > 10
                    and abs(hole.rect.y - self.player.y_pos) > 10
                ):
                    self.map.add_entity(Hole(self.player, self.map))
            self.last_shot_time = pygame.time.get_ticks()
        self.check_damage_timeout(False)
        for proj in self.projectiles:
            if proj.rect.colliderect(self.rect) and proj.reflected:
                self.invincible = False

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-1)
            if (
                self.player.sword_active
                and self.rect.colliderect(self.player.weapon.hitbox)
                and not self.invincible
            ):
                self.player.weapon.collide(self)
                self.check_health()
                self.invincible = True

    def end(self):
        self.state = "dead"
        to_add = Coin(self.player, self.map, (self.x_pos, self.y_pos), 10)
        self.map.add_entity(to_add)

        self.player.update_xp(self.xp)

