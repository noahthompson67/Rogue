import random

import config_files.screen_size as ss
import resources
from entity import Entity
import pygame
from pygame import Rect
import colors as c
import weapon

HEALTH_PICKUP_SIZE = 30


class HealthPickup(Entity):
    def __init__(self, player, map, health_amount=10, position=None):
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        super().__init__(player, map, position=position)
        self.health_amount = health_amount
        self.state = "alive"
        self.rect = Rect(
            position[0], position[1], HEALTH_PICKUP_SIZE, HEALTH_PICKUP_SIZE
        )
        self.rect.center = position
        self.image = pygame.transform.scale(
            resources.medkit, (self.rect.width, self.rect.height)
        )

    def collide(self):
        if self.player.health == self.player.health_max:
            return
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.update_health(self.health_amount)


class Coin(Entity):
    def __init__(self, player, map, position=None, value=None):
        super().__init__(player, map)
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        self.value = value
        if self.value is None:
            self.value = random.choice([1, 5, 10])
        if self.value == 1:
            self.color = (168, 88, 50)
        elif self.value == 5:
            self.color = (120, 125, 130)
        else:
            self.color = (196, 201, 207)

        self.state = "alive"
        self.rect = Rect(0, 0, HEALTH_PICKUP_SIZE, HEALTH_PICKUP_SIZE)
        self.rect.center = position

    def draw(self, screen):
        if self.state == "alive":
            pygame.draw.rect(screen, self.color, self.rect, 15, 15, 15, 15)

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.money += self.value


class EnergyPickup(Entity):
    def __init__(self, player, map, energy_amount=10, position=None):
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        super().__init__(player, map, position=position)
        self.energy_amount = energy_amount
        self.state = "alive"
        self.rect = Rect(
            position[0], position[1], HEALTH_PICKUP_SIZE, HEALTH_PICKUP_SIZE
        )
        self.rect.center = position
        self.image = pygame.transform.scale(
            resources.energy, (self.rect.width, self.rect.height)
        )

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.energy = min(
                    self.player.energy_max, self.player.energy + self.energy_amount
                )


class TreasureChest(Entity):
    def __init__(self, player, map, position=None):
        super().__init__(player, map)
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        self.state = "closed"
        self.rect = Rect(0, 0, 30, 30)
        self.rect.center = position
        self.color = (110, 110, 80)
        self.block_rect = Rect(0, 0, 30, 30)
        self.block_rect.center = position
        self.treasure = weapon.Pickaxe(self.player, "pickaxe")

    def draw(self, screen):
        if self.state == "closed":
            pygame.draw.rect(
                screen, self.color, self.rect, self.rect.width, self.rect.height
            )
        else:
            pygame.draw.rect(
                screen, c.GREEN, self.rect, self.rect.width, self.rect.height
            )

    def collide(self):
        self.block_path()

    def interact(self, screen):
        if (
            self.block_rect.colliderect(self.player.rect)
            and self.map.get_enemies_remaining() == 0
        ):
            self.state = "open"
            if isinstance(self.treasure, weapon.Weapon):
                self.player.weapons.append(self.treasure)


class Key(Entity):
    def __init__(self, player, map, position=None):
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        super().__init__(player, map, position=position)
        self.state = "alive"
        self.rect = Rect(
            position[0], position[1], HEALTH_PICKUP_SIZE, HEALTH_PICKUP_SIZE
        )
        self.rect.center = position
        self.image = pygame.transform.scale(
            resources.key, (self.rect.width, self.rect.height)
        )

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.keys += 1
