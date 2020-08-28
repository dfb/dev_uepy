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
    DestroyAllActorsOfClass(myactors.MySO)
    DestroyAllActorsOfClass(myactors.MyBob)

def OnModuleAfterReload(watcher, state):
    log('AFTER RELOAD!!!')
    if 0:
        for i in range(100):
            SpawnActor(GetWorld(), myactors.MySO)
    SpawnActor(GetWorld(), myactors.MyBob)

