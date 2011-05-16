import Creature, Colors, Logger, ToastWrangler, World, Overlay, random
#A few simple generic creatures to fight against.

def getGenericCreature():
    r = random.randint(0, 1)

    if (r == 0):
        return Bandito()
    return Outlaw()

class Bandito(Creature.Creature):
    def __init__(self):
        Creature.Creature.__init__(self)
        self.description = 'a thieving bandito'
        self.representation = 'B'
        self.speed = 180
        self.attribute = Colors.getPairNumber("YELLOW", "BLACK")

class Outlaw(Creature.Creature):
    def __init__(self):
        Creature.Creature.__init__(self)
        self.description = 'an outlaw'
        self.representation = 'T'
        self.speed = 220
        self.attribute = Colors.getPairNumber("RED", "BLACK")

