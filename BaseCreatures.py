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
        self.inventory = []
        self.weapon = None

    def getHelpDescription(self):
        if (self.weapon == None):
            return Creature.Creature.getHelpDescription(self)
        else:
            return Creature.Creature.getHelpDescription(self) + ' carrying ' + self.weapon.getDescription()

    def addToInventory(self, item):
        assert(isinstance(item, Item.InventoryItem))
        self.inventory.append(item)

    def getInventory(self):
        return self.inventory

    def getWeapon(self):
        return self.weapon

    def setWeapon(self, weapon):
        assert(weapon in self.getInventory())
        self.weapon = weapon

class Bandito(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'a thieving bandito'
        self.representation = 'B'
        self.speed = 180
        self.attribute = Colors.getPairNumber("YELLOW", "BLACK")
        w = BaseItems.Revolver()
        self.addToInventory(w)
        self.setWeapon(w)

class Outlaw(CreatureWithInventory):
    def __init__(self):
        CreatureWithInventory.__init__(self)
        self.description = 'an outlaw'
        self.representation = 'T'
        self.speed = 220
        self.attribute = Colors.getPairNumber("RED", "BLACK")

