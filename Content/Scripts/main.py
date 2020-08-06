from uepy import log, logTB
from importlib import reload

# AVOID module-level stuff with side effects!

def Init():
    '''called from ue4 when this module is loaded on startup (or, in dev, when the c++ game module is recompiled'''
    log('main.Init called')

import myactors

def OnPreBeginPIE():
    log('main.OnPreBeginPIE called')
    global myactors
    myactors = reload(myactors)

'''
replication? C->S events, S->multicast events, replicated variables & their initial state on a joining client

for each class we want to extend in py:
- create a CPP class
- create a Py class

for each method we want to be able to override in py:
- CPP half has a pass-through impl that calls the py inst
- CPP half probably also has a Super version (e.g. for BeginPlay we also create SuperBeginPlay that calls Super::BeginPlay)
- PY half has a default impl that is empty except it calls the Super method

for each API we want to be able to call from PY
- pybind exposes wrapper for that API (both for "us" but for other code that gets a pointer to one of these objs)
- for subclasses, PY half has a trampoline method that calls same API on self.engineObj

TODO
- impl a couple of operator overloads to see how they work, e.g. FVector + FVector

KEEPING ME UP AT NIGHT
(and for each, the risk: is it just a lot of work, is it the complexity, is it the unknowns?)
1) exposing APIs/vars/events: duplication of code, maintenance, DRY - this one has me worried
DONE - 2) object ownership / lifecycle - doable, just unfun
3) replication, inl initial state repl - doable, but may cause us to completely invent our own
    - or not, if we can solve the get-rid-of-Become problem, and the C++ class uprops any state vars (e.g. config)
4) interaction with legacy BP stuff (gamestate, gamemode) - doable, but maybe because we completely rip out the old stuff. also depends on replication if we go that route
    - maybe not: those things are callable from C++, no?
5) delegate binding - doable, just need to invent something probably
    - make c++ delegates work, but then invent something for just-py delegates for when we get to e.g. pygameinstance and all pySOs
6) mem leaks, packaged build issues, misc gremlins - doable, and hopefully less of an issue due to less code?

based on the above, I think if I can get comfortable with #1, we can really commit to this path overall.
    Stuff to achieve:
        - support for array params and return values
        - impl MyGameMode and have MyGameInstance return its class
        - have MyGameMode return/create MyGameState
        - impl MyGameState in C++ and py & on begin play (or periodically in tick), spawn some chairs
        - delegates
        - impl far more engine APIs callable from python

Hmm... no, doing all of that manually for now wouldn't be that bad - unfun, but definitely doable even if lots of DRY violations.

at this point, it seems like everything except testing it in a build is in the "can do, just need to go do it" camp, with the first item on that list
being the housekeeper, because we can't really get very far without that. New plan:
    TODO
        - just to push things along:
            - verify all works in a build
        - sidebar: experiment to see if we /could/ expose some uprops to the editor, e.g. an editor-editable int prop for starters
            - gonna need a UI button to spawn a python obj
            - if that works, see if we can successfully save a python actor in the map!!
        - noodle on organization some
            - uepy.classes, .structs, .enums?
            - org of plugin-supplied C++ and py code - where does that all live in the filesystem, how is it managed?
        - do something with umg
        - do something with binding to a delegate event
        - figure out module reloading - any way to auto reload stuff if we're in PIE? or maybe on prepie start we just reload everything in order anyway?
        - start making Compile button not cause us to completely blow up
        - and then... maybe see if we can get UnrealEnginePython to coexist with uepy?
            - if so, bring it into 4.23 and get scriptrunner moved over to uepy


    - add rudimentary uepy plugin to modus 4.23
    - start hacking until we have 1 fully functional PSO
    - add in a py-based configurator
    - again, verify in a packaged build
    - tackle things like event binding, replication, spawning
    - port existing PSOs while also adding in helpers to reduce manual stuffs
    - get scriptrunner working again
    - port all the remaining py stuff and rip out UnrealEnginePython
    - port game mode, instance, state, etc. out of BP
    - massive code cleanup to reduce all the duplication and cruft from the earlier hacking
    - what about calls to Super::??

QOL soon
- crash on import error of main
- reloadable modules - or maybe move this out of main to something that gets reloaded?
- prj.py needs to package up everything in Content/Scripts I think

LATER
- the engine nulls out objs it kills, so we could have the tracker turn around and fiddle with the py obj - like set a flag in the
    py inst saying the engineObj is dead or something
- in PIE, we leak a GameInstance each time you run (do we care? not sure)
- pyso spawner, py console like with UnrealEnginePython
- tools to auto-gen a lot of the binding code - template metaprogramming?, CppHeaderParser if needed

'''

