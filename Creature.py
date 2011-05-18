import curses
import Logger, Item, Colors, InputHandler, ToastWrangler, FOV
import copy

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
        self.inputHandler = InputHandler.KeyboardInputHandler(ToastWrangler.screen)

        self.minimumLightToSeeThreshold = 3

        self.seeDistance = 99
        self.fov = None

        self.light = None

        self.moveActionDistance = 3
        self.moveDistanceThisTurn = 0

        self.maxHP = 10
        self.hp = 10

        self.horizontalAttackDistance = 1
        self.verticalAttackDistance = 1

    def getHelpDescription(self):
        return self.getDescription()

    def canAttack(self, x, y):
        if (self.canSee(x,y)):
            xCost = abs(self.x - x)
            yCost = abs(self.y - y)
            if (xCost == 1 and yCost == 1): #diagonal
                xCost = 0
            
            zCost = abs(self.worldCell.getZ() - self.world.world[x][y].getZ())
            if (zCost <= self.getVerticalAttackDistance() and xCost + yCost <= self.getHorizontalAttackDistance()):
                return True
            return False

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

    def lightIsOn(self):
            return self.light != None

    def togglePersonalLight(self):
        if (self.lightIsOn()):
            self.turnLightOff()
        else:
            self.turnLightOn()


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
        Logger.put('%s was placed into %d,%d' % (self.getDescription(None, None), x, y))

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
        #Logger.put('%s is thinking...' % (self.description))
        #key = self.inputHandler.getDirection()
        #if (key == 27):
        #   return

        #dir = self.inputHandler.keyToOffset(key)
        #Logger.put('%s wants to move: (%d,%d)' % (self.description, dir[0], dir[1]))
        #self.world.moveItem(self, self.x, self.y, self.x + dir[0], self.y + dir[1])
        self.world.addEventCallback(self.speed, self.doThink, self)
        self.world.draw()
        curses.napms(200)

