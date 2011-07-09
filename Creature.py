import curses
import Logger, Item, Colors, InputHandler, ToastWrangler, FOV, Behavior
import copy, random

class Creature(Item.LocationAwareItem):
    def __init__(self):
        Item.LocationAwareItem.__init__(self)
        self.x = None
        self.y = None
        self.world = None
        self.speed = 100
        self.description = 'uninherited-from creature'
        self.representation = 't'
        self.foreGroundColorName = 'YELLOW'
        self.attribute = Colors.BOLD | Colors.getPairNumber(self.foreGroundColorName, "BLACK")
        self.inputHandler = InputHandler.SingletonKeyboardInputHander(ToastWrangler.screen)
        Logger.put(str(self.inputHandler))

        self.minimumLightToSeeThreshold = 3

        self.seeDistance = 99
        self.fov = None

        self.light = None

        self.moveActionDistance = 3
        self.moveDistanceThisTurn = 0

        self.didAttack = False

        self.maxHP = 10
        self.hp = 10

        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1

        self.attackDamage = 1

        self.toggleLightCost = 1

        self.team = 0

    def getAttackDamage(self, target):
        return self.attackDamage

    def setTeam(self, newTeam):
        self.team = newTeam

    def getTeam(self):
        return self.team

    def getHealthDescriptionAdjective(self):
        healthPercentage = float(self.hp) / self.maxHP

        for percentage, adjective in zip([0.10, 0.8, 0.9], ['mortally wounded', 'wounded', 'scratched']):
            if (healthPercentage <= percentage):
                return adjective + ' '
        return ''

    def getHelpDescription(self):
        return self.getHealthDescriptionAdjective() + self.getDescription()

    def targetIsAttackable(self, creature):
        return (creature.getTeam() != self.getTeam() and isinstance(creature,Creature))

    def canAttack(self, x, y):
        if (self.canSee(x,y)): #For now, can only attack creatures
            xCost = abs(self.x - x)
            yCost = abs(self.y - y)
            if (xCost == 1 and yCost == 1): #diagonal
                xCost = 0
            
            zCost = abs(self.worldCell.getZ() - self.world.world[x][y].getZ())
            if (zCost <= self.getVerticalAttackDistance() and xCost + yCost <= self.getHorizontalAttackDistance()):
                return True
            return False

    def getWorld(self):
        return self.world

    def getHorizontalAttackDistance(self):
        return self.horizontalAttackDistance

    def getVerticalAttackDistance(self):
        return self.verticalAttackDistance

    def getMaxHP(self):
        return self.maxHP

    def getHP(self):
        return self.hp

    def healHP(self, amount):
        self.hp = self.hp + amount
        if (self.hp > self.maxHP):
            self.hp = self.maxHP

    def getMoveActionDistance(self):
        return self.moveActionDistance

    def getMoveDistanceThisTurn(self):
        return self.moveDistanceThisTurn

    def startTurn(self):
        self.moveDistanceThisTurn = 0
        self.didAttack = False

    def endTurn(self):
        pass

    def isAlive(self):
        return True

    def getMinimumLightToSeeThreshold(self, x = None, y = None):
        return self.minimumLightToSeeThreshold 

    def getBrightnessThreshold(self, x = None, y = None):
        return 5.0

    def getLocation(self):
        return (self.x, self.y)

    def getFullCanSeeList(self):
        #return a list of (x,y) tuples
        #where each (x,y) tuple is a square that the Creature can see
        worldDims = self.world.getDimensions()
        canSeeList = []
        for x in range(0,worldDims[0]):
            for y in range(0, worldDims[1]):
                if (self.canSee(x,y)):
                    canSeeList.append((x,y))

        return canSeeList

    def canSee(self, x, y):
        if (self.fov.changed):
            self.fov.do_fov()
        isLit = self.fov.lit(x,y)
        canSee = self.world.getGlobalLightingAt(x, y) >= self.getMinimumLightToSeeThreshold(x,y)
        return isLit and canSee 
        #return self.fov.lit(x,y)

    def getStatusBarHPAttribute(self):
        percentHealth = float(self.getHP())/self.getMaxHP()
        if (percentHealth <= 0.333):
            return Colors.getPairNumber('RED', 'BLACK')
        elif (percentHealth <= 0.666):
            return Colors.getPairNumber('YELLOW', 'BLACK')
        else: 
            return Colors.getPairNumber('GREEN', 'BLACK')

    def newLocation(self):
        if (self.light != None):
            self.light.changePosition(self.x, self.y)
        self.fov.changePosition(self.x, self.y)
        Item.LocationAwareItem.newLocation(self)

    def canPerformMoveAction(self, futureCost):
        return self.moveDistanceThisTurn + futureCost <= self.moveActionDistance

    def lightIsOn(self):
            return self.light != None

    def togglePersonalLight(self):
        if (self.canPerformMoveAction(self.toggleLightCost)):
            if (self.lightIsOn()):
                self.turnLightOff()
            else:
                self.turnLightOn()
            self.doMoveAction(self.toggleLightCost)
        else:
            self.world.addStatusLineIfPlayer(self, 'Toggling the light requires %0.1f move points.' % (float(self.toggleLightCost)))
            pass

    def doMoveAction(self, moveCost):
        assert(self.canPerformMoveAction(moveCost))
        self.moveDistanceThisTurn += moveCost

    def isDoneAttacking(self):
        return self.didAttack

    def setIsDoneAttacking(self):
        self.didAttack = True

    def isDoneMoving(self):
        return self.moveDistanceThisTurn >= self.moveActionDistance

    def setIsDoneMoving(self):
        self.moveDistanceThisTurn = self.moveActionDistance

    def turnLightOn(self):
        if (self.light != None):
            Logger.put('Warning: %s.turnLightOn() but light already on.' % (str(self)))
        self.light = self.makeNewLight()
        self.world.addLightSource(self.light)

    def turnLightOff(self):
        if (self.light == None):
            Logger.put('Warning: %s.turnLightOff() but light already off.' % (str(self)))
        self.world.removeLightSource(self.light)
        self.light = None

    def makeNewLight(self):
        return FOV.LightMap(self.world, self.x, self.y, 10.0)

    def placeInto(self, world, worldCell, x, y):
        #Logger.put('%s was placed into %d,%d' % (self.getDescription(None, None), x, y))

        if (not world == self.world):
            self.world = world
            self.fov = FOV.LightMap(self.world, x, y, self.seeDistance)
            #Dirty hack: set self.x and self.y so that turnLightOn
            #knows where in the world the light is. 
            self.x = x
            self.y = y
            #END HACK
            self.turnLightOn()
            self.world.addEventCallback(self.speed, self.doThink, self)
        Item.LocationAwareItem.placeInto(self, world, worldCell, x, y)

        

    def moveTo(self, destX, destY):
        if (self.world.isInBounds(destX, destY) and self.world.getMayPass(destX, destY, self)):
            self.world.moveItem(self, self.x, self.y, destX, destY)
            return True
        return False

    def doThink(self):
        dir = InputHandler.InputHandler.getRandomDirection()
        self.moveTo(self.x + dir[0], self.y + dir[1])
       
        #Eventually, the behavior should become a property/field in the Creature.            
        behavior = Behavior.PerhapsAttackNearest(self)
        behavior.doAction()

        self.world.addEventCallback(self.speed, self.doThink, self)

        self.world.draw()
        curses.napms(200)

    def takeDamage(self, damage, attacker):
        self.hp = max(self.hp - damage, 1)
        

    def doAttack(self, target):
        #see if the attack hits
        accuracy = self.getWeapon().getBaseAccuracy()

        self.getWorld().addAppropriateStatusLine(self,
                'You (%s) attacked %s.' % (self.getDescription(), target.getDescription()),
                '%s attacked you (%s).' % (self.getDescription(), target.getDescription()))

        if (accuracy == 1 or random.random() <= accuracy):
            damage = self.getAttackDamage(target)
            target.takeDamage(damage, self)

            self.getWorld().addAppropriateStatusLine(self,
                    'The attack did %d damage.' % (damage),
                    'The attack to you did %d damage.' % (damage))
        else:
            self.getWorld().addStatusLine('The attack missed!')


