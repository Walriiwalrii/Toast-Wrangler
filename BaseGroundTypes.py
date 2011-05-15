import WorldState, Colors
import random, curses

class LightAble(WorldState.WorldRepresentation):
    def __init__(self, world,x,y):
        WorldState.WorldRepresentation.__init__(self,world,x,y)

    def getLightedAttribute(self, viewer, globalLighting, attrValue):
        if (globalLighting < viewer.getBrightnessThreshold(self.x, self.y)):
            return attrValue | curses.A_DIM
        return attrValue | curses.A_BOLD

    def getAttribute(self, viewer, globalLighting):
        return self.getLightedAttribute(viewer, globalLighting, self.attribute)     

    def getZDepthAttribute(self, viewer, globalLighting):
        return self.getLightedAttribute(viewer, globalLighting, self.zDepthAttribute)       


class Ground(LightAble):
    def __init__(self, world, x, y):
        LightAble.__init__(self,world,x,y)
        self.isWalkable = True
        r = random.randint(0,100)
        self.representation = WorldState.WorldRepresentation.convertString(u'\u2593')
        self.updateColor('YELLOW', 'BLACK')

class Water(LightAble):
    def __init__(self,world,x,y):
        LightAble.__init__(self,world,x,y)
        self.representation = WorldState.WorldRepresentation.convertString('~') 
        self.isWalkable = False
        self.updateColor('BLUE', 'BLUE')

class Swamp(LightAble):
    def __init__(self,world,x,y):
        LightAble.__init__(self,world,x,y)
        self.representation = WorldState.WorldRepresentation.convertString(u'\u2591')   
        self.updateColor('YELLOW', 'BLUE')
        self.isWalkable = True

class Tree(LightAble):
    def __init__(self,world,x,y):
        LightAble.__init__(self,world,x,y)
        self.representation = WorldState.WorldRepresentation.convertString('T') 
        self.representation = WorldState.WorldRepresentation.convertString(u'\u00B6')
        self.updateColor('GREEN', 'BLACK')
        self.isWalkable = False
        self.blocksSight = True

class Bush(LightAble):
    def __init__(self,world,x,y):
        LightAble.__init__(self,world,x,y)
        self.representation = WorldState.WorldRepresentation.convertString(u'\u2663')
        self.updateColor('GREEN', 'BLACK')
        self.isWalkable = False
        self.blocksSight = False

class LargeBoulder(LightAble):
    def __init__(self, world,x,y):
        LightAble.__init__(self,world,x,y)
        self.isWalkable = False
        self.blocksSight = False
        #self.representation = WorldState.WorldRepresentation.convertString(u'\u2586')
        self.representation = WorldState.WorldRepresentation.convertString('*')
        self.updateColor('YELLOW', 'BLACK')
