import Creature, Colors, Logger, ToastWrangler, World, Overlay, random, BaseItems, Item
#A few simple generic creatures to fight against.

def getGenericCreature():
    r = random.randint(0, 1)

    if (r == 0):
        return Bandito()
    return Outlaw()

class CreatureWithInventory(Creature.Creature):
    def __init__(self):
        Creature.Creature.__init__(self)
        self.noInventoryItem = BaseItems.Fists()
        self.inventory = []
        self.weapon = self.noInventoryItem

    def getHelpDescription(self):
        if (self.weapon == self.noInventoryItem):
            return Creature.Creature.getHelpDescription(self)
        else:
            return Creature.Creature.getHelpDescription(self) + ' carrying ' + self.weapon.getDescription()

    def addToInventory(self, item):
        Logger.put('%s' % (item))
        Logger.put('%s' % (isinstance(item, Item.InventoryItem)))

        assert(isinstance(item, Item.InventoryItem))
        self.inventory.append(item)

    def getInventory(self):
        return self.inventory

    def getWeapon(self):
        return self.weapon

    def setWeapon(self, weapon):
        assert(weapon in self.getInventory())
        assert(isinstance(weapon, BaseItems.Weapon))
        self.weapon = weapon

    def getHorizontalAttackDistance(self):
        return self.weapon.getHorizontalAttackDistance()

    def getVerticalAttackDistance(self):
        return self.weapon.getVerticalAttackDistance()

class Bandito(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'thieving bandito'
        self.representation = 'B'
        self.speed = 180
        self.attribute = Colors.getPairNumber("YELLOW", "BLACK")
        w = BaseItems.Revolver()
        self.addToInventory(w)
        self.setWeapon(w)
        "Banditos can see in the dark pretty well."
        self.minimumLightToSeeThreshold = self.minimumLightToSeeThreshold - 1

class Deputy(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'deputy'
        self.representation = '@'
        self.speed = 200
        self.attribute = Colors.getPairNumber("WHITE", "BLACK")
        w = BaseItems.Revolver()
        self.addToInventory(w)
        self.setWeapon(w)

class Outlaw(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'outlaw'
        self.representation = 'T'
        self.speed = 220
        self.attribute = Colors.getPairNumber("RED", "BLACK")
        "Outlaws cannot see in the dark well."
        self.minimumLightToSeeThreshold = self.minimumLightToSeeThreshold + 1

class Sheriff(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'sheriff'
        self.representation = '@'
        self.speed = 200
        self.attribute = Colors.getPairNumber("WHITE", "BLACK")
        w = BaseItems.Revolver()
        self.addToInventory(w)
        self.setWeapon(w)

        self.addToInventory(BaseItems.SheriffBadge())





