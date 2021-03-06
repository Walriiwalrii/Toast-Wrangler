import World, ToastWrangler, InputHandler, Logger

class Item(object):
    def __init__(self):
        self.mass = 1
        self.description = 'uninherited-from item'
        self.representation = '_'
        self.attribute = 0
        self.x = None
        self.y = None

    def doesAppearOnMap(self, viewer, globalLighting):
        return True

    def isAlive(self):
        return False

    def __str__(self):
        return self.getDescription()

    def getDescription(self, viewer=None, globalLighting=None):
        return self.description

    def getRepresentation(self, viewer, globalLighting):
        return self.representation
    
    def getAttribute(self, viewer, globalLighting):
        return self.attribute

    def getDrawTuple(self, viewer, globalLighting):
        return (self.getRepresentation(viewer, globalLighting), self.getAttribute(viewer, globalLighting))

    def placeInto(self, world, worldCell, x, y):
        self.x = x
        self.y = y
        #Logger.put('%s placed into %d,%d' % (self.description, x, y))

    def removeFrom(self, world, worldCell):
        #Logger.put('%s removed from its cell' % (self.description))
        pass

class InventoryItem(Item):
    def __init__(self):
        self.locationChanged = False
        self.worldCell = None
    def doesAppearOnMap(self, viewer, globalLighting):
        return False

class LocationAwareItem(Item):
    def __init__(self):
        self.locationChanged = False
        self.worldCell = None

    def newLocation(self):
        self.locationChanged = False
        pass

    def placeInto(self, world, worldCell, x, y):
        origX = self.x
        origY = self.y
        Item.placeInto(self, world, worldCell, x, y)
        self.worldCell = worldCell

        if (x != origX or y != origY):
            self.locationChanged = True
            self.newLocation()

