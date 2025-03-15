import pygame.draw
from entity import Entity
import colors as c
import random
from weapon import CursedBlade


class NPC(Entity):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.recipe = [
            {"message": "hello",
             "promptOptions": None,
             "optionHandlers": None,
             },
            {
                 "message": "Yes or no?",
                 "promptOptions": ["yes", "no"],
                 "optionHandlers": [self.accept_prompt, self.reject_prompt]
             },
             {
                 "message": "Goodbye",
                 "promptOptions": None,
                 "optionHandlers": None
             } 
        ]
        self.message_index = -1
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.active = False
        self.interaction_rect = self.rect.inflate(40,40)
        self.prompt_objects = []
        self.knockback = False
        self.prompt_selection = 0
        self.prompt_options = None

    def accept_prompt(self):
        print("Prompt accepted!")

    def reject_prompt(self):
        print("prompt rejected!")

    def draw(self, screen):
        if self.active:
            screen.blit(self.message_object, self.rect.move(0, 50))
            if len(self.prompt_objects) > 1:
                for i in range(len(self.prompt_objects)):
                    screen.blit(self.prompt_objects[i], self.rect.move(50 + 50*i, 100))
                    if self.prompt_selection == i:
                        pygame.draw.rect(screen, c.RED, self.rect.move(50 + 50*i, 120))
        pygame.draw.rect(screen, c.HOTSPRING, self.interaction_rect)
        pygame.draw.rect(screen, c.GREEN, self.rect.inflate(2,2))

    def interact(self):
        self.message_index += 1
        if self.message_index >= len(self.recipe):
            self.message_index = -1
            self.active = False
            print('empty')
            self.player.interacting = False
            return
        if self.prompt_options is None and self.recipe[self.message_index]["promptOptions"] is None:
            self.active = True
            self.player.interacting = True
            self.message_text = self.recipe[self.message_index]["message"]
            self.message_object = self.font.render(self.message_text, True, c.BLACK, c.CONSOLE_BACKGROUND)
        elif self.prompt_options is not None:
            self.recipe[self.message_index-1]["optionHandlers"][self.prompt_selection]()
            self.prompt_options = None
            self.prompt_objects = []
        else:
            self.prompt_options = self.recipe[self.message_index]["promptOptions"]
            self.prompt_objects = []
            for option in self.prompt_options:
                 self.prompt_objects.append(self.font.render(option, True, c.BLACK, c.CONSOLE_BACKGROUND))
        self.message_text = self.recipe[self.message_index]["message"]
        self.message_object = self.font.render(self.message_text, True, c.BLACK, c.CONSOLE_BACKGROUND)

    def update(self):
        if self.active and len(self.prompt_objects) > 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.prompt_selection -= 1
            elif keys[pygame.K_RIGHT]:
                self.prompt_selection += 1
            if self.prompt_selection < 0:
                self.prompt_selection = len(self.recipe[self.message_index]["promptOptions"]) - 1
            elif self.prompt_selection > len(self.recipe[self.message_index]["promptOptions"]) - 1:
                self.prompt_selection = 0



class Medic(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.recipe = [
            {"message": "That looks like it hurts...",
             "promptOptions": None,
             "optionHandlers": None,
             },
             {
                 "message": "Let me help you with that.",
                 "promptOptions": ["yes", "no"],
                 "optionHandlers": [self.accept_prompt, self.reject_prompt]
             },
             {
                 "message": "All patched up. That's all I can do.",
                 "promptOptions": None,
                 "optionHandlers": None
             }
        ]

    def accept_prompt(self):
        self.player.update_health(100)
        self.recipe = [
            {
                 "message": "All patched up. That's all I can do.",
                 "promptOptions": None,
                 "optionHandlers": None
             }
        ]
        self.message_index = -1


    def reject_prompt(self):
        self.recipe[2]["message"] = "Suit yourself, hombre"


class Merchant(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.recipe = [
            {"message": "I found this old key on the ground...",
             "promptOptions": None,
             "optionHandlers": None,
            },
             {
                 "message": "I'll sell it for 25 cents.",
                 "promptOptions": ["Yes [25 cents]", "No"],
                 "optionHandlers": [self.accept_prompt, self.reject_prompt]
             },
             {
                 "message": "No problem. Lemme know if you change your mind.",
                 "promptOptions": None,
                 "optionHandlers": None
             }
        ]
    
    def accept_prompt(self):
        if self.player.money >= 25:
            self.player.money -= 25
            self.player.keys += 1
            self.recipe = [
                {
                    "message": "Pleasure doing business with you.",
                    "promptOptions": None,
                    "optionHandlers": None
                }
            ]
            self.message_index = -1
        else:
            self.recipe[2]["message"] = "You don't have enough money, broke boi"

    def reject_prompt(self):
        pass

class DemonMerchant(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.cursed = random.random() < 0.1
        blade_name = "cursed" if self.cursed else "dark"
        self.recipe = [
            {"message": str(f"[The beast silently offers you a {blade_name} blade...]"),
                "promptOptions": None,
                "optionHandlers": None,
            },
            {
                "message": "[Accept the offering?]",
                "promptOptions": ["Yes", "No"],
                "optionHandlers": [self.accept_prompt, self.reject_prompt]
            },
            {
                "message": "",
                "promptOptions": None,
                "optionHandlers": None
            }
        ]
        self.accepted = False

    def interact(self):
        super().interact()
        if self.accepted:
            self.recipe = [
                {
                    "message": "...",
                    "promptOptions": None,
                    "optionHandlers": None
                }
            ]
        
    def accept_prompt(self):
        self.accepted = True
        if self.cursed:
            self.player.health_max *= 0.5
            self.player.health = 1
            self.player.weapons.append(CursedBlade(self.player, "Cursed Blade"))
            self.recipe = [
                {
                    "message": "[You feel cursed]",
                    "promptOptions": None,
                    "optionHandlers": None
                }
            ]
        else:
            self.player.damage += 3
            self.player.health_max *= 0.75
            self.recipe = [
                {
                    "message": "[You feel stronger]",
                    "promptOptions": None,
                    "optionHandlers": None
                }
            ]
        self.message_index = -1

    def reject_prompt(self):
        self.recipe[2]["message"] = "[The beast snorts in contempt]"


class Dog(NPC):
    def __init__(self, player, map):
        super().__init__(player, map)
        self.recipe = [
            {"message": "Woof!",
             "promptOptions": None,
             "optionHandlers": None,
             }
        ]
        self.tamed = True
        self.interaction_rect = self.rect.inflate(100, 100)
        self.bark_timer = 0
    
    def update(self):
        if not self.rect.inflate(200, 200).colliderect(self.player.rect):
            self.move_towards_player()
        if pygame.time.get_ticks() - self.bark_timer > 10000:
            for entity in self.map.get_entities():
                if entity.rect.colliderect(self.rect.inflate(200, 200)):
                    self.bark_timer = pygame.time.get_ticks()
                    entity.add_fear(100)

    def add_fear(self, frames, override=False):
        if override:
            return super().add_fear(frames)
                
