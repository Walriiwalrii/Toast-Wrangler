import Creature, Colors, Logger, ToastWrangler, World, Overlay

class Player(Creature.Creature):
    def __init__(self):
        Creature.Creature.__init__(self)
        self.description = 'the player'
        self.representation = '@'
        self.speed = 200
        self.attribute = Colors.getPairNumber("WHITE", "BLACK")
        self.attackOverlay = None

    def placeInto(self, world, worldCell, x, y):
        self.attackOverlay = Overlay.CanAttackOverlay(world, self)
        Creature.Creature.placeInto(self, world, worldCell, x, y)

    def keysAvailableAnytime(self, key, shouldDraw = True):
        if (key == ToastWrangler.zModeKey):
            if (self.world.getDrawMode() == World.World.DRAW_DETAIL_DEPTH):
                self.world.setDrawMode(World.World.DRAW_DETAIL_PHYSICAL)                
            else:
                self.world.setDrawMode(World.World.DRAW_DETAIL_DEPTH)
            if (shouldDraw):
                self.world.draw()
            return True
        elif (key == ToastWrangler.tabKey):
            if (self.world.getViewMode() == World.World.VIEW_VIEWER_INFORMATION):
                self.world.setViewMode(World.World.VIEW_TEAM_INFORMATION)
            else:
                self.world.setViewMode(World.World.VIEW_VIEWER_INFORMATION)
            if (shouldDraw):
                self.world.draw()
            return True
        return False

    def doHelp(self):
        self.world.addStatusLine('Entered help mode:')
        self.world.addStatusLine('Use direction keys to move around. \'q\' to exit. SPACE/ENTER to view square.')

        self.world.setViewMode(World.World.VIEW_TEAM_INFORMATION)

        self.world.draw()

        class HelpViewer:
                def __init__(self, team, x, y):
                    self.x = x
                    self.y = y
                    self.team = team

                def getLocation(self):
                    return (self.x, self.y)

                def changeLocation(self, x, y):
                    self.x = x
                    self.y = y
                    Logger.put('HelpViewer location: (%d, %d)' % (x, y))

                def canSee(self, x, y):
                    return self.team.canSee(x,y)

                def getBrightnessThreshold(self, x, y):
                    return self.team.getBrightnessThreshold(x, y)

        viewer = HelpViewer(self.world.team, self.x, self.y)

        key = None

        while (key != ToastWrangler.qKey):
            key = self.inputHandler.waitForKey()

            if (key == ToastWrangler.enterKey or key == ToastWrangler.spaceKey):
                if (viewer.canSee(viewer.x, viewer.y)):
                    cell = self.world.getWorldCell(viewer.x, viewer.y)
                    self.world.addStatusLine('What is here:')
                    self.world.addStatusLine(' * %s' % (cell.getHelpDescription()))
                    self.world.addStatusLine(' * %s' % (cell.getContentsDescription()))
                    pass
                pass
            else: #try to interpret this as a direction key
                try:
                    dir = self.inputHandler.keyToOffset(key)
    
                    if (self.world.isInBounds(viewer.x + dir[0], viewer.y + dir[1])):
                       viewer.changeLocation(viewer.x + dir[0], viewer.y + dir[1]) 
                except ValueError:
                    pass
            self.world.draw(viewer)
            pass

        self.world.addStatusLine('Exited help mode')
        self.world.draw()
        pass

    def doThink(self):
        self.world.addEventCallback(self.speed, self.doThink, self)
        
        self.startTurn()

        retVal = False
        didAttack = False
        doneMoving = not (self.moveActionDistance > 0)


        while (not didAttack or not doneMoving):
            self.world.setViewer(self)

            self.world.draw()

            Logger.put('%s is thinking...' % (self.description))
            key = self.inputHandler.waitForKey()
            if (key == ToastWrangler.enterKey or key == ord('.')): #skip turn
                didAttack = doneMoving = True
                continue
            Logger.put('found; %d, help = %d' % (key, ToastWrangler.helpKey))
            if (key == ToastWrangler.helpKey):
                self.doHelp()
                pass
            elif (self.keysAvailableAnytime(key)):
                self.world.draw()
                continue
            elif (not didAttack and key == ToastWrangler.attackKey):
                overlayOn = False
                self.attackOverlay.setCursorPosition(self.x, self.y)
                self.world.setOverlay(self.attackOverlay)
                self.world.draw()
                key = self.inputHandler.pauseForKey()
                if (self.keysAvailableAnytime(key)):
                    self.world.draw()
                    continue

                attackModeQuitKeys = [ToastWrangler.attackKey, ToastWrangler.enterKey, ToastWrangler.spaceKey]
                while (not key in attackModeQuitKeys):
                    key = self.inputHandler.pauseForKey()
                    self.keysAvailableAnytime(key)
    
                    try:
                        dir = self.inputHandler.keyToOffset(key)
                        adjusted = self.attackOverlay.adjustCursorPosition(dir[0], dir[1])
                        if (adjusted):
                            overlayOn = False
                    except ValueError:
                        pass

                    if (overlayOn): self.world.setOverlay(self.attackOverlay)
                    else: self.world.setDefaultOverlay()
                    self.world.draw()
                    overlayOn = not overlayOn

                self.world.setDefaultOverlay()
                if (key != ToastWrangler.attackKey):
                    didAttack = True
                    self.world.addStatusLine('You attacked (%d, %d)' %  (self.attackOverlay.cursorPosX, self.attackOverlay.cursorPosY))
                
            elif (key == ToastWrangler.quitKey):
                return retVal
            elif (not doneMoving):
                try:
                    self.keysAvailableAnytime(key)
                    dir = self.inputHandler.keyToOffset(key)
    
                    if (self.world.isInBounds(self.x + dir[0], self.y + dir[1])):
                        moveCost = self.worldCell.getMoveCost(self.world.getWorldCell(self.x + dir[0], self.y + dir[1]))
                        futureMoveCost = moveCost + self.moveDistanceThisTurn
                        if (futureMoveCost <= self.moveActionDistance):
                            if (self.moveTo(self.x+dir[0], self.y+dir[1])):
                                self.moveDistanceThisTurn+=moveCost
                                if (self.moveDistanceThisTurn >= self.moveActionDistance):
                                    doneMoving = True

                except ValueError:
                    pass
                    #not a direction
                    #Logger.put('rejected: %d' % (key))
            elif (key == 66):  #a
                c = Creature.Creature()
                self.world.placeItem(c, 0, 0)
                self.world.addStatusLine('Added creature to 0 0')
                self.world.draw()

        

            self.world.draw()

        self.endTurn()
        return retVal
