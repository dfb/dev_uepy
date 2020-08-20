# imported by HackyWorldHookActor creating a SourceWatcher
from uepy import *
import os

MODULE_SOURCE_ROOTS = [
    os.path.dirname(__file__),
    os.path.join(FPaths.ProjectPluginsDir().replace('/', os.sep), 'uepy', 'Content', 'Scripts'),
]

import myactors

def OnModuleBeforeReload(watcher):
    log('before reload')
    DestroyAllActorsOfClass(myactors.MySO.engineClass)

def OnModuleAfterReload(watcher, state):
    log('AFTER RELOAD!!!')
    for i in range(100):
        SpawnActor(GetWorld(), myactors.MySO.engineClass)

