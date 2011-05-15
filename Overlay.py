import curses
import Colors

class Overlay:
	def __init__(self, world):
		self.world = world

	def getDrawTuple(self, x, y, viewer, lighting):
		viewerCoords = viewer.getLocation()
		retVal = self.world.world[x][y].getDrawTuple(viewer, lighting)
		if (x == viewerCoords[0] and y == viewerCoords[1]):
				retVal = (retVal[0], retVal[1]  | curses.A_BLINK)	
		return retVal

class CanAttackOverlay(Overlay):
	def __init__(self, world, creature):
		Overlay.__init__(self, world)
		self.creature = creature
		self.cursorPosX = 0
		self.cursorPosY = 0
		self.attackAttribute = Colors.getPairNumber('WHITE', 'RED') | curses.A_BOLD
	def getDrawTuple(self, x, y, viewer, lighting):
		worldTuple = self.world.world[x][y].getDrawTuple(viewer, lighting)
		if (x == self.cursorPosX and y == self.cursorPosY):
			return ('X', self.attackAttribute)
		if (self.creature.canAttack(x,y)):
			return (worldTuple[0], self.attackAttribute)
		return worldTuple
	def setCursorPosition(self, x, y):
		self.cursorPosX = x
		self.cursorPosY = y
	def adjustCursorPosition(self, xDiff, yDiff):
		newX = self.cursorPosX + xDiff
		newY = self.cursorPosY + yDiff
		if (self.creature.canAttack(newX,newY)):
			self.cursorPosX = newX
			self.cursorPosY = newY
			return True
		return False

