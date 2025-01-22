from enemies import Zombie, Shooter, Ghost, Bat, BadRock, SpiritOrb
from environment_objects import Hole, Fire, Water, Grass, Rock, MushroomPatch, HotSpring
from boss import Telekinetic, Golem
from npc import NPC, Medic, Merchant, DemonMerchant
from items import Coin, HealthPickup, EnergyPickup, TreasureChest, Key
import config_files.screen_size as ss
from weapon import Pickaxe, GhostBlade, CursedBlade, Laser


WARP_SIZE = 30
PLAYER_SIZE = 30
SHIELD_SIZE = 5

MAX_TIME = 1440
TIME_UPDATE_INTERVAL = 1500

X_HUD_OFFSET = 10
Y_HUD_OFFSET = 30

# MINIMAP CONSTANTS
MINIMAP_CELL_SIZE = ss.SCREEN_WIDTH / 110


SHIElD_OFFSETS = {"N": (0, 0), "S": (0, 30), "E": (0, 0), "W": (30, 0)}

OPTIONS = ["RESUME", "INVENTORY", "ACHIEVEMENTS", "SETTINGS", "EXIT"]
mob_registry = {
    "zombie": Zombie,
    "shooter": Shooter,
    "telekinetic": Telekinetic,
    "golem": Golem,
    "hole": Hole,
    "ghost": Ghost,
    "npc": NPC,
    "fire": Fire,
    "water": Water,
    "coin": Coin,
    "healthpickup": HealthPickup,
    "grass": Grass,
    "rock": Rock,
    "bat": Bat,
    "energy": EnergyPickup,
    "treasure": TreasureChest,
    "mushroom": MushroomPatch,
    "hotspring": HotSpring,
    "key": Key,
    "medic": Medic,
    "merchant": Merchant,
    "badrock": BadRock,
    "demonmerchant": DemonMerchant,
    "orb": SpiritOrb
}

weapon_registry = {
    "pickaxe": Pickaxe,
    "ghost": GhostBlade,
    "cursed": CursedBlade,
    "laser": Laser
}
