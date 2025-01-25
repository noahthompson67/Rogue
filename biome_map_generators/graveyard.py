
from enemies import Zombie, Ghost
from biome_map_generators.biome import Biome
class GraveyardBiome(Biome):
    def __init__(self, player, *args, **kwargs):
        super().__init__( player, "graveyard", *args, **kwargs)
        print('generating graveyard')

    def generate_map(self, map):
        for _ in range(10):
            map.add_entity(Zombie(self.player, map))
        for _ in range(5):
            map.add_entity(Ghost(self.player, map))


    def generate_boss_entrance(self, *args, **kwargs):
        print('override generate_boss_entrance')

    def generate_challenge_room(self, *args, **kwargs):
        print('override generate_challenge_room')

    def generate_settlement(self, *args, **kwargs):
        print('override generate_settlement')