import uepy
from uepy import log, logTB

class MyGameState:
    def __init__(self, engineObj):
        self.engineObj = engineObj
        log('MyGameState.__init__')

    def HandleBeginPlay(self):
        log('MyGameState.HandleBeginPlay')

