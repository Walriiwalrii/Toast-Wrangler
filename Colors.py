import curses
import Logger
import sys

colorPairs = None

BLACK = curses.COLOR_BLACK
BLUE = curses.COLOR_BLUE
CYAN = curses.COLOR_CYAN
GREEN = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
RED = curses.COLOR_RED
WHITE = curses.COLOR_WHITE
YELLOW = curses.COLOR_YELLOW

BOLD = curses.A_BOLD
BLINK = curses.A_BLINK
UNDERLINE = curses.A_UNDERLINE

colors = [BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW ]
colorValueToName = {
    BLACK : "BLACK",
    BLUE : "BLUE",
    CYAN : "CYAN",
    GREEN : "GREEN", 
    MAGENTA : "MAGENTA",
    RED : "RED",
    WHITE : "WHITE",
    YELLOW : "YELLOW"
    }

colorNameToValue = {
    "BLACK" : BLACK,
    "BLUE" : BLUE,
    "CYAN" : CYAN,
    "GREEN" : GREEN, 
    "MAGENTA" : MAGENTA,
    "RED" : RED,
    "WHITE" : WHITE,
    "YELLOW" : YELLOW
    }


def getPairNumber(foreground, background): #given strings representing the colors, returns that color pair
    global colorPairs
    global colorValueToName
    return curses.color_pair(colorPairs[colorNameToValue[background]][colorNameToValue[foreground]])


def init():
    global colorPairs

    Logger.put('%d color pairs supported.' % (curses.COLOR_PAIRS))
    Logger.put('curses.hasColors() = %d' % (curses.has_colors()))

    if (colorPairs != None):
        Logger.put('Colors.init() called more than once!')
        return
    if (curses.COLOR_PAIRS < 64):
        Logger.put('Cannot start unless there is support for 64 color pairs or more!')
        Logger.put('Your system has: %d pairs.' % (curses.COLOR_PAIRS))
        sys.exit(1)

    pairCount = 1
    colorPairs = {}
    for c1 in colors:
        colorPairs[c1] = {}
        for c2 in colors:
#            if (c2 == WHITE and c1 == BLACK):
#                continue
            #Logger.put('%s & %s = %d' % (colorValueToName[c2], colorValueToName[c1], pairCount))
            curses.init_pair(pairCount, c2, c1)
            colorPairs[c1][c2] = pairCount
            pairCount = pairCount + 1
    colorPairs[BLACK][WHITE] = 0
    #Logger.put('%s' % (str(colorPairs)))


