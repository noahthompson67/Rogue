import time

import colors as c
import config
import resources
from map_generator import MapGenerator
import pygame
from pygame import Rect
import sys
from player import Player
from colors import WHITE, BLACK
import cProfile
import random
import config_files.screen_size as ss

# Initialize Pygame


class MainTask:
    def __init__(self):
        pygame.init()
        # Set up display
        display_info = pygame.display.Info()
        ss.SCREEN_WIDTH = display_info.current_w  # Current screen width
        ss.SCREEN_HEIGHT = display_info.current_h
        ss.PAUSE_HEIGHT = ss.SCREEN_HEIGHT * 0.5
        ss.HUD_HEIGHT = ss.SCREEN_HEIGHT * 0.15
        self.screen = self.screen = pygame.display.set_mode(
            (ss.SCREEN_WIDTH, ss.SCREEN_HEIGHT), pygame.NOFRAME
        )
        self.warp_timeout = 0
        self.player = Player()
        self.init_hud()
        self.time_of_day = 0
        self.time_last_update = 0
        self.fullscreen = False
        self.map_generator = MapGenerator(self.screen, self.player, "void")
        self.map = self.map_generator.get_current_map()
        self.light_sources = []
        self.light_sources.append((self.player.x_pos, self.player.y_pos, 75, False))
        self.player_rect = Rect(
            self.player.y_pos, self.player.x_pos, self.player.radius, self.player.radius
        )
        self.console_state = False
        self.console_command = ""
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.console_rect = Rect(10, ss.SCREEN_HEIGHT - 75, ss.SCREEN_WIDTH - 15, 40)

        self.flicker_time = 0
        self.console_right_end_image = resources.console_right
        self.console_left_end_image = resources.console_left
        self.console_mid_image = resources.console_mid

        self.hud_left_image = resources.hud_left
        self.hud_mid_image = resources.hud_mid
        self.hud_right_image = resources.hud_right

        self.hud_left = Rect(0, 0, ss.SCREEN_WIDTH * 0.01, ss.HUD_HEIGHT)
        self.hud_mid = Rect(0, 0, ss.SCREEN_WIDTH, ss.HUD_HEIGHT)
        self.hud_right = Rect(
            ss.SCREEN_WIDTH * 0.99, 0, ss.SCREEN_WIDTH * 0.01, ss.HUD_HEIGHT
        )

        self.console_right_end = Rect(
            ss.SCREEN_WIDTH * 0.95,
            ss.SCREEN_HEIGHT * 0.9,
            ss.SCREEN_WIDTH * 0.01,
            ss.SCREEN_HEIGHT * 0.05,
        )
        self.console_left_end = Rect(
            0, ss.SCREEN_HEIGHT * 0.9, ss.SCREEN_WIDTH * 0.01, ss.SCREEN_HEIGHT * 0.05
        )
        self.console_mid = Rect(
            self.console_left_end.width,
            ss.SCREEN_HEIGHT * 0.9,
            ss.SCREEN_WIDTH * 0.95 - self.console_right_end.width,
            ss.SCREEN_HEIGHT * 0.05,
        )

        self.console_right_end_image = pygame.transform.scale(
            self.console_right_end_image,
            (self.console_right_end.width, self.console_right_end.height),
        )
        self.console_left_end_image = pygame.transform.scale(
            self.console_left_end_image,
            (self.console_left_end.width, self.console_left_end.height),
        )
        self.console_mid_image = pygame.transform.scale(
            self.console_mid_image, (self.console_mid.width, self.console_mid.height)
        )

        self.hud_right_end_image = pygame.transform.scale(
            self.hud_right_image, (self.hud_right.width, self.hud_right.height)
        )
        self.hud_mid_image = pygame.transform.scale(
            self.hud_mid_image, (self.hud_mid.width, self.hud_mid.height)
        )
        self.hud_left_end_image = pygame.transform.scale(
            self.hud_left_image, (self.hud_left.width, self.hud_left.height)
        )

        self.console_rect_inner = Rect(
            15, ss.SCREEN_HEIGHT - 70, ss.SCREEN_WIDTH - 25, 40
        )
        self.console_text_rect = Rect(
            20,
            ss.SCREEN_HEIGHT * 0.9 + self.console_mid.height * 0.3,
            ss.SCREEN_WIDTH - 30,
            30,
        )

        self.pause_rect_outer = Rect(
            ss.SCREEN_WIDTH * 0.75,
            ss.SCREEN_HEIGHT * 0.05,
            ss.SCREEN_WIDTH * 0.15,
            ss.PAUSE_HEIGHT,
        )
        self.pause_rect_inner = Rect(
            ss.SCREEN_WIDTH * 0.75 + 5,
            ss.SCREEN_HEIGHT * 0.05 + 5,
            ss.SCREEN_WIDTH * 0.15 - 10,
            ss.PAUSE_HEIGHT - 10,
        )

        self.option_rects = []
        self.light_source_counter = 0
        self.cached_radii = {}

        for i in range(len(config.OPTIONS)):
            option_rect = Rect(
                ss.SCREEN_WIDTH * 0.75 + 15,
                ss.SCREEN_HEIGHT * 0.05
                + 15
                + (ss.PAUSE_HEIGHT / len(config.OPTIONS) * i),
                ss.SCREEN_WIDTH * 0.15 - 10,
                20,
            )
            self.option_rects.append((option_rect, config.OPTIONS[i]))
        self.enemies = self.map.get_entities()
        self.paused = False
        for entity in self.map.get_entities():
            if entity.light_source:
                self.light_sources.append(
                    (
                        entity.rect.centerx,
                        entity.rect.centery,
                        entity.flicker_radius,
                        entity.flicker,
                    )
                )

    # Main loop

    def run(self):
        loop_iterations = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.player.console_state:
                    if event.type == pygame.KEYDOWN:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_RETURN]:
                            if self.player.console_state:
                                self.command(self.console_command.lower())
                                self.console_command = ""
                        elif keys[pygame.K_BACKSPACE]:
                            self.console_command = self.console_command[:-1]
                        else:
                            self.console_command += event.unicode
                else:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_f]:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode(
                                (ss.SCREEN_WIDTH, ss.SCREEN_HEIGHT), pygame.FULLSCREEN
                            )
                        else:
                            self.screen = pygame.display.set_mode(
                                (ss.SCREEN_WIDTH, ss.SCREEN_HEIGHT)
                            )
            self.update_time()
            self.screen.fill(c.BIOME_BACKGROUND_COLORS[self.map_generator.biome.name])

            self.player.update()
            self.light_sources[0] = (self.player.x_pos, self.player.y_pos, 75, False)
            self.map.draw_map(self.screen)
            self.map_generator.draw_minimap(self.screen)

            update_entity = (not self.player.paused and not self.player.console_state)
            for entity in self.enemies:
                if update_entity:
                    entity.update()
                    entity.collide()
                    entity.interact(self.screen)
                entity.draw(self.screen)
            self.player.draw(self.screen)

            if self.player.console_state:
                self.screen.blit(
                    self.console_right_end_image, self.console_right_end
                )
                self.screen.blit(self.console_left_end_image, self.console_left_end)
                self.screen.blit(self.console_mid_image, self.console_mid)
                command = self.font.render(
                    self.console_command, True, BLACK, c.CONSOLE_BACKGROUND
                )
                self.screen.blit(command, self.console_text_rect)
            elif self.player.paused:
                pygame.draw.rect(self.screen, BLACK, self.pause_rect_outer)
                pygame.draw.rect(self.screen, WHITE, self.pause_rect_inner)
                for options in self.option_rects:
                    font = pygame.font.Font("freesansbold.ttf", 12)
                    op = font.render(options[1], True, BLACK, WHITE)
                    self.screen.blit(op, options[0])
            self.enemies = self.map.get_entities()
            self.player_rect = self.player.rect
            if loop_iterations % 100 == 0:
                self.map_generator.remove_dead_entities()
            t = self.player_rect.collidelist(self.map_generator.current_map.warps)
            if t >= 0:
                self.warp(t)
                pygame.display.set_caption(str(self.map.name))
            loop_iterations += 1

            pygame.time.Clock().tick(60)

            self.draw_dimmer_overlay()
            self.draw_light_sources()
            self.draw_hud(self.screen)
            pygame.display.flip()

    def warp(self, num):
        self.warp_timeout = time.time()
        self.map_generator.warp(self.player_rect, num)
        self.map = self.map_generator.get_current_map()
        self.light_sources = self.light_sources[:1]
        for entity in self.map.get_entities():
            if entity.light_source:
                self.light_sources.append(
                    (
                        entity.rect.centerx,
                        entity.rect.centery,
                        entity.flicker_radius,
                        entity.flicker,
                    )
                )
        self.enemies = self.map.get_entities()

    def draw_background(self):
        self.screen.blit(self.background_image, self.background_rect)

    def command(self, command):
        try:
            cmd = command.split(" ")
            if cmd[0] == "spawn":
                try:
                    if cmd[1] == 'all':
                        for mob in config.mob_registry:
                            print(mob)
                            to_add = config.mob_registry.get(mob)(self.player, self.map)
                            self.map_generator.current_map.add_entity(to_add)
                    else:
                        mob = config.mob_registry.get(cmd[1])
                        if len(cmd) > 2:
                            spawn_count = int(cmd[2])
                        else:
                            spawn_count = 1
                        for _ in range(spawn_count):
                            to_add = mob(self.player, self.map)
                            self.map_generator.current_map.add_entity(to_add)
                except UnicodeError as e:
                    print(f"No entity of type {cmd[1]}")
                    print(e)
            elif cmd[0] == "health":
                self.player.update_health(int(cmd[1]))
                self.player.visible = True
            elif cmd[0] == "xp":
                self.player.update_xp(int(cmd[1]))
            elif cmd[0] == "killall":
                if len(cmd) > 1 and cmd[1] == "drops":
                    for entity in self.map.get_entities():
                        entity.update_health_override(-999)
                else:
                    self.map_generator.current_map.set_entities([])
                    self.map_generator.current_map.remove_dead_entities()
            elif cmd[0] == "warp":
                self.map_generator.warp_command(int(cmd[1]), int(cmd[2]))
                self.map = self.map_generator.get_current_map()
                self.enemies = self.map.get_entities()
            elif cmd[0] == "money":
                self.player.money += int(cmd[1])
            elif cmd[0] == "invincible":
                self.player.invincible = True
            elif cmd[0] == "fullmap":
                self.map_generator.set_full_minimap()
            elif cmd[0] == "status":
                self.player.add_status(cmd[1], int(cmd[2]))
            elif cmd[0] == "exit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif cmd[0] == "time":
                self.time_of_day += int(cmd[1])
            elif cmd[0] == "fullheal":
                self.player.health = self.player.health_max
                self.player.status = []
            elif cmd[0] == "speed":
                self.player.speed = int(cmd[1])
            elif cmd[0] == "biome":
                self.map.entities = []
                self.map_generator = MapGenerator(self.screen, self.player, cmd[1])
            elif cmd[0] == "weapon":
                if cmd[1] == "all":
                    for weapon_name in config.weapon_registry:
                        wep = config.weapon_registry.get(weapon_name)(self.player, weapon_name)
                        self.player.weapons.append(wep)
                else:
                    weapon = config.weapon_registry.get(cmd[1])
                    wep = weapon(self.player, cmd[1])
                    self.player.weapons.append(wep)

            else:
                print(f"unknown command: {cmd}")
        except UnicodeError as e:
            print(e)
        except IndexError as e:
            print(f"Incorrect usage of a valid command: {e}")
        except TypeError as e:
            print(e)

    def update_time(self):
        if (
            pygame.time.get_ticks() - self.time_last_update
            > config.TIME_UPDATE_INTERVAL
        ):
            self.time_of_day = (self.time_of_day + 1) % config.MAX_TIME
            self.time_last_update = pygame.time.get_ticks()

    def time_to_string(self):
        hours = int(self.time_of_day / 60)
        minutes = self.time_of_day % 60
        return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}"

    def draw_dimmer_overlay(self):
        if self.map_generator.biome_name == "cave":
            dim_alpha = 220
        elif self.time_of_day < config.MAX_TIME // 2:  # daytime
            dim_alpha = 0
        else:  # nighttime
            progress = (self.time_of_day - config.MAX_TIME // 2) / (
                config.MAX_TIME // 2
            )
            dim_alpha = int(220 * progress)
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, dim_alpha))
        self.screen.blit(overlay, (0, 0))

    def init_hud(self):
        x = config.X_HUD_OFFSET
        y = config.Y_HUD_OFFSET

        self.hud_background = Rect(x, y, ss.SCREEN_WIDTH - 10, ss.HUD_HEIGHT - 10)
        self.hud_background_border = Rect(0, 0, ss.SCREEN_WIDTH, ss.HUD_HEIGHT)
        self.outer_health_bar = Rect(x, y, 100, 20)
        self.inner_health_bar = Rect(x + 2, y + 2, 95, 15)
        self.outer_xp_bar = Rect(x, y + 25, 85, 20)
        self.inner_xp_bar = Rect(x + 2, y + 27, 80, 15)
        self.outer_energy_bar = Rect(x, y + 50, 85, 20)
        self.inner_energy_bar = Rect(x + 2, y + 52, 80, 15)
        self.money_text_rect = Rect(x + 110, y, 0, 0)
        self.level_text_rect = Rect(x + 110, y + 25, 0, 0)
        self.time_text_rect = Rect(x + 110, y + 50, 0, 0)
        self.key_text_rect = Rect(x + 150, y, 0, 0)

        self.location_text_rect = Rect(
            ss.SCREEN_WIDTH * 0.95, ss.HUD_HEIGHT * 0.85, 0, 0
        )
        self.money_icon = Rect(x + 120, y, 10, 10)
        self.status_icons = []
        self.weapon_icons = []
        self.weapon_selection_rect = Rect(x + 200, y + 75, 50, 50)
        for i in range(10):
            status_rect = Rect(x + i * 50, y + 75, 50, 50)
            self.status_icons.append(status_rect)
        for i in range(10):
            weapon_rect = Rect(x + 250 + (i * 50), y + 75, 25, 25)
            self.weapon_icons.append(weapon_rect)

        self.poison_icon_image = pygame.image.load(
            "assets/poison_icon.png"
        ).convert_alpha()
        self.poison_icon_image = pygame.transform.scale(
            self.poison_icon_image,
            (self.status_icons[0].width, self.status_icons[0].height),
        )
        self.fire_icon_image = pygame.image.load("assets/fire_icon.png").convert_alpha()
        self.fire_icon_image = pygame.transform.scale(
            self.fire_icon_image,
            (self.status_icons[0].width, self.status_icons[0].height),
        )
        self.confusion_icon_image = pygame.image.load(
            "assets/confusion_icon.png"
        ).convert_alpha()
        self.confusion_icon_image = pygame.transform.scale(
            self.confusion_icon_image,
            (self.status_icons[0].width, self.status_icons[0].height),
        )
        self.key_image = pygame.transform.scale(resources.key, (30, 30))

    def draw_hud(self, screen):
        screen.blit(self.hud_mid_image, self.hud_mid)
        screen.blit(self.hud_left_end_image, self.hud_left)
        screen.blit(self.hud_right_end_image, self.hud_right)
        # HEALTH BAR
        pygame.draw.rect(screen, BLACK, self.outer_health_bar)
        pygame.draw.rect(screen, WHITE, self.inner_health_bar)
        pygame.draw.rect(
            screen,
            c.RED,
            Rect(
                config.X_HUD_OFFSET + 2,
                config.Y_HUD_OFFSET + 2,
                (self.player.health / self.player.health_max) * 95,
                self.inner_health_bar.height,
            ),
        )

        # XP BAR
        pygame.draw.rect(screen, BLACK, self.outer_xp_bar)
        pygame.draw.rect(screen, WHITE, self.inner_xp_bar)
        pygame.draw.rect(
            screen,
            c.GREEN,
            Rect(
                config.X_HUD_OFFSET + 2,
                config.Y_HUD_OFFSET + 27,
                (self.player.XP / self.player.XP_max) * 80,
                15,
            ),
        )

        # ENERGY BAR
        pygame.draw.rect(screen, BLACK, self.outer_energy_bar)
        pygame.draw.rect(screen, WHITE, self.inner_energy_bar)
        pygame.draw.rect(
            screen,
            c.ENERGY,
            Rect(
                config.X_HUD_OFFSET + 2,
                config.Y_HUD_OFFSET + 52,
                (self.player.energy / self.player.energy_max) * 80,
                15,
            ),
        )

        font = pygame.font.Font("freesansbold.ttf", 20)
        level_text = font.render(
            str(self.player.level), True, BLACK, c.CONSOLE_BACKGROUND
        )
        money_text = font.render(
            str(self.player.money) + "¢", True, BLACK, c.CONSOLE_BACKGROUND
        )
        location_text = font.render(
            str(self.map.location), True, BLACK, c.CONSOLE_BACKGROUND
        )
        keys_text = font.render(
            str(self.player.keys), True, BLACK, c.CONSOLE_BACKGROUND
        )
        pygame.draw.rect(screen, c.GOLD, self.money_icon, 15, 15, 15, 15)
        time_text = font.render(
            self.time_to_string(), True, BLACK, c.CONSOLE_BACKGROUND
        )
        if len(self.player.status) > 0:
            status_icon_idx = 0
            current_statuses = [sublist[0] for sublist in self.player.status]
            if "poison" in current_statuses:
                screen.blit(self.poison_icon_image, self.status_icons[status_icon_idx])
                status_icon_idx += 1
            if "confusion" in current_statuses:
                screen.blit(
                    self.confusion_icon_image, self.status_icons[status_icon_idx]
                )
                status_icon_idx += 1
            if "fire" in current_statuses:
                screen.blit(self.fire_icon_image, self.status_icons[status_icon_idx])
                status_icon_idx += 1
            if "slow" in current_statuses:
                pygame.draw.rect(
                    screen, c.SLOW_ICON, self.status_icons[status_icon_idx]
                )
                status_icon_idx += 1
            if "sleep" in current_statuses:
                pygame.draw.rect(
                    screen, c.SLOW_ICON, self.status_icons[status_icon_idx]
                )
                status_icon_idx += 1
        for i in range(len(self.player.weapons)):
            if self.player.weapon_idx == i:
                pygame.draw.rect(self.screen, c.BLACK, self.weapon_icons[i].inflate(5,5))
            pygame.draw.rect(self.screen, self.player.weapons[i].color, self.weapon_icons[i])

        screen.blit(level_text, self.level_text_rect)
        screen.blit(money_text, self.money_text_rect)
        screen.blit(time_text, self.time_text_rect)
        screen.blit(location_text, self.location_text_rect)
        screen.blit(keys_text, self.key_text_rect)

        self.map_generator.draw_minimap(self.screen)

    def generate_light_source(self, radius, color=(100, 100, 80)):
        light = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            alpha = int(255 * (r / radius) ** 0.5)
            pygame.draw.circle(light, (*color, alpha), (radius, radius), r)
        return light

    import random

    def draw_light_sources(self):
        if (
            self.time_of_day < config.MAX_TIME // 2
            and self.map_generator.biome_name != "cave"
        ):  # daytime
            return

        self.light_source_counter += 1

        for i, (x, y, radius, flickers) in enumerate(self.light_sources):
            if i not in self.cached_radii:
                self.cached_radii[i] = max(1, int(radius))
            if (
                self.light_source_counter % 5 == 0 or i not in self.cached_radii
            ) and flickers:
                flicker = random.uniform(-radius * 0.05, radius * 0.05)
                self.cached_radii[i] = max(1, int(radius + flicker))

            flickering_radius = self.cached_radii[i]
            light = self.generate_light_source(flickering_radius)
            self.screen.blit(
                light,
                (x - flickering_radius, y - flickering_radius),
                special_flags=pygame.BLEND_RGBA_ADD,
            )


task = MainTask()
cProfile.run("task.run()", "assets/profile_results.prof")
