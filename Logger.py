import sys

outFile = None

def init():
    global outFile
    outFile = open('log.txt', 'w')

def put(str = ''):
    outFile.write(str + '\n')

def fatal(str = ''):
    msg = 'FATAL ERROR ' + str
    sys.stderr.write(msg)
    put(msg)
    sys.exit(1)
