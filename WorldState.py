import curses, copy, random
import Colors
import string

import ToastWrangler

class WorldRepresentation:
    #Default is a static world cell

    @staticmethod
    def convertString(str):
        return str.encode(ToastWrangler.encoding)

    def getWalkableDescription(self):
        if (self.isWalkable):
            return 'can walk on it'
        return 'cannot walk on it'

    def getBlocksSightDescription(self):
        if (self.blocksSight):
            return 'blocks line of sight'
        return 'does not block line of sight'

    def __init__(self, world, x, y, z = 0):
        self.x = x
        self.y = y
        self.z = 0
        self.world = world
        self.blocksSight = False
        self.isWalkable = True
        val = random.randint(0,2)


        if (val <= 0):
            self.representation = '?'
            self.updateColor('BLUE', 'BLACK')
        else:
            #self.representation = WorldRepresentation.convertString(u'\u2591')
            self.representation = ' '
            self.updateColor('YELLOW', 'BLACK')

        self.contents = []

    def updateColor(self, fgColor, bgColor):
        self.attribute = Colors.getPairNumber(fgColor, bgColor)
        self.fgColor = fgColor
        self.bgColor = bgColor
        self.zDepthAttribute = self.attribute
        if (fgColor == bgColor): #Same color! Uh oh!
            if (bgColor != 'BLACK'):
                self.zDepthAttribute = Colors.getPairNumber(self.fgColor, 'BLACK')
            else:
                self.zDepthAttribute = Colors.getPairNumber(self.fgColor, 'WHITE')

    def getMoveCost(self, otherWorldCell):
        xCost = abs(self.x - otherWorldCell.x)
        yCost = abs(self.y - otherWorldCell.y)

        #for now, only allowed to move 1 square 'over' at a time
        assert(xCost <= 1) 
        assert(yCost <= 1)

        diagCost = xCost + yCost
        
        if (xCost == 1 and yCost == 1): #diagonal movement only 'costs' 1
            diagCost = 1

        return diagCost + abs(self.getZ() - otherWorldCell.getZ())

    def setZ(self, newZ):
        self.z = newZ

    def getZ(self):
        return self.z

    def getZDepthAttribute(self, viewer, globalLighting):
        return self.zDepthAttribute

    def anythingAliveInContents(self):
        for i in self.contents:
            if (i.isAlive()):
                return True
        return False

    def getRepresentation(self, viewer, globalLighting):
        return self.representation

    def getAttribute(self, viewer, globalLighting):
        return self.attribute

    def getMayPass(self, viewer):
        return self.isWalkable

    def getBlocksSight(self):
        return self.blocksSight

    def getContents(self): #returns the list of what objects are in this cell
        return self.contents

    def addItem(self, item, x, y):
        self.contents.append(item)
        item.placeInto(self.world, self, x, y)

    def removeItem(self, item):
        self.contents.remove(item)
        item.removeFrom(self.world, self)

    def getDrawTuple(self, viewer, globalLighting): #returns a tuple of the form: (character, attribute)
        #try to show an item in this square first
        reverseItems = copy.copy(self.contents)
        reverseItems.reverse()
        for i in reverseItems:
            if (i.doesAppearOnMap(viewer, globalLighting)):
                return i.getDrawTuple(viewer, globalLighting)
        return (self.getRepresentation(viewer, globalLighting), self.getAttribute(viewer, globalLighting))

    def getHelpDescription(self):
        objectType = self.__class__.__name__
        walkable = self.getWalkableDescription()
        sight = self.getBlocksSightDescription()

        return '%s (%s, %s)' % (objectType, walkable, sight)

    def getContentsDescription(self):
        if (len(self.contents) <= 0):
            return '[no contents]'

        return string.join([o.getHelpDescription() for o in self.contents], ', ')
