import random

import environment_objects
import npc
from environment_objects import Rock, Fire, Hole, MushroomPatch
from items import TreasureChest
from enemies import MobGenerator, Bat, Shooter
from boss import Golem
from pygame import Rect
import config_files.screen_size as ss
from biome_map_generators.biome import Biome


class VoidBiome(Biome):
    def __init__(self, player, *args, **kwargs):
        super().__init__( player, "void", *args, **kwargs)



