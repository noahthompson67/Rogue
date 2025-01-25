
from biome_map_generators.biome import Biome


class VoidBiome(Biome):
    def __init__(self, player, *args, **kwargs):
        super().__init__( player, "void", *args, **kwargs)



