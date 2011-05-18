import curses, heapq, random, sys, copy

import WorldState, Logger, ToastWrangler, Item, Creature, Player, BaseGroundTypes, FOV, Colors, Overlay

class TeamViewer:
    INFINITY = 9999
    def __init__(self, world, initTeam = []):
        self.world = world
        self.teamList = initTeam

    def getTeamList(self):
        return self.teamList

    def getTeamMember(self, index):
        return self.teamList[index]

    def getLocation(self):
        return self.world.currentViewer.getLocation()

    def canSee(self, x, y):
        for i in self.teamList:
            if (i.canSee(x,y)):
                return True
        return False

    def getBrightnessThreshold(self, x, y):
        threshold = TeamViewer.INFINITY #infinity to start
        for i in self.teamList:
            if (i.canSee(x,y)):
                newThresh = i.getBrightnessThreshold(x,y)
                if (newThresh < threshold):
                    threshold = newThresh
        #SOMEONE should be able to see this square if we're being asked about the brightness threshold
        assert (threshold != TeamViewer.INFINITY)

        return threshold
                
            

class World:
    cannotSeeRepresentation = ' '
    cannotSeeAttribute = None

    DRAW_MODE_BEGIN = 0
    DRAW_DETAIL_DEPTH = 0
    DRAW_DETAIL_PHYSICAL = 1
    DRAW_MODE_END = 1

    VIEW_MODE_BEGIN = 0
    VIEW_VIEWER_INFORMATION = 0
    VIEW_TEAM_INFORMATION = 1
    VIEW_MODE_END = 1

    zHeightLookupTable = {
        -9 : u'\u2784',
        -8 : u'\u2783',
        -7 : u'\u2782',
        -6 : u'\u2781',
        -5 : u'\u2780',
        -4 : u'\u2779',
        -3 : u'\u2778',
        -2 : u'\u2777',
        -1 : u'\u2776',
        0 : '0',
        1 : '1',
        2 : '2',
        3 : '3',
        4 : '4',
        5 : '5',
        6 : '6',
        7 : '7',
        8 : '8',
        9 : '9',
    }

    def __init__(self, screen, width = None, height = None):
        self.screen = screen
        self.width = width
        self.height = height
        self.statusLinesHeight = 5
        self.time = 0
        self.eventHeap = []
        self.shouldPause = False
        self.lightSources = []

        self.defaultOverlay = Overlay.Overlay(self)
        self.overlay = self.defaultOverlay

        self.setDrawMode(World.DRAW_DETAIL_PHYSICAL)
        self.setViewMode(World.VIEW_VIEWER_INFORMATION)

        #self.world is referenced by x first, then y
        self.world = []

        if (self.width == None):
            self.width = self.screen.getmaxyx()[1]
        if (self.height == None):
            self.height = self.screen.getmaxyx()[0] - 5

        #self.makeForestMap()
        self.loadMapFromFile('testMap.txt')

        self.team = TeamViewer(self, [Player.Player(), Player.Player()])
        self.currentViewer = self.team.getTeamMember(0)
        for i in range(0, len(self.team.getTeamList())):
            self.placeItem(self.team.getTeamMember(i), i, 0)

        #initialize some static data if not already initialized
        if (World.cannotSeeAttribute == None):
            World.cannotSeeAttribute = Colors.getPairNumber('WHITE', 'BLACK')
            for k in World.zHeightLookupTable.keys():
                result = WorldState.WorldRepresentation.convertString(World.zHeightLookupTable[k])
                if (k < 0):
                    World.zHeightLookupTable[k] = result
                else:
                    World.zHeightLookupTable[k] = result

        self.statusLines = []
        self.statusOffset = 11-6
        for i in range(0, 10):
            self.addStatusLine('WEEE %d' % (i))
        self.statusLinesAttribute = 0

    def setOverlay(self, newOverlay):
        self.overlay = newOverlay

    def setDefaultOverlay(self):
        self.overlay = self.defaultOverlay

    def getCannotSeeTuple(self):
        return (World.cannotSeeRepresentation, World.cannotSeeAttribute)

    def getDrawMode(self):
        return self.drawMode

    def setDrawMode(self, newMode):
        assert(newMode >= World.DRAW_MODE_BEGIN and newMode <= World.DRAW_MODE_END)
        self.drawMode = newMode

    def getViewMode(self):
        return self.viewMode

    def setViewMode(self, newMode):
        assert(newMode >= World.VIEW_MODE_BEGIN and newMode <= World.VIEW_MODE_END)
        self.viewMode = newMode

    def setViewer(self, creature):
        assert(isinstance(creature, Player.Player))
        self.currentViewer = creature

    def prepareForDraw(self):
        for l in self.lightSources:
            l.do_fov()

    def addLightSource(self, fovObj):
        assert (not fovObj in self.lightSources)
        self.lightSources.append(fovObj)

    def removeLightSource(self, lightFovObj):
        "Remove the specified light source and recalculate lighting."
        self.lightSources.remove(lightFovObj)
        self.prepareForDraw()

    def getGlobalLightingAt(self, x, y):
        ret = 0.0
        for l in self.lightSources:
            ret = ret + l.getLightAt(x,y)
        return ret

    fileGridCharacterToObjectMap = {
        'b' : BaseGroundTypes.Bush,
        'd' : BaseGroundTypes.Ground,
        's' : BaseGroundTypes.Swamp,
        't' : BaseGroundTypes.Tree,
        '~' : BaseGroundTypes.Water,
        '#' : BaseGroundTypes.CampFire,
        '*' : BaseGroundTypes.LargeBoulder,
    }

    fileGridCharacterToLightMap = {
        '#' : 7 #campfire
    }

    def fileGridCharacterToObject(self, char, x, y):        
        assert(char in World.fileGridCharacterToObjectMap)
        Logger.put('Looking up: %s = %s' % (char, World.fileGridCharacterToObjectMap[char]))
        obj = World.fileGridCharacterToObjectMap[char](self,x,y)
        return obj

    def fileGridCharacterToLight(self, char, x, y):
        return World.fileGridCharacterToLightMap.get(char, None)

    @staticmethod
    def fileGridZToZ(z):
        return int(z)

    def loadMapFromFile(self, filename):
        f = open(filename, 'r')

        dims = [int(s) for s in f.readline().split(' ')]

        self.width = dims[0]
        self.height = dims[1]

        Logger.put('%s\'s dimensions: %s' % (filename, str(dims)))

        cMap = []
        for i in range(0, self.height):
            line = f.readline().strip()
            cMap.extend(line)

        assert(len(cMap) == self.width * self.height)

        #Make the world array empty and of the right dimensions
        self.world = []
        for x in range(0, self.width):
            array = []
            for y in range(0, self.height):
                array.append(None)
            self.world.append(array)

        #self.world = [ copy.copy([[None] * self.height ]) * self.width

        Logger.put('World: %s' % (self.world))

        for y in range(0, self.height):
            for x in range(0, self.width):
                charPopped = cMap.pop(0)
                self.world[x][y] = self.fileGridCharacterToObject(charPopped,x,y)

                lightIntensity = self.fileGridCharacterToLight(charPopped,x,y)
                if (lightIntensity != None):
                    lightObj = FOV.LightMap(self, x, y, lightIntensity)
                    self.addLightSource(lightObj)
                    pass

        #No more characters should exist in the cMap listing because we added them all to the map.
        assert(len(cMap) == 0)

        #Now read in z-information
        cMap = []
        line = f.readline().strip()
        assert(line == '') #blank line in between objects and Z depths
        for i in range(0, self.height):
            line = f.readline().strip()
            cMap.extend(line)

        for y in range(0, self.height):
            for x in range(0, self.width):
                charPopped = cMap.pop(0)
                self.world[x][y].setZ(self.fileGridZToZ(charPopped))

        Logger.put('World len = %d' % (len(self.world)))
        Logger.put('World[0] len = %d' % (len(self.world[0])))

        f.close()

        Logger.put('%s' % (str(self.world)))

    def makeForestMap(self):
        rsx = random.randint(0,self.width-1)
        rex = random.randint(0,self.width-1)
        rwidth = random.randint(2, 6)

        for i in range(0, self.width):
            curCol = []
            for j in range(0, self.height):
                q = random.randint(0,80)
                if (q == 0):    
                    curCol.append(BaseGroundTypes.Tree(self,i,j))
                else:
                    curCol.append(BaseGroundTypes.Ground(self,i,j))
            self.world.append(curCol)

        for x in range(10,25):
            for y in range(10,25):
                if (y == 10 or x == 10 or y == 24 or x == 24):
                    self.world[x][y] = BaseGroundTypes.Swamp(self,x,y)
                else:
                    self.world[x][y] = BaseGroundTypes.Water(self,x,y)
        
    def makeDesertMap(self):
        for i in range(0, self.width):
            curCol = []
            for j in range(0, self.height):
                q = random.randint(0,95)
                if (q == 0):
                    curCol.append(BaseGroundTypes.LargeBoulder(self,i,j))
                else:
                    curCol.append(BaseGroundTypes.Ground(self,i,j))
            self.world.append(curCol)

    def addEventCallback(self, dtime, function, target):
        assert (dtime > 0)
        heapq.heappush(self.eventHeap, (self.time + dtime,function,target))
        #Logger.put('HEAP: has %d @ %d %s' % (len(self.eventHeap), self.time + dtime, str(function)))


    def getDimensions(self):
        return (self.width, self.height)

    def processNextEvent(self):
        if (self.eventHeap):
            nextEvent = heapq.heappop(self.eventHeap)
            Logger.put("Time: was %d now is %d: %s" % (self.time, nextEvent[0], str(nextEvent)))
            assert(self.time <= nextEvent[0])
            self.time = nextEvent[0]
            if (nextEvent[1]() == True):
                self.shouldPause = False
            return True
        return False

    def doEventLoop(self):
        self.draw()
        while (self.processNextEvent()):
            if (self.shouldPause):
                curses.napms(50)
                pass
            self.shouldPause = True
            #self.draw(self.currentViewer)
            if (ToastWrangler.getShouldQuit()):
                return

    def getWorldCell(self, x, y):
        assert(x >= 0 and y >= 0 and x < self.width and y < self.height)
        return self.world[x][y]

    def getBlocksSight(self, x, y):
        return self.world[x][y].getBlocksSight()

    def getMayPass(self, x, y, viewer):
        return self.world[x][y].getMayPass(viewer) and not self.world[x][y].anythingAliveInContents()

    def isInBounds(self, x, y):
        return not (x < 0 or y >= self.height or x >= self.width or y < 0)

    def placeItem(self, item, itemX = 0, itemY = 0):
        self.world[itemX][itemY].addItem(item, itemX, itemY)

    def addStatusLine(self, string):
        self.statusLines.append(string)
        self.statusOffset = max(len(self.statusLines) - self.statusLinesHeight, 0)
        pass

    def drawStatusRegion(self):
        maxSideBarLen = 11
        width = self.screen.getmaxyx()[1] - 1 - maxSideBarLen - 1
        height = self.statusLinesHeight
        startX = 0
        startY = self.screen.getmaxyx()[0] - 6

        if (self.statusLines == []):
            return
        linesDrawn = 0

        for i in self.statusLines[self.statusOffset:]:
            linesDrawn = linesDrawn + 1
            remainingSpace = width - len(i)

            self.screen.addnstr(startY + linesDrawn, startX, i + ' ' * remainingSpace, width, self.statusLinesAttribute)

            if (linesDrawn >= height):
                break
        if (self.getViewMode() == World.VIEW_VIEWER_INFORMATION):
            viewModeStr = 'Indiv. View'
        else:
            viewModeStr = 'Team View  '

        if (self.getDrawMode() == World.DRAW_DETAIL_DEPTH):
            drawModeStr = 'Depth Mode '
        else:
            drawModeStr = 'Detail Mode'

        self.screen.addnstr(startY, width + 1, viewModeStr, maxSideBarLen, self.statusLinesAttribute)
        self.screen.addnstr(startY + 1, width + 1, drawModeStr, maxSideBarLen, self.statusLinesAttribute)
        self.screen.addnstr(startY + 2, width + 1, 'MovePts: %d' % (self.currentViewer.getMoveActionDistance() - self.currentViewer.getMoveDistanceThisTurn()), maxSideBarLen, self.statusLinesAttribute)

        currentViewerHPStr = 'HP: %d/%d' % (self.currentViewer.getHP(), self.currentViewer.getMaxHP())
        self.screen.addnstr(startY + 3, width + 1, currentViewerHPStr, maxSideBarLen, self.currentViewer.getStatusBarHPAttribute())


    def moveItem(self, item, x, y, newX, newY):
        if (not self.isInBounds(newX, newY)):
            raise ValueError('Unable to move item %s from %d,%d to %d,%d' % (item.getDescription(), x, y, newX, newY))
        self.world[x][y].removeItem(item)
        self.world[newX][newY].addItem(item, newX, newY)
        return True

    @staticmethod
    def zHeightToCharacter(z):
        if (z == None):
            return World.cannotSeeRepresentation
        assert(z in World.zHeightLookupTable)
        return World.zHeightLookupTable[z]


    def draw(self, viewer = None, maxWidth = None, maxHeight = None):
        if (viewer == None):
            if (self.getViewMode() == World.VIEW_TEAM_INFORMATION):
                viewer = self.team
            else:
                viewer = self.currentViewer
#unnecessary asserts: the help feature can override the viewer parameter now.
#        else:
#            assert(self.getViewMode() != World.VIEW_TEAM_INFORMATION)

        if (maxWidth == None):
            maxWidth = min(self.screen.getmaxyx()[1], self.width)

        if (maxHeight == None):
            maxHeight = min(self.screen.getmaxyx()[0] - 5, self.height)

        startX, startY = viewer.getLocation()

        #try to center the camera on them
        startX = max(startX - maxWidth / 2, 0)
        startY = max(startY - maxHeight / 2, 0)

        upperWidthBound = maxWidth + startX
        upperHeightBound = maxHeight + startY

        if (upperWidthBound > self.width):
            upperWidthBound = self.width
            startX = self.width - maxWidth

        if (upperHeightBound > self.height):
            upperHeightBound = self.height
            startY = self.height - maxHeight

        #Logger.put('%d %d to %d %d' % (startX, upperWidthBound, startY, upperHeightBound))
        xDims = range(startX, upperWidthBound)
        yDims = range(startY, upperHeightBound)

        self.prepareForDraw()

        #viewerCoords = self.currentViewer.getLocation()
        viewerCoords = viewer.getLocation()
        

        for j in yDims:
            for i in xDims:
                if (self.drawMode == World.DRAW_DETAIL_PHYSICAL):
                    if (viewer.canSee(i,j)):
                        representation = self.overlay.getDrawTuple(i,j,viewer,self.getGlobalLightingAt(i,j))
                        #representation = self.world[i][j].getDrawTuple(viewer, self.getGlobalLightingAt(i,j))
                    else:
                        representation = self.getCannotSeeTuple()
                elif (self.drawMode == World.DRAW_DETAIL_DEPTH):
                    if (viewer.canSee(i,j)):
                        z = World.zHeightToCharacter(self.world[i][j].getZ())
                        representation = (z, self.world[i][j].getZDepthAttribute(viewer, self.getGlobalLightingAt(i,j)))
                    else:
                        representation = self.getCannotSeeTuple()
                        
                else:
                    raise ValueError('Draw mode: %d not yet finished.' % (self.drawMode))
                
                #Logger.put('%d, %d, %s, %s' % (j-startY, i-startX, representation[0], representation[1]))
                self.screen.addstr(j - startY, i - startX, representation[0], representation[1])
                #self.screen.addch(j - startY, i - startX, 178, representation[1])
                    
        self.drawStatusRegion()
        self.screen.move(viewerCoords[1] - startY, viewerCoords[0] - startX)
        self.screen.refresh()
