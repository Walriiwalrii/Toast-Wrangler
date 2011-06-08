import curses, random
import ToastWrangler
import Logger

class InputHandler:
    directionTranslator = {
        curses.KEY_A1:curses.KEY_A1,
        curses.KEY_UP:curses.KEY_UP,
        curses.KEY_A3:curses.KEY_A3,
        curses.KEY_LEFT:curses.KEY_LEFT,
        curses.KEY_RIGHT:curses.KEY_RIGHT,
        curses.KEY_C1:curses.KEY_C1,
        curses.KEY_DOWN:curses.KEY_DOWN,
        curses.KEY_C3:curses.KEY_C3,

        49: curses.KEY_C1,
        50: curses.KEY_DOWN,
        51: curses.KEY_C3,

        52: curses.KEY_LEFT,
        54: curses.KEY_RIGHT,

        55: curses.KEY_A1,
        56: curses.KEY_UP,
        57: curses.KEY_A3
        }
    directionOffset = {
            curses.KEY_A1 : (-1,-1), 
            curses.KEY_UP: (0, -1),
            curses.KEY_A3: (1, -1),
            curses.KEY_LEFT: (-1, 0), 
            curses.KEY_RIGHT: (1, 0), 
            curses.KEY_C1: (-1, 1), 
            curses.KEY_DOWN : (0, 1), 
            curses.KEY_C3 : (1,1)
        }

    def __init__(self, screen):
        self.screen = screen
        return

    @staticmethod
    def getRandomDirection():
        keys = InputHandler.directionOffset.keys()
        i = random.randint(0,len(keys)-1)
        return InputHandler.directionOffset[keys[i]]
    
    def getKey(self):
        raise ValueError('Base class InputHandler cannot supply valid keys!')

    @staticmethod
    def keyToOffset(key, translate = True):
        if (translate and key in InputHandler.directionTranslator):
                key = InputHandler.directionTranslator[key]
        if (not key in InputHandler.directionOffset):
            raise ValueError('Invalid key: %s' % (str(key)))

        return InputHandler.directionOffset[key]

    def getDirection(self, allowEscape = False):
        while (True):
            k = self.waitForKey()
            if (k in InputHandler.directionTranslator):
                return InputHandler.directionTranslator[k]
            if (allowEscape and k == ToastWrangler.quitKey):
                return k
            Logger.put('Rejected: %d' % (k))

        

class KeyboardInputHandler(InputHandler):
    def __init__(self, screen):
        InputHandler.__init__(self, screen)
        self.defaultPauseTime = 500 #500ms

    def getDefaultPauseTime(self):
        return self.defaultPauseTime

    def waitForKey(self):
        self.screen.nodelay(0)
        ret = self.getKey()
        self.screen.nodelay(1)
        return ret

    def pauseForKey(self, pauseTime = None): #pauseTime in milliseconds
    
        if (pauseTime == None):
            pauseTime = self.defaultPauseTime

        assert(pauseTime >= 100 and pauseTime <= 255 * 100)
        self.screen.nodelay(1)
        curses.halfdelay(int(pauseTime / 100))
        ret = self.getKey(False)
        #curses.nocbreak()
        #curses.cbreak()
        #self.screen.nodelay(0)
        return ret

    def getKey(self, retry = True):
        while (True):
            try:
                key = self.screen.getch()
                #Logger.put('Key: %d' % (key))
                if (key == ToastWrangler.quitKey): #escape key
                        ToastWrangler.setQuit()
                return key
            except ValueError:
                if (retry):
                    continue
                else:
                    return -1
