import random
import Creature, World, Logger

class Behavior(object):
    def __init__(self, creature):
        self.creature = creature
        pass

    def doAction(self):
        Logger.put('WARNING: %s is using Behavior.doAction(), which does nothing' % (str(self)))
        pass

class AttackNearest(Behavior):
    def doAction(self):
        visibleTiles = self.creature.getFullCanSeeList()

        attackableCreatures = []

        for t in visibleTiles:
            cellContents = self.creature.world.getWorldCell(t[0],t[1]).getContents()
            for c in cellContents:
                if (self.creature.targetIsAttackable(c)):
                    attackableCreatures.append(c)

        if (len(attackableCreatures) > 0):
            #Pick a random attackable creature
            target = random.choice(attackableCreatures)
            Logger.put('%s has decided to attack %s' % (str(self.creature), str(target)))
        else:
            pass
