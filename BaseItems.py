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

class MeleeWeapon(Weapon):
    def __init__(self):
        Weapon.__init__(self)
        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1
        self.accuracy = 0.65


class Bottle(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        #TODO: It should be possible to throw or melee someone with a beer bottle.
        #TODO: A bottle should have a high chance of breaking once it is used.
        #After breaking, it should perhaps do slicing damage.
        self.description = 'a beer bottle'
        self.accuracy = 0.60

class BrassKnuckles(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        self.description = 'a fist wearing brass knuckles'

class Fists(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1
        self.accuracy = 0.65

class Hammer(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        self.description = 'a metal hammer with a wooden handle'
        self.accuracy = 0.55

class Hatchet(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        self.description = 'a metal hatch with a wooden handle'
        self.accuracy = 0.55

class LargeRock(MeleeWeapon):
    def __init__(self):
        #TODO: It should be possible to bash (melee) someone with a large rock,
        #or, throw the large rock.
        MeleeWeapon.__init__(self)
        self.description = 'a large rock'
        self.accuracy = 0.60

class PocketKnife(MeleeWeapon):
    def __init__(self):
        MeleeWeapon.__init__(self)
        self.description = 'an open pocket knife'
        self.accuracy = 0.60

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


