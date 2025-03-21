from enemies import Zombie, Shooter, Ghost, Bat, BadRock, SpiritOrb, Slime
from environment_objects import Hole, Fire, Water, Grass, Rock, MushroomPatch, HotSpring, Bomb, Path, Crate, Spikes, DoorLockPlate
from boss import Telekinetic, Golem, Reaper
from npc import NPC, Merchant, DemonMerchant, Dog, Medic
from items import Coin, HealthPickup, EnergyPickup, TreasureChest, Key
import config_files.screen_size as ss


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
    "orb": SpiritOrb,
    "reaper": Reaper,
    "slime": Slime,
    "bomb": Bomb,
    "path": Path,
    "dog": Dog,
    "crate": Crate,
    "spikes": Spikes,
    "plate": DoorLockPlate
}


