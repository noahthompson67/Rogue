import random
from weapon import Weapon
import pygame
import pygame.time
from pygame import Rect

import config
from colors import BLUE, BLACK, GREEN, CLEAR_WHITE
import colors as c
import config_files.screen_size as ss

LEFT_IDLE = 0
RIGHT_IDLE = 1
UP_IDLE = 2
DOWN_IDLE = 3
DOWN_LEFT_STEP = 4
DOWN_RIGHT_STEP = 5


class Player:
    def __init__(self):
        self.speed = 5
        self.speed_modifier = 1
        self.radius = 1

        self.rect = Rect(0, 0, config.PLAYER_SIZE, config.PLAYER_SIZE)
        self.rect.center = ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2 + ss.HUD_HEIGHT / 2

        self.shield_hitbox = Rect(
            self.rect.centerx, self.rect.centery, config.PLAYER_SIZE, config.PLAYER_SIZE
        )
        self.shield_active = False
        self.invincible = False
        self.interacting = False
        self.default_color = c.BLUE
        self.color = BLUE
        self.color_duration = 0
        self.health = 10
        self.health_max = 10
        self.health_time = 0
        self.energy = 10
        self.energy_max = 10
        self.XP = 0
        self.XP_max = 5
        self.level = 1
        self.damage = 1
        self.last_direction = "S"
        self.visible = True
        self.frame_count = 0
        self.console_state = False
        self.interaction_time = 0
        self.money = 0
        self.paused = False
        self.pause_timeout = 0
        self.console_timeout = 0
        self.status = []
        self.blocked_directions = []
        self.default_controls = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        self.controls = self.default_controls
        self.weapons = []
        sword = Weapon(self)
        self.weapons.append(sword)
        self.weapon_idx = 0
        self.weapon = self.weapons[0]
        self.keys = 0
        self.weapon_switch_time = 0
        self.move_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

    def update(self):
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_SLASH]
            and pygame.time.get_ticks() - self.console_timeout > 120
        ):
            self.console_timeout = pygame.time.get_ticks()
            self.console_state = not self.console_state
        if keys[pygame.K_RETURN] and pygame.time.get_ticks() - self.pause_timeout > 120:
            self.pause_timeout = pygame.time.get_ticks()
            if self.console_state:
                self.console_state = False
            else:
                self.paused = not self.paused
        if self.shield_active and not keys[pygame.K_t]:
            self.shield_active = False
        if self.console_state or self.paused:
            return
        if (
            keys[pygame.K_SPACE]
            and pygame.time.get_ticks() - self.interaction_time > 250
        ):
            self.interaction_time = pygame.time.get_ticks()
            self.interacting = not self.interacting
        if self.health <= 0:
            return
        if self.status:
            self.handle_status()
        if keys[pygame.K_LSHIFT]:
            self.speed_modifier = 2
        else:
            self.speed_modifier = 1
        if keys[self.controls[0]] and "N" not in self.blocked_directions:  # Move up
            self.rect.centery -= self.speed * self.speed_modifier
            if not self.shield_active:
                self.last_direction = "N"
        if keys[self.controls[1]] and "S" not in self.blocked_directions:  # Move down
            self.rect.centery += self.speed * self.speed_modifier
            if not self.shield_active:
                self.last_direction = "S"
        if keys[self.controls[2]] and "W" not in self.blocked_directions:  # Move left
            self.rect.centerx -= self.speed * self.speed_modifier
            if not self.shield_active:
                self.last_direction = "W"
        if keys[self.controls[3]] and "E" not in self.blocked_directions:  # Move right
            self.rect.centerx += self.speed * self.speed_modifier
            if not self.shield_active:
                self.last_direction = "E"
        if keys[pygame.K_q]:
            self.switch_weapon(False)
        if keys[pygame.K_e]:
            self.switch_weapon(True)
        elif keys[pygame.K_z]:
            self.shield_active = True

        if self.color == c.RED and pygame.time.get_ticks() - self.health_time > 3:
            self.color = self.default_color
            self.color = self.default_color

        self.rect.centery = max(
            config.PLAYER_SIZE / 2 + ss.HUD_HEIGHT,
            min(ss.SCREEN_HEIGHT - config.PLAYER_SIZE, self.rect.centery),
        )
        self.rect.centerx = max(
            config.PLAYER_SIZE,
            min(ss.SCREEN_WIDTH - config.PLAYER_SIZE, self.rect.centerx),
        )
        self.frame_count += 1
        self.blocked_directions = []
        self.weapon.update()

    def draw(self, screen):
        self.handle_color()
        if self.visible:
            self.weapon.draw(screen)
            if self.shield_active:
                shield_width = (
                    config.PLAYER_SIZE
                    if self.last_direction in ["N", "S"]
                    else config.SHIELD_SIZE
                )
                shield_length = (
                    config.PLAYER_SIZE
                    if self.last_direction in ["E", "W"]
                    else config.SHIELD_SIZE
                )
                self.shield_hitbox.update(
                    self.rect.centerx + config.SHIElD_OFFSETS[self.last_direction][0],
                    self.rect.centery + config.SHIElD_OFFSETS[self.last_direction][1],
                    shield_width,
                    shield_length,
                )
                pygame.draw.rect(screen, GREEN, self.shield_hitbox)
        if self.health <= 0:
            font = pygame.font.Font("freesansbold.ttf", 20)
            death_text = font.render("RIP :(", True, BLACK, CLEAR_WHITE)
            death_text_rect = Rect(ss.SCREEN_WIDTH / 2, ss.SCREEN_HEIGHT / 2, 30, 30)
            screen.blit(death_text, death_text_rect)
        pygame.draw.rect(screen, self.color, self.rect)

    def update_energy(self, num):
        if self.energy + num < 0:
            return False
        else:
            self.energy += num
            return True

    def update_health(self, num, shield_override=False):
        if num > 0:
            self.health += num
        if num < 0:
            if self.invincible:
                return
            if pygame.time.get_ticks() - self.health_time > 3:
                if self.shield_active and not shield_override:
                    return
                self.health += num
                self.health_time = pygame.time.get_ticks()
                self.color = c.RED
        self.health = max(self.health, 0)
        self.health = min(self.health, self.health_max)
        if self.health <= 0:
            self.visible = False

    def update_xp(self, num):
        self.XP += num
        while self.XP >= self.XP_max:
            self.level += 1
            self.XP -= self.XP_max
            self.XP_max += 1
            self.health_max += 1
            self.health += 1

    def handle_status(self):
        for i in range(len(self.status)):
            if self.status[i][0] == "poison":
                if self.status[i][1] % 100 == 0:
                    if self.color_duration == 0:
                        self.set_color(c.POISON_ICON, 50)
                    self.health -= 1
            elif self.status[i][0] == "fire":
                if self.status[i][1] % 100 == 0:
                    if self.color_duration == 0:
                        self.set_color(c.FIRE_ICON, 50)
                    self.health -= 1
                    if random.random() < 0.25:
                        self.status[i][1] = -1
                if self.status[i][1] == 0:
                    self.status[i][1] = 599
            elif self.status[i][0] == "slow":
                pass
            elif self.status[i][0] == "sleep":
                if self.status[i][1] > 0:
                    self.blocked_directions = ["N", "S", "E", "W"]
                else:
                    self.blocked_directions = []
            elif self.status[i][0] == "confusion":
                if self.status[i][1] % 1000 == 0:
                    temp_controls = []
                    while len(temp_controls) < 4:
                        val = random.randrange(0, 4)
                        if self.default_controls[val] not in temp_controls:
                            temp_controls.append(self.default_controls[val])
                    self.controls = temp_controls
                if self.status[i][1] <= 0:
                    self.controls = self.default_controls
            self.status[i][1] -= 1
        self.status = [x for x in self.status if x[1] >= 0]

    def add_status(self, status, duration):
        for s in self.status:
            if s[0] == status:
                s[1] = duration - 1
                return
        self.status.append([status, duration])

    def set_color(self, color, duration):
        self.color = color
        self.color_duration = duration

    def handle_color(self):
        if self.color_duration > 0:
            self.color_duration -= 1
            if self.color_duration == 0:
                self.color = self.default_color

    def switch_weapon(self, forward):
        if pygame.time.get_ticks() - self.weapon_switch_time < 200 or self.weapon.active:
            return
        else:
            self.weapon_switch_time = pygame.time.get_ticks()
            if forward:
                if self.weapon_idx + 1 == len(self.weapons):
                    self.weapon_idx = 0
                else:
                    self.weapon_idx += 1
            else:
                if self.weapon_idx - 1 < 0:
                    self.weapon_idx = len(self.weapons) - 1
                else:
                    self.weapon_idx -= 1
            self.weapon = self.weapons[self.weapon_idx]
    def key_up(self, key):
        self.weapon.key_up(key)
    def key_down(self, key):
        self.weapon.key_down(key)
