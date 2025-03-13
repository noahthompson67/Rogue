import pygame.locals
import config
import resources
import weapon
from entity import Entity
import random
import config_files.screen_size as ss
import pygame
import colors as c
from pygame import Rect
import math
import utils

ZOMBIE_SIZE = 50
ENEMY_HEALTH_TIMEOUT = 0.5
ZOMBIE_SPEED = 0.75

class Enemy:
    def __init__(self):
        pass


class Zombie(Entity, Enemy):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, size=30, position=None)
        self.health = 3
        self.default_color = c.ZOMBIE_RED
        self.color = self.default_color
        self.speed = 0.75
        self.action_rect = self.rect.inflate(ZOMBIE_SIZE * 5, ZOMBIE_SIZE * 5)
        self.sleeping = True

    def update(self):
        if self.sleeping:
            return
        self.move_towards_player()
        self.check_damage_timeout()
        super().update()

    def collide(self):
        if self.state != "dead":
            self.check_contact_damage(1)
            if self.action_rect.colliderect(self.player.rect):
                if self.sleeping:
                    self.sleeping = False
                    return
                self.speed = min(1.5, self.speed + 0.05)
            else:
                self.speed = max(ZOMBIE_SPEED, self.speed - 0.05)
            self.player.weapon.collide(self)

    def draw(self, screen):
        if not self.sleeping:
            super().draw(screen)


class Shooter(Entity, Enemy):
    def __init__(self, player, map, position=None, shot_target=None):
        super().__init__(player, map, position=position, size=50)
        self.last_shot_time = 0
        self.action_rect = self.rect.inflate(500, 500)
        self.color = c.SHOOTER_COLOR
        self.state = "undead"
        self.image = pygame.transform.scale(
            resources.gargoyle, (self.rect.width, self.rect.height)
        )
        self.shot = False
        self.shot_target = shot_target
        self.knockback = False
        self.block_rect = self.rect.inflate(10, 10)

    def update(self):
        self.block_path()
        if (
            pygame.time.get_ticks() - self.last_shot_time > 2000
            and self.map.is_active()
        ):
            self.shot = True
            to_add = Projectile(self.player, self.map, position=(self.rect.centerx, self.rect.centery), target_pos=self.shot_target)
            self.map.add_entity(to_add)
            self.last_shot_time = pygame.time.get_ticks()




class Projectile(Entity, Enemy):
    def __init__(self, player, map, position, target_pos=None):
        super().__init__(player, map, size=20, position=position)
        if target_pos is None:
            target_pos = player.rect.center
        
        self.speed = 5
        self.color = c.RED
        self.creation_time = pygame.time.get_ticks()
        self.direction_x = target_pos[0] - self.rect.centerx
        self.direction_y = target_pos[1] - self.rect.centery
        self.reflectable = False
        self.reflected = False
        distance = math.sqrt(self.direction_x**2 + self.direction_y**2)
        self.image = pygame.transform.scale(
            resources.projectile, (self.rect.width, self.rect.height)
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
                self.rect.colliderect(self.player.weapon.hitbox)
                and self.reflectable
                and self.player.weapon.active
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
                    target_x = self.rect.centerx
                    target_y = 0
                elif middle_x and not upper:
                    print(6)
                    target_x = self.rect.centerx
                    target_y = ss.SCREEN_HEIGHT
                elif middle_y and left:
                    print(9)
                    target_x = 0
                    target_y = self.rect.centery
                elif middle_y and not left:
                    print(3)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.rect.centery
                elif upper and left and not middle_y and not middle_x:
                    if -x > y:
                        print(10)
                    else:
                        print(11)
                    target_x = 0
                    target_y = self.rect.centery / self.rect.centerx
                elif not upper and left and not middle_y and not middle_x:
                    if x < y:
                        print(8)
                    else:
                        print(7)
                    target_x = 0
                    target_y = -self.rect.centerx * self.rect.centery
                elif upper and not left and not middle_y and not middle_x:
                    if x < y:
                        print(1)
                    else:
                        print(2)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.rect.centery/ self.rect.centerx
                elif not upper and not left and not middle_y and not middle_x:
                    if -x > y:
                        print(4)
                    else:
                        print(5)
                    target_x = ss.SCREEN_WIDTH
                    target_y = self.rect.centerx * self.rect.centery

                self.direction_x = target_x - self.rect.centerx
                self.direction_y = target_y - self.rect.centery
                distance = math.sqrt(self.direction_x**2 + self.direction_y**2)
                if distance != 0:
                    self.direction_x /= distance
                    self.direction_y /= distance

class BoomerangProjectile(Entity, Enemy):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, size=10, position=position)
        self.color = (100, 50, 30)
        center1, center2, radius = self.find_circle_center_and_radius(self.rect.center, player.rect.center)
        self.path = self.generate_circle_points(center2, radius, self.rect.center)
        self.arc_index = 0


    def update(self):
        if self.state != "dead":
            self.rect.center = self.path[self.arc_index]
            self.arc_index += 1
            if self.arc_index == len(self.path):
                self.state = "dead"



    def find_circle_center_and_radius(self, p1, p2):
        # Midpoint between p1 and p2
        midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

        # Distance between p1 and p2
        dist = math.dist(p1, p2)

        # We assume a default radius (r > dist/2)
        radius = dist / 2 + 5  # You can modify the offset to adjust circle size

        # Distance from midpoint to the circle center
        offset = math.sqrt(radius ** 2 - (dist / 2) ** 2)

        # Unit vector perpendicular to the line p1->p2
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        perp_unit = (-dy / dist, dx / dist)

        # Two possible circle centers
        center1 = (midpoint[0] + perp_unit[0] * offset, midpoint[1] + perp_unit[1] * offset)
        center2 = (midpoint[0] - perp_unit[0] * offset, midpoint[1] - perp_unit[1] * offset)

        return center1, center2, radius


    def angle_of_point(self, center, point):
        cx, cy = center
        px, py = point
        return math.atan2(py - cy, px - cx)


    def generate_circle_points(self, center, radius, start_point, num_points=100):
        cx, cy = center
        # Calculate the starting angle based on p1
        start_angle = self.angle_of_point(center, start_point)
        points = [
            (cx + radius * math.cos(start_angle + 2 * math.pi * t / num_points),
            cy + radius * math.sin(start_angle + 2 * math.pi * t / num_points))
            for t in range(num_points)
        ]
        return points


class Ghost(Entity, Enemy):
    def __init__(self, player, map):
        super().__init__(player, map, size=30)
        self.generate_nearby_location()
        self.health = 2
        self.default_color = c.GHOST_COLOR
        self.color = self.default_color
        self.speed = 0.75
        self.outline_color = tuple(x + 3 for x in c.BIOME_BACKGROUND_COLORS[self.map.biome.name])
        self.frame_count = random.randrange(0, 50)
        self.spritesheet = pygame.image.load("assets/ghost.png")
        self.frame_index = 0
        self.visible = True

    def update(self):
        self.handle_sprites(32, 1)
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
        if self.player.weapon.active and self.rect.colliderect(self.player.weapon.hitbox):
            if isinstance(self.player.weapon, weapon.GhostBlade):
                self.player.weapon.collide(self)






class Bat(Entity, Enemy):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, size=20, position=position)
        if position is None:
            self.generate_nearby_location()
        self.health = 1
        self.default_color = c.BLACK
        self.color = self.default_color
        self.speed = 1.75
        self.frame_count = random.randrange(0, 50)
        self.first_frame = True
        self.image = resources.bat_1
        self.image = pygame.transform.scale(
            self.image, (self.rect.width, self.rect.height)
        )

    def update(self):
        if self.state == "alive":
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
                self.image = pygame.transform.scale(
                    self.image, (self.rect.width, self.rect.height)
                )

        super().update()

    def collide(self):
        if self.state == "alive":
            if self.rect.colliderect(self.player.rect):
                self.player.update_health(-2)
                if random.random() < 0.75:
                    self.player.add_status("poison", random.randrange(1, 10) * 100)
            self.player.weapon.collide(self)

class MobGenerator(Entity, Enemy):
    def __init__(self, player, map, mob, freq, mob_count=-1):
        super().__init__(player, map)
        self.generate_nearby_location()
        self.mob_count = mob_count
        self.health = 1
        self.default_color = c.GOLD
        self.color = self.default_color
        self.spawn_time = pygame.time.get_ticks()
        self.mob = mob
        self.frequency = freq

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.frequency:
            to_add = self.mob(self.player, self.map)
            distance = (
                (self.player.rect.centerx - to_add.rect.centerx) ** 2
                + (self.player.rect.centery - to_add.rect.centery) ** 2
            ) ** 0.5
            while distance < 10:
                to_add = self.mob(self.player, self.map)
                distance = (
                    (self.player.rect.centerx - to_add.rect.centerx) ** 2
                    + (self.player.rect.centery - to_add.rect.centery) ** 2
                ) ** 0.5

            to_add.drops = []
            self.map.add_entity(to_add)
            self.mob_count -= 1
            if self.mob_count == 0:
                self.end()
            self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        pass


class BadRock(Entity, Enemy):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, size=50, position=position)
        self.health = 100
        self.action_rect = self.rect.inflate(250, 250)
        self.image = pygame.transform.scale(
            resources.rock, (self.rect.width, self.rect.height)
        )
        self.default_color = c.ZOMBIE_RED
        self.color = self.default_color
        self.speed = 0.75
        self.active = False

    def update(self):
        if self.health <= 0:
            if self.state == "alive":
                self.end()
            return
        if not self.active and self.rect.inflate(50, 50).colliderect(self.player.rect):
            self.active = True
        if self.active:
            self.move_towards_player()
        self.check_damage_timeout()

    def collide(self):
        if self.state != "dead":
            self.check_contact_damage(1)
            if self.action_rect.colliderect(self.player.rect):
                self.speed = min(1.5, self.speed + 0.05)
            else:
                self.speed = max(ZOMBIE_SPEED, self.speed - 0.05)
            self.player.weapon.collide(self)

class SpiritOrb(Entity):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, position=position)
        self.interacted = False
        self.path_index = 0
        self.health = 1
        self.reverse = False
        self.color = (215, 252, 253)
        self.light_source = True
        self.update_time = 0
        path_length = random.randrange(1000, 5000)
        self.spritesheet = pygame.image.load("assets/orb.png")
        self.frame_count = 0 
        self.frame_index = 0
        self.path = self.generate_loopy_path(length=path_length, step_range=(2, 10), loopiness=10, x_bounds=(50, ss.SCREEN_WIDTH*.95), y_bounds=(ss.HUD_HEIGHT+50, ss.SCREEN_HEIGHT*.95))
   
    def update(self):
        if pygame.time.get_ticks() - self.update_time > 10:
            self.update_time = pygame.time.get_ticks()
            if self.path_index == len(self.path)-1:
                self.reverse = True
            elif self.path_index == 0:
                self.reverse = False
            self.rect.center = self.path[self.path_index]
            if self.reverse:
                self.path_index -= 1
            else:
                self.path_index += 1
        self.frame_count += 1
        super().update()
        self.handle_sprites(16, 1)

    def collide(self):
        self.check_contact_damage(1)
        if self.player.weapon.active and self.rect.colliderect(self.player.weapon.hitbox):
            if isinstance(self.player.weapon, weapon.GhostBlade):
                self.player.weapon.collide(self)

class Slime(Entity):
    def __init__(self, player, map, position=None):
        super().__init__(player, map, position=position)
        self.color = (20, 100, 50)
        self.default_color = self.color
        self.speed = 5
        self.health = 3
        self.rect.width = 50
        self.rect.height = 50
        self.scale = 3
        self.drops = []
        self.spritesheet = pygame.image.load("assets/slime.png")

    def __set_size(self, size):
        self.rect.width = size
        self.rect.height = size
        self.scale /= 2
    
    def update(self):
        self.handle_sprites(16, self.scale)
        self.frame_count += 1
        if self.action == 'lunge':
            self.move_towards_player()
            self.lunge_frames -= 1
            if self.lunge_frames == 0:
                self.action = 'idle'
        else:
            if random.random() < .05:
                self.action = 'lunge'
                self.lunge_frames = 50
        self.check_damage_timeout()
        super().update()
        

    def end(self):
            if self.rect.width > 25:
                rects = []
                rects.append(Rect(self.rect.left, self.rect.top, 0, 0))
                rects.append(Rect(self.rect.right, self.rect.top, 0, 0))
                for rect in rects:
                    to_add = Slime(self.player, self.map)
                    to_add.rect = rect
                    to_add.__set_size(self.rect.width-5)
                    self.map.add_entity(to_add)
            super().end()

    def collide(self):
        if self.state != "dead":
            self.check_contact_damage(1)
            self.player.weapon.collide(self)