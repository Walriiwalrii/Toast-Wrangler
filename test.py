#!/usr/bin/python
import locale, curses, random

def getBlock():
	blocks = (u'\u2591', u'\u2592', u'\u2593', u'\u2588', ' ')
	return blocks[random.randint(0,len(blocks)-1)]

def blah(screen):
	screen.addstr('BLOOD DEMO v0.0000001')
	screen.refresh()
	screen.getch()

	dims = screen.getmaxyx()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	global code
	for r in range(100): #100 redraws
		for i in range(dims[0]-1):
			for j in range(dims[1]):
					screen.addstr(i,j,getBlock().encode('utf-8'), curses.color_pair(1))
		screen.refresh()
	screen.getch()

locale.setlocale(locale.LC_ALL, 'en_US.utf8')
curses.wrapper(blah)
