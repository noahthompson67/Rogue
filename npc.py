import pygame.draw
from entity import Entity
from pygame import Rect
import colors as c
import random
import config_files.screen_size as ss
import resources
from weapon import CursedBlade


class NPC(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.size = 28
        x = random.randrange(
            int(self.size * 1.5), ss.SCREEN_WIDTH - int(self.size * 1.5)
        )
        y = random.randrange(
            int(self.size * 1.5), ss.SCREEN_HEIGHT - int(self.size * 1.5)
        )
        self.message_text = ["NPC message..."]
        self.rect = Rect(0, 0, self.size, self.size)
        self.rect.center = x, y
        self.set_random_position()
        self.action_rect = self.rect.inflate(50, 50)
        self.default_color = c.GREEN
        self.color = c.GREEN
        self.active = False
        self.message_index = 0
        self.prompt_cursor = Rect(0, 0, 30, 30)
        self.prompt_cursor_index = 0
        self.prompt = False
        self.prompt_text = None
        self.prompt_time = 0
        self.interactions = 0
        self.health = 1000
        self.prompt_options = ["yes", "no"]
        self.prompt_options_rects = []
        self.default_message_text = self.message_text
        self.visible = True
        self.inactive = False
        self.message_visible = False
        self.interact_time = 0
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.console_rect = Rect(0, ss.SCREEN_HEIGHT - 75, ss.SCREEN_WIDTH - 10, 50)
        self.console_rect_inner = Rect(
            5, ss.SCREEN_HEIGHT - 70, ss.SCREEN_WIDTH - 20, 40
        )
        self.console_text_rect = Rect(
            10, ss.SCREEN_HEIGHT - 65, ss.SCREEN_WIDTH - 25, 30
        )

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

    def set_pos(self, x, y):
        self.rect.center = x, y
        self.action_rect.center = x, y

    def update(self):
        if not self.action_rect.colliderect(self.player.rect):
            self.active = False
            self.message_index = 0
        if self.prompt and self.active:
            keys = pygame.key.get_pressed()
            if (
                keys[pygame.K_RIGHT]
                and pygame.time.get_ticks() - self.prompt_time > 250
            ):
                self.prompt_cursor_index += 1
                self.prompt_time = pygame.time.get_ticks()
                if self.prompt_cursor_index > len(self.prompt_options) - 1:
                    self.prompt_cursor_index = 0
                self.prompt_cursor.center = self.prompt_options_rects[
                    self.prompt_cursor_index
                ].center
            elif (
                keys[pygame.K_LEFT] and pygame.time.get_ticks() - self.prompt_time > 250
            ):
                self.prompt_time = pygame.time.get_ticks()
                self.prompt_cursor_index -= 1
                if self.prompt_cursor_index < 0:
                    self.prompt_cursor_index = len(self.prompt_options) - 1
                self.prompt_cursor.center = self.prompt_options_rects[
                    self.prompt_cursor_index
                ].center

    def draw(self, screen):
        pygame.draw.rect(screen, c.BLACK, self.rect.inflate(2,2))
        super().draw(screen)
        if self.active:
            if self.inactive:
                self.message = self.font.render(
                    self.inactive_text, True, c.BLACK, c.CONSOLE_BACKGROUND
                )
            else:
                self.message = self.font.render(
                    self.message_text[self.message_index],
                    True,
                    c.BLACK,
                    c.CONSOLE_BACKGROUND,
                )
            screen.blit(self.console_right_end_image, self.console_right_end)
            screen.blit(self.console_left_end_image, self.console_left_end)
            screen.blit(self.console_mid_image, self.console_mid)
            if self.prompt:
                self.prompt_font = self.font.render(
                    self.prompt_text, True, c.BLACK, c.CONSOLE_BACKGROUND
                )
                screen.blit(self.prompt_font, self.console_text_rect)
                for i in range(len(self.prompt_options)):
                    temp = self.font.render(
                        self.prompt_options[i], True, c.BLACK, c.CONSOLE_BACKGROUND
                    )
                    # Draw the text
                    screen.blit(temp, self.prompt_options_rects[i])

                    if i == self.prompt_cursor_index:
                        pygame.draw.rect(
                            screen,
                            c.BLACK,
                            self.prompt_options_rects[i].move(0, -5).inflate(15, 0),
                            width=3,
                        )
            else:
                screen.blit(self.message, self.console_text_rect)

    def interact(self, screen):
        if self.action_rect.colliderect(self.player.rect):
            keys = pygame.key.get_pressed()
            if (
                keys[pygame.K_SPACE]
                and pygame.time.get_ticks() - self.prompt_time > 800
            ):
                self.prompt_time = pygame.time.get_ticks()
                if self.interactions == 0:
                    self.active = True
                    self.interactions += 1
                elif self.message_index + 1 < len(self.message_text):
                    self.message_index += 1
                    self.interactions += 1
                elif not self.prompt and self.prompt_text is not None:
                    self.prompt = True
                elif self.prompt:
                    self.handle_prompt(self.prompt_options[self.prompt_cursor_index])
                else:
                    self.active = False
                    self.message_text = self.default_message_text
                    self.message_index = 0
        else:
            if self.message_index != 0 or self.active:
                self.message_index = 0
                self.active = False
                self.interactions = 0
                self.message_text = self.default_message_text

    def generate_prompt_option_rects(self):
        current_pos = (
            self.console_text_rect.right - ss.SCREEN_WIDTH * 0.30,
            self.console_text_rect.top,
        )
        for i in range(len(self.prompt_options)):
            self.prompt_options_rects.append(
                Rect(current_pos[0] + (i * 50), current_pos[1], 30, 30)
            )


class Medic(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.interactions = 0
        self.message_text = ["That looks like it hurts..."]
        self.default_message_text = self.message_text
        self.prompt_text = "Let me help you with that."
        self.inactive_text = "All patched up. That's all I can do."
        self.generate_prompt_option_rects()
        self.color = (150, 19, 12)

    def handle_prompt(self, response):
        if response == "no":
            self.prompt = False
            self.message_text.append("Suit yourself, hombre.")
            self.message_index = len(self.message_text) - 1
        elif response == "yes":
            self.prompt = False
            self.message_index = len(self.message_text) - 1
            self.inactive = True


class Merchant(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.interacted = False
        self.generate_prompt_option_rects()
        self.message_text = ["I found this rusty key on the ground."]
        self.default_message_text = self.message_text
        self.prompt_text = "I'll sell it to you for 25 cents."
        self.inactive_text = "Pleasure doing business with you"
        self.prompt_cursor.center = self.prompt_options_rects[0].center
        self.color = (222, 111, 20)

    def handle_prompt(self, response):
        if response == "no":
            self.prompt = False
            self.message_text.append("Suit yourself, hombre.")
            self.message_index = len(self.message_text) - 1
        elif response == "yes":
            if self.player.money >= 25:
                self.prompt = False
                self.player.money -= 25
                self.message_index = len(self.message_text) - 1
                self.player.keys += 1
                self.inactive = True
            else:
                self.prompt = False
                self.message_text.append("You don't have enough money.")
                self.message_index = len(self.message_text) - 1


class DemonMerchant(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.interacted = False
        self.color = (50, 50, 40)
        self.generate_prompt_option_rects()
        self.message_text = ["..."]
        self.cursed = random.random() < 0.1
        if self.cursed:
            self.prompt_text = "[Accept the cursed offering?]"
            self.inactive_text = "[You feel cursed]"
        else:
            self.prompt_text = "[Exchange life force for power?]"
            self.inactive_text = "[You feel stronger]"
        self.default_message_text = self.message_text
        self.prompt_cursor.center = self.prompt_options_rects[0].center

    def handle_prompt(self, response):
        if response == "no":
            self.prompt = False
            self.message_index = 0
        elif response == "yes":
            if self.cursed:
                weapon = CursedBlade(self.player, "Cursed Blade")
                self.player.weapons.append(weapon)
                self.player.health_max *= 0.5
                self.player.health = 1
            else:
                self.player.damage += 3
                self.player.health_max *= 0.5
                self.prompt = False
                self.message_index = len(self.message_text) - 1
                self.inactive = True
                self.state = "dead"

