import random

import config_files.screen_size as ss
import resources
from entity import Entity
import pygame
from pygame import Rect
import colors as c
import weapon
import utils

HEALTH_PICKUP_SIZE = 30


class HealthPickup(Entity):
    def __init__(self, player, map, health_amount=10, position=None):
        if position is None:
            position = (ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2)
        super().__init__(player, map, position=position, size=30)
        self.health_amount = health_amount
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
        super().__init__(player, map, size=HEALTH_PICKUP_SIZE, position=position)
       
        self.value = value
        if self.value is None:
            self.value = random.choice([1, 5, 10])
        if self.value == 1:
            self.color = (168, 88, 50)
        elif self.value == 5:
            self.color = (120, 125, 130)
        else:
            self.color = (196, 201, 207)
        self.images = []
        self.images.append(utils.get_sprite(resources.objects, (0, 64), 16, 16, 2))
        self.images.append(utils.get_sprite(resources.objects, (16, 64), 16, 16, 2))
        self.images.append(utils.get_sprite(resources.objects, (32, 64), 16, 16, 2))
        self.image_frame = 0
        self.image = self.images[self.image_frame]
        self.frame_count = 0
    

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.money += self.value

    def update(self):
        super().update()
        if self.frame_count % 8 == 0:
            self.image_frame += 1
            if self.image_frame > 2:
                self.image_frame = 0
            self.image = self.images[self.image_frame]
        self.frame_count += 1
        if self.frame_count > 1000000:
            self.frame_count = 0


    
    


class EnergyPickup(Entity):
    def __init__(self, player, map, energy_amount=10, position=None):
        super().__init__(player, map, position=position, size=HEALTH_PICKUP_SIZE)
        self.energy_amount = energy_amount
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
    def __init__(self, player, map, position=None, item=None):
        super().__init__(player, map, position=position, size=30)
        self.state = "closed"
        self.color = (110, 110, 80)
        self.block_rect = self.rect.inflate(10, 10)
        if item is None:
            self.treasure = Coin(self.player, self.map, value=5)
        else:
            self.treasure = item

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
            and self.map.get_enemies_remaining() == 0 and self.state != 'open'
        ):
            self.state = "open"
            if isinstance(self.treasure, weapon.Weapon):
                self.player.weapons.append(self.treasure)
            elif isinstance(self.treasure, Entity):
                self.map.add_entity(self.treasure)

class Key(Entity):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, position=position, size=HEALTH_PICKUP_SIZE)
        self.image = pygame.transform.scale(
            resources.key, (self.rect.width, self.rect.height)
        )

    def collide(self):
        if self.state != "dead":
            if self.rect.colliderect(self.player.rect):
                self.state = "dead"
                self.player.keys += 1
