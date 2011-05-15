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

    def keysAvailableAnytime(self, key):
        if (key == ToastWrangler.zModeKey):
            if (self.world.getDrawMode() == World.World.DRAW_DETAIL_DEPTH):
                self.world.setDrawMode(World.World.DRAW_DETAIL_PHYSICAL)                
            else:
                self.world.setDrawMode(World.World.DRAW_DETAIL_DEPTH)
            self.world.draw()
            return True
        elif (key == ToastWrangler.tabKey):
            if (self.world.getViewMode() == World.World.VIEW_VIEWER_INFORMATION):
                self.world.setViewMode(World.World.VIEW_TEAM_INFORMATION)
            else:
                self.world.setViewMode(World.World.VIEW_VIEWER_INFORMATION)
            self.world.draw()
            return True
        return False

    def doHelp(self):
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
            if (self.keysAvailableAnytime(key)):
                self.world.draw()
                continue
            if (key == ToastWrangler.helpKey):
                self.doHelp()
                pass
            if (not didAttack and key == ToastWrangler.attackKey):
                overlayOn = False
                self.attackOverlay.setCursorPosition(self.x, self.y)
                self.world.setOverlay(self.attackOverlay)
                self.world.draw()
                key = self.inputHandler.pauseForKey()
                self.keysAvailableAnytime(key)
                while (key != ToastWrangler.attackKey):
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
                didAttack = True
                
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
#                   if (key == 65): #a
#                       c = Creature.Creature()
#                       self.world.placeItem(c, 0, 0)

        

            self.world.draw()

        self.endTurn()
        return retVal
