import random
import Creature, World, Logger

class Behavior(object):
    def __init__(self, creature):
        self.creature = creature
        pass

    def doAction(self):
        Logger.put('WARNING: %s is using Behavior.doAction(), which does nothing' % (str(self)))
        pass

class AttackRandomTarget(Behavior):

    def attackRandomPossibleTarget(self):
        visibleTiles = self.creature.getFullCanSeeList()

        attackableCreatures = []

        for t in visibleTiles:
            attackableCreatures.extend(self.creature.getWorld().getAttackableCreaturesInCell(t[0],t[1],self.creature))

        if (len(attackableCreatures) > 0):
            #Pick a random attackable creature
            target = random.choice(attackableCreatures)
            Logger.put('%s has decided to attack %s' % (str(self.creature), str(target)))
            self.creature.doAttack(target)
        else:
            pass

    def doAction(self):
        self.attackRandomPossibleTarget()

class PerhapsAttackNearest(AttackRandomTarget):
    def __init__(self, creature, attemptAttackChance = 0.5):
        super(PerhapsAttackNearest,self).__init__(creature)
        self.attemptAttackChance = attemptAttackChance

    def doAction(self):
        diceRoll = random.random()
        if (diceRoll < self.attemptAttackChance):
            self.attackRandomPossibleTarget()
        else:
            Logger.put('%s has chosen to ignore possible targets' % (str(self.creature)))
