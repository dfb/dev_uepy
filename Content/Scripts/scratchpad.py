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
    DestroyAllActorsOfClass(myactors.SubSO)

def OnModuleAfterReload(watcher, state):
    log('AFTER RELOAD!!!')
    if 0:
        for i in range(100):
            SpawnActor(GetWorld(), myactors.MySO)
    SpawnActor(GetWorld(), myactors.MyBob)

    klass = StaticLoadObject(UBlueprintGeneratedClass, '/Game/SomeBPActor.SomeBPActor_C')
    log('KLASS?', klass, klass.GetName() if klass else '???')
    actor = SpawnActor(GetWorld(), klass, speed=1, rotating=True, moveAmount=FVector(0,0,0.1), label='what is is, yo!')
    #actor.Set('speed', 1)
    #actor.Set('rotating', True)
    #actor.Set('label', 'bonkers')
    #actor.Set('moveAmount', FVector(0,0,0.1))
    #actor.Set('someStrings', ['one', 'two', 'tree'])
    #actor.Set('someInts', [9, 5, 1, 11, 1000, 1, 2, 3, 3, 2, 1, -1, -2, -3, -4, -5])
    #actor.Set('someBools', [not not 'what', False, 0, None, True, 1, not not 'dave', False, 0, None, 1, True])

    #m = FMyStruct()
    #m.moveAmount = FVector(-0.05, 0, 0.1)
    #m.rotating = True
    #actor.Set('structProp', m)

