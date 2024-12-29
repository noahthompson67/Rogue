



class Biome:
    def __new__(cls, player, name, *args, **kwargs):
        if name == "cave":
            from biome_map_generators.cave import CaveBiome
            print('generated a cave')
            return super().__new__(CaveBiome)
        elif name == "forest":
            from forest import ForestBiome
            return super().__new__(ForestBiome)
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
