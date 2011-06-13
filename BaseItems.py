#These are some simple items that are common in the world.

import World, ToastWrangler, InputHandler, Logger, Item

class Weapon(Item.InventoryItem):
    def __init__(self):
        Item.InventoryItem.__init__(self)
        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1
        self.accuracy = 1
    def getHorizontalAttackDistance(self):
        return self.horizontalAttackDistance
    def getVerticalAttackDistance(self):
        return self.verticalAttackDistance
    def getBaseAccuracy(self):
        return self.accuracy

    #base modifier: general accuracy of this weapon, not ignoring the user
    #and/or target
    def getHitModifier(self):
        return 1

class Fists(Weapon):
    def __init__(self):
        Weapon.__init__(self)
        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1
        self.accuracy = 0.65

class Revolver(Weapon):
    def __init__(self):
        Weapon.__init__(self)
        self.description = 'a revolver'
        self.horizontalAttackDistance = 10
        self.verticalAttackDistance = 10
        self.accuracy = 0.70

class SheriffBadge(Item.InventoryItem):
    def __init__(self):
        Item.InventoryItem.__init__(self)
        self.description = 'a sheriff\'s badge'
