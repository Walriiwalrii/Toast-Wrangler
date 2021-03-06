import Creature, Colors, Logger, ToastWrangler, World, Overlay, BaseCreatures, BaseItems
import time, random

#def __init__(self):
#    BaseCreatures.CreatureWithInventory.__init__(self)
#    self.description = 'the player'
#    self.representation = '@'
#    self.speed = 200
#    self.attribute = Colors.getPairNumber("WHITE", "BLACK")
#    self.attackOverlay = None

#    self.addToInventory(BaseItems.SheriffBadge())
#    w = BaseItems.Revolver()
#    self.addToInventory(w)
#    self.setWeapon(w)

def makePlayerControlled(self):
    self.setTeam(ToastWrangler.PLAYER_TEAM)

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
    #If the Creature has recently become Player
    #controlled, then it may not have its attackOverlay
    #value set. So, we try to access it and if it hasn't
    #been set, we initialize it.

    try:
        self.attackOverlay
    except:
        self.attackOverlay = Overlay.CanAttackOverlay(self.world, self)
        Logger.put('Creature %s has had attackOverlay initialized.' % (self))

    self.world.addEventCallback(self.speed, self.doThink, self)
    
    self.startTurn()

    self.world.resetStatusLinesAppended()

    retVal = False

    while (not self.isDoneAttacking() or not self.isDoneMoving()):
        self.world.setViewer(self)

        self.world.draw()

        Logger.put('%s is thinking...' % (self.description))
        key = self.inputHandler.waitForKey()
        if (key == ToastWrangler.enterKey or key == ord('.')): #skip turn
            self.setIsDoneMoving()
            self.setIsDoneAttacking()
            continue

        if (key == ToastWrangler.lightToggleKey):
            self.togglePersonalLight()
        elif (key == ToastWrangler.helpKey):
            Player.doHelp(self)
            pass
        elif (keysAvailableAnytime(self,key)):
            self.world.draw()
            continue
        elif (not self.isDoneAttacking() and key == ToastWrangler.attackKey):
            overlayOn = False
            self.attackOverlay.setCursorPosition(self.x, self.y)
            self.world.setOverlay(self.attackOverlay)
            self.world.draw()

            key = None

            previousMeasureTime = time.time()

            attackModeQuitKeys = [ToastWrangler.attackKey, ToastWrangler.enterKey, ToastWrangler.spaceKey]
            while (not key in attackModeQuitKeys):
                nowTime = time.time()
                key = self.inputHandler.pauseForKey(self.inputHandler.getDefaultPauseTime() - (nowTime - previousMeasureTime))

                previousMeasureTime = nowTime

                keysAvailableAnytime(self,key)

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
                x, y = self.attackOverlay.cursorPosX, self.attackOverlay.cursorPosY
                self.setIsDoneAttacking()
                targets = self.world.getAttackableCreaturesInCell(x, y, self)
                if (len(targets)>0):
                    self.doAttack(random.choice(targets))
            
        elif (key == ToastWrangler.quitKey):
            return retVal
        elif (not self.isDoneMoving()):
            try:
                keysAvailableAnytime(self,key)
                dir = self.inputHandler.keyToOffset(key)

            except ValueError:
                pass
            else:
                if (self.world.isInBounds(self.x + dir[0], self.y + dir[1])):
                    moveCost = self.worldCell.getMoveCost(self.world.getWorldCell(self.x + dir[0], self.y + dir[1]))
                    if (self.canPerformMoveAction(moveCost)):
                        if (self.moveTo(self.x+dir[0], self.y+dir[1])):
                            self.doMoveAction(moveCost)


        if (key == 66):  #B
            c = BaseCreatures.getGenericCreature()
            self.world.placeItem(c, 0, 0)
            self.world.addStatusLine('DEBUG: Added random creature to 0 0')
            self.world.draw()

        self.world.draw()

    self.endTurn()
    return retVal
