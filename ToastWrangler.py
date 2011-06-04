import curses
import curses.wrapper

import InputHandler
import World

import Logger
import Colors

import locale, sys, random, time

encoding = None
screen = None

shouldQuit = False

quitKey         = ord('Q') 

zModeKey        = ord('z')
tabKey          = ord('\t')
attackKey       = ord('a')

enterKey        = ord('\n')
spaceKey        = ord(' ')

helpKey         = ord('/')
qKey            = ord('q')
lightToggleKey  = ord('l')

PLAYER_TEAM     = 999

def setQuit(quitStatus = True):
    global shouldQuit
    shouldQuit = quitStatus

def getShouldQuit():
    global shouldQuit
    return shouldQuit

def doIntro(screen):
    quit = False
    key = -1
    screen.nodelay(0)
    for l in open('tutorial.txt'):
        screen.addstr(l)
        screen.refresh()
        #time.sleep(0.100)
        
    while (not quit):
        coords = screen.getmaxyx()
        try:
            key = screen.getch()    
        except ValueError:
            continue
        if (key != -1):
            break
    screen.nodelay(1)
    screen.clear()
    screen.refresh()

    
def launchGame(screenParam):
    global screen
    screen = screenParam
    Colors.init()
    curses.curs_set(1)
    screen.keypad(1)
    screen.nodelay(1)

    doIntro(screenParam)

    #val = k.getKey()

    #screen.addstr(2, 1, "%d" % (val))

    w = World.World(screen, 80, 30)
    w.doEventLoop()
    
def go():
    print 'Initializing Toast Wrangler... ',
    global encoding
    locale.setlocale(locale.LC_ALL,"en_US.utf8")
    encoding = locale.getpreferredencoding()

    Logger.init()
    print 'Done!'
    curses.wrapper(launchGame)
    print 'Thank you for playing Toast Wrangler.'
