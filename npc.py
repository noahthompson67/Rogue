import pygame.draw
from entity import Entity
from pygame import Rect
import colors as c
import random
import config_files.screen_size as ss

class NPC(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.size = 30
        self.x_pos = random.randrange(
            int(self.size * 1.5), ss.SCREEN_WIDTH - int(self.size * 1.5)
        )
        self.y_pos = random.randrange(
            int(self.size * 1.5), ss.SCREEN_HEIGHT - int(self.size * 1.5)
        )

        self.rect = Rect(self.x_pos, self.y_pos, self.size, self.size)
        self.set_random_position()
        self.action_rect = Rect(0, 0, self.size * 4, self.size * 4)
        self.action_rect.center = self.rect.center
        self.default_color = c.GREEN
        self.color = c.GREEN
        self.state = "alive"
        self.active = False
        self.message_index = 0

        self.message_text = []
        self.generate_random_message()
        self.visible = True
        self.message_visible = False

        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.console_rect = Rect(
            0, ss.SCREEN_HEIGHT - 75, ss.SCREEN_WIDTH - 10, 50
        )
        self.console_rect_inner = Rect(
            5, ss.SCREEN_HEIGHT - 70, ss.SCREEN_WIDTH - 20, 40
        )
        self.console_text_rect = Rect(
            10, ss.SCREEN_HEIGHT - 65, ss.SCREEN_WIDTH - 25, 30
        )

    def update(self):
        if not self.action_rect.colliderect(self.player.rect):
            self.active = False
            self.message_index = 0

    def draw(self, screen):
        pygame.draw.rect(screen, c.ZOMBIE_RED, self.action_rect)
        super().draw(screen)
        if self.active:
            self.message = self.font.render(
                self.message_text[self.message_index], True, c.BLACK, c.WHITE
            )
            pygame.draw.rect(screen, c.BLACK, self.console_rect)
            pygame.draw.rect(screen, c.WHITE, self.console_rect_inner)
            screen.blit(self.message, self.console_text_rect)

    def interact(self, screen):
        self.player.interacting = False
        if self.active:
            if self.message_index < len(self.message_text) - 1:
                self.message_index += 1
            else:
                self.message_index = 0
                self.active = False
        elif self.action_rect.colliderect(self.player.rect):
            self.active = True

    def generate_random_message(self):
        first_names = [
            "James",
            "John",
            "Robert",
            "Michael",
            "William",
            "David",
            "Richard",
            "Joseph",
            "Thomas",
            "Charles",
            "Christopher",
            "Daniel",
            "Matthew",
            "Anthony",
            "Mark",
            "Donald",
            "Steven",
            "Paul",
            "Andrew",
            "Joshua",
            "Kevin",
            "Brian",
            "George",
            "Edward",
            "Ronald",
            "Timothy",
            "Jason",
            "Jeffrey",
            "Ryan",
            "Jacob",
            "Gary",
            "Nicholas",
            "Eric",
            "Jonathan",
            "Stephen",
            "Larry",
            "Justin",
            "Scott",
            "Brandon",
            "Benjamin",
            "Samuel",
            "Frank",
            "Gregory",
            "Raymond",
            "Alexander",
            "Patrick",
            "Jack",
            "Dennis",
            "Jerry",
            "Tyler",
            "Aaron",
            "Jose",
            "Adam",
            "Henry",
            "Nathan",
            "Douglas",
            "Zachary",
            "Peter",
            "Kyle",
            "Walter",
            "Ethan",
            "Jeremy",
            "Harold",
            "Keith",
            "Christian",
            "Roger",
            "Noah",
            "Gerald",
            "Carl",
            "Terry",
            "Sean",
            "Austin",
            "Arthur",
            "Lawrence",
            "Jesse",
            "Dylan",
            "Bryan",
            "Joe",
            "Jordan",
            "Billy",
            "Bruce",
            "Albert",
            "Willie",
            "Gabriel",
            "Logan",
            "Alan",
            "Juan",
            "Wayne",
            "Ralph",
            "Roy",
            "Eugene",
            "Randy",
            "Vincent",
            "Russell",
            "Louis",
            "Philip",
            "Bobby",
            "Johnny",
            "Bradley",
            "Phillip",
        ]

        likes = [
            "oranges",
            "bears",
            "furniture",
            "money",
            "math",
            "cats",
            "magnets",
            "trains",
            "turtles",
        ]

        favorite_colors = [
            "blue",
            "red",
            "green",
            "millennial gray",
            "purple",
            "orange",
        ]

        first_name = first_names[random.randrange(0, len(first_names))]
        like = likes[random.randrange(0, len(likes))]
        favorite_color = favorite_colors[random.randrange(0, len(favorite_colors))]

        self.message_text = [
            f"Hi, I'm {first_name}.",
            f"My favorite color is {favorite_color}.",
            f"I like {like}.",
        ]


class Medic(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.interacted = False
        self.message_text = ["That looks like it hurts...", "Let me help you with that"]

    def interact(self, screen):
        if not self.interacted and self.message_index == 1:
            super().interact(screen)
            self.player.update_health(100)
            self.player.energy = self.player.energy_max
            self.interacted = True
            self.message_text = ["I've done all I can.", "Good luck."]
            self.message_index = 0
        else:
            super().interact(screen)


