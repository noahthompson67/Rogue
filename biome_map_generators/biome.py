



class Biome:
    def __new__(cls, player, name, *args, **kwargs):
        if name == "cave":
            from biome_map_generators.cave import CaveBiome
            return super().__new__(CaveBiome)
        elif name == "forest":
            from biome_map_generators.forest import ForestBiome
            return super().__new__(ForestBiome)
        elif name == "void":
            from biome_map_generators.void import VoidBiome
            return super().__new__(VoidBiome)
        elif name == "graveyard":
            from biome_map_generators.graveyard import GraveyardBiome
            return super().__new__(GraveyardBiome)
        return super().__new__(cls)

    def __init__(self, player, name, *args, **kwargs):
        self.name = name
        self.player = player

    def generate_random_map(self, map):
        pass

    def generate_boss_map(self, map):
        pass

    def generate_map(self, *args, **kwargs):
        print('override generate_map')
        pass

    def generate_boss_entrance(self, *args, **kwargs):
        print('override generate_boss_entrance')

    def generate_challenge_room(self, *args, **kwargs):
        print('override generate_challenge_room')

    def generate_settlement(self, *args, **kwargs):
        print('override generate_settlement')
