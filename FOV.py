"FOV calculation for roguelike"
"originally from: http://roguebasin.roguelikedevelopment.org/index.php?title=Python_shadowcasting_implementation"

import curses, math, random
import Logger

FOV_RADIUS = 10

dungeon =  ["###########################################################",
            "#...........#.............................................#",
            "#...........#........#....................................#",
            "#.....................#...................................#",
            "#....####..............#..................................#",
            "#.......#.......................#####################.....#",
            "#.......#...........................................#.....#",
            "#.......#...........##..............................#.....#",
            "#####........#......##..........##################..#.....#",
            "#...#...........................#................#..#.....#",
            "#...#............#..............#................#..#.....#",
            "#...............................#..###############..#.....#",
            "#...............................#...................#.....#",
            "#...............................#...................#.....#",
            "#...............................#####################.....#",
            "#.........................................................#",
            "#.........................................................#",
            "###########################################################"]

class LightMap(object):
    epsilon = 1.0
    # Multipliers for transforming coordinates to other octants:
    mult = [
                [1,  0,  0, -1, -1,  0,  0,  1],
                [0,  1, -1,  0,  0, -1,  1,  0],
                [0,  1,  1,  0,  0, -1, -1,  0],
                [1,  0,  0,  1, -1,  0,  0, -1]
            ]
    def __init__(self, world, x, y, intensity = 10.0, enabled = True):
        self.world = world
        self.width, self.height = self.world.getDimensions()
        self.light = []
	self.changeIntensity(intensity)
	self.changed = True
	self.changePosition(x,y)
	self.setEnabled(enabled)
	self.resetMap()

    def setEnabled(self, newEnabled):
	assert(newEnabled == True or newEnabled == False)
	self.enabled = newEnabled
	self.changed = True

    def changePosition(self, newX, newY):
	assert(newX >= 0 and newY >= 0)
	self.x = newX
	self.y = newY
	self.changed = True

    def changeIntensity(self, newIntensity):
	newIntensity = float(newIntensity)
	assert(newIntensity > 0.0)
	self.changed = True
	self.intensity = newIntensity

    def resetMap(self):
	self.light = []
        for i in range(self.height):
            self.light.append([0.0] * self.width)
	
    def getLightAt(self, x, y):
	if (not self.enabled):
		return 0.0
	else:
		return self.square(x,y)

    def square(self, x, y):
        return self.light[y][x]

    def blocked(self, x, y):
        return (x < 0 or y < 0
                or x >= self.width or y >= self.height
                or self.world.getBlocksSight(x,y))

    def lit(self, x, y):
        return self.square(x,y) > 0.0

    def set_lit(self, x, y, distance):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.light[y][x] = distance
	    if (self.square(x,y) < LightMap.epsilon):
		self.light[y][x] = 0.0

    def _cast_light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
        "Recursive lightcasting function"
        if start < end:
            return
        radius_squared = radius*radius
        for j in range(row, radius+1):
            dx, dy = -j-1, -j
            blocked = False
            while dx <= 0:
                dx += 1
                # Translate the dx, dy coordinates into map coordinates:
                X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
                # l_slope and r_slope store the slopes of the left and right
                # extremities of the square we're considering:
                l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
                if start < r_slope:
                    continue
                elif end > l_slope:
                    break
                else:
                    # Our light beam is touching this square; light it:
		    distSquared = dx*dx + dy*dy
                    if distSquared < radius_squared:
                        self.set_lit(X, Y, radius - math.sqrt(distSquared))
                    if blocked:
                        # we're scanning a row of blocked squares:
                        if self.blocked(X, Y):
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                    else:
                        if self.blocked(X, Y) and j < radius:
                            # This is a blocking square, start a child scan:
                            blocked = True
                            self._cast_light(cx, cy, j+1, start, l_slope,
                                             radius, xx, xy, yx, yy, id+1)
                            new_start = r_slope
            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break
    def do_fov(self):
	if (self.changed):
		self.changed = False
		self.resetMap()
		if (not self.enabled):
			return
		radius = int(math.ceil(self.intensity))
		"Calculate lit squares from the given location and radius"
		for oct in range(8):
		    self._cast_light(self.x, self.y, 1, 1.0, 0.0, radius,
		                     self.mult[0][oct], self.mult[1][oct],
		                     self.mult[2][oct], self.mult[3][oct], 0)

		#Lights at a particular position always light up the position they are at
		self.set_lit(self.x, self.y, self.intensity)

    def display(self, s, X, Y):
        "Display the map on the given curses screen (utterly unoptimized)"
        dark, lit = curses.color_pair(8), curses.color_pair(7) | curses.A_BOLD    
        for x in range(self.width):
            for y in range(self.height):
                if self.lit(x, y):
                    attr = lit
                else:
                    attr = dark
                if x == X and y == Y:
                    ch = '@'
                    attr = lit
                else:
                    ch = self.square(x, y)
                s.addstr(y, x, ch, attr)
        s.refresh()
        

def color_pairs():
    c = []
    for i in range(1, 16):
        curses.init_pair(i, i % 8, 0)
        if i < 8:
            c.append(curses.color_pair(i))
        else:
            c.append(curses.color_pair(i) | curses.A_BOLD)
    return c


if __name__ == '__main__':
    try:
        s = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        color_pairs()
        s.keypad(1)
        x, y = 36, 13
        map = Map(dungeon)
        while True:
            map.do_fov(x, y, FOV_RADIUS)
            map.display(s, x, y)
            k = s.getch()
            if k == 27:
                break
            elif k == 259:
                y -= 1
            elif k == 258:
                y += 1
            elif k == 260:
                x -= 1
            elif k == 261:
                x += 1
    finally:
        s.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        print "Normal termination."

