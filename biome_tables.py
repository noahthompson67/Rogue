import random

import config_files.screen_size as ss
from environment_objects import Rock, Fire
from enemies import MobGenerator, Bat


def generate_random_cave_map(map, player):
    rock_wall_count = random.randrange(4,10)
    for _ in range(rock_wall_count):
        first_rock = Rock(player, map)
        first_rock_pos = first_rock.rect.center
        rock_spawn_count = random.randrange(10, 20)
        vertical_wall = random.choice([True, False])
        for i in range(rock_spawn_count):
            rock = Rock(player, map)
            if vertical_wall:
                rock.rect.center = (first_rock_pos[0], first_rock_pos[1] + i * 30)

            else:
                rock.rect.center = (first_rock_pos[0] + i * 30, first_rock_pos[1])
            rock.health = random.randrange(1, 5)
            rock.block_rect.center = rock.rect.center
            rock.drops = []
            map.add_entity(rock)
    map.add_entity(MobGenerator(player, map, Bat, 10000))


def generate_cave_map(map, player):
    n = map.north_map is not None
    s = map.south_map is not None
    e = map.east_map is not None
    w = map.west_map is not None
    if n and s and not e and not w:
        map.entities = []
        left_rock_pos = (ss.SCREEN_WIDTH / 2 - ss.PLAYER_SIZE * 2, ss.PLAYER_SIZE)
        right_rock_pos = (ss.SCREEN_WIDTH / 2 + ss.PLAYER_SIZE * 2, ss.PLAYER_SIZE)
        for i in range(25):
            left_rock = Rock(player, map)
            right_rock = Rock(player, map)

            left_rock.rect.center = (left_rock_pos[0], left_rock_pos[1] + i * 30)
            right_rock.rect.center = (right_rock_pos[0], right_rock_pos[1] + i * 30)

            left_rock.block_rect.center = left_rock.rect.center
            right_rock.block_rect.center = right_rock.rect.center
            left_rock.drops = []
            right_rock.drops = []
            map.add_entity(left_rock)
            map.add_entity(right_rock)
        map.add_entity(MobGenerator(player, map, Bat, 10000))
        left_fire = Fire(player, map)
        right_fire = Fire(player, map)
        left_fire.rect.center = (ss.SCREEN_WIDTH / 4, ss.SCREEN_HEIGHT / 2)
        right_fire.rect.center = (ss.SCREEN_WIDTH * 0.75, ss.SCREEN_HEIGHT / 2)

        map.add_entity(left_fire)
        map.add_entity(right_fire)

    else:
        generate_random_cave_map(map, player)


def generate_boss_cave_map(map, player):
    map.entities = []