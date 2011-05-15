outFile = None

def init():
    global outFile
    outFile = open('log.txt', 'w')

def put(str = ''):
    outFile.write(str + '\n')
