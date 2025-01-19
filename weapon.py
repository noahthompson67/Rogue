import enemies
import environment_objects
import colors as c


class Weapon:
    def __init__(self, player, name):
        self.player = player
        self.damage = self.player.damage
        self.name = name
        self.color = c.GREEN

    def collide(self, entity):
        entity.update_health(-self.damage)
        # TODO: handle knockback


class Pickaxe(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = self.player.damage / 2
        self.color = (100, 100, 3)

    def collide(self, entity):
        if isinstance(entity, environment_objects.Rock) and self.player.energy > 0:
            entity.update_health(-100)
        elif isinstance(entity, enemies.Rock) and self.player.energy > 0:
            entity.update_health(-100)
        elif self.player.energy > 0:
            entity.update_health(-1)
        else:
            entity.update_health(0)
        self.player.energy -= 1
        self.player.energy = max(0, self.player.energy)


class CursedBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 1000
        self.color = (120, 0, 0)

    def collide(self, entity):
        super().collide(entity)
        self.player.health = min(self.player.health, 1)


class GhostBlade(Weapon):
    def __init__(self, player, name):
        super().__init__(player, name)
        self.damage = 0
        self.color = (120, 120, 120)

    def collide(self, entity):
        super().collide(entity)
        entity.update_health_override(-1)
        self.player.energy -= 1

