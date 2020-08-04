import uepy
from uepy import log, logTB

class MyGameInstance:
    def __init__(self, engineObj):
        self.engineObj = engineObj
        log('MyGameInstance.__init__')

    def Init(self):
        log('MyGameInstance.Init') # I think either InitializePlayInEditor or InitializeStandalone are called *before* this one

    def OnStart(self):
        log('MyGameInstance.OnStart') # "Called when the game instance is started either normally or through PIE." - called after Init

    def Shutdown(self):
        log('MyGameInstance.Shutdown')

    def StartGameInstance(self):
        log('MyGameInstance.StartGameInstance') # I think this is called in a packaged game, while StartPlayInEditorGameInstance is called in PIE (and it should just call StartGameInstance)

    def OverrideGameModeClass(self, *args):
        log('MyGameInstance.OverrideGameModeClass')

