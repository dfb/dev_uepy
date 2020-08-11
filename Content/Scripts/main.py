from uepy import log, logTB
import uepy
from importlib import reload
import sys

# Capture sys.stdout/stderr
class OutRedir:
    def write(self, buf):
        log(buf)
    def flush(self):
        pass
    def isatty(self):
        return False
sys.stdout = OutRedir()
sys.stderr = OutRedir()
del OutRedir

# some stuff for interactive
__builtins__['reload'] = reload
__builtins__['uepy'] = uepy

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
        - uepy.umg has a UUserWidget class we can extend in python
        - on startup, create and register a UUserWidget subclass that does basically nothing
        - see if we can use it in UMG
        - expose just enough APIs for that child class to add a button or something
        - make sure it shows up in e.g. a parent BP widget or something
        - uepy.editor module
        - uepy.editor exposes a func to register a new nomad tab spawner
            - takes a menu name and a class to instantiate, then instantiates it and wraps it in an SDockTab
            - maybe it takes the module and class name so it can reload the module on open?
            - have it unregister any prior version of it first

        - delegates!
            - uepy defines FPyDelegate base class
            - FPyEditor, FPySlate, etc. child classes as needed
            - delegate constructor takes a py callable and stores it
            - delegate defines methods with all kinds of signatures as needed
        - add a BP widget and bind events to it
        - add a button to it that logs a message
        - expose to py the code necessary to launch the editor utility widget, instead of having the module do it
        - start exposing to py the stuff needed to build more editor utility widgets
        - expose to py a function for helping us detect editor vs game vs whatever
        - have main.py's Init, if in editor, import spawner module
        - flesh out spawner module and uepy.umg as needed
        - impl some stuff in spawner
            - filter/dropdown w/ actor classes + spawn button
            - delete and respawn selected
            - watch & reload

        - umg
            - create a UEditorUtilityWidget
            - compare notes with the plugin stuffs - which approach should we use?
            - learn how to make a widget in UMG editor but control it via C++ (and then python)
            - make a dummy PSO widget that has a button that spawns a MySO or something
            - finally maybe get into the work of tracking registered classes so we can make a list of them?

            - in BP, create some new UMG panel with logic behind it - a button that broadcasts a msg to actors to e.g. change their color
            - make a BP actor that responds to that event
            - bind a key to show/hide this umg panel (2d, over the 3d window)
            - make C++ & Py actors implement that interface and get it working
            - side quest: see if we can say that only the py actor implements it! - have REgisterPyClass take an optional list of interface classes
            - create another UMG panel, this time just in python, that does more or less the same thing
            - have a separate key show/hide it as well

        - side quest: experiment to see if we /could/ expose some uprops to the editor, e.g. an editor-editable int prop for starters
            - gonna need a UI button to spawn a python obj
            - if that works, see if we can successfully save a python actor in the map!!
            - if that works, see if we can also expose ufunctions too?? (maybe as a later 'todo')
        - noodle on organization some
            - uepy.classes, .structs, .enums? or better to have uepy.umg, .actor, .mesh, .material ? both? (thinking in terms of both classes but also supporting helper code)
            ue
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
    - OnConstruct
    - port game mode, instance, state, etc. out of BP
    - massive code cleanup to reduce all the duplication and cruft from the earlier hacking
    - what about calls to Super::??

UMG vs SLATE: it looks like we can now do UUserWidget subclasses for editor panels, such that it probably makes the most sense to invest in UMG-based stuffs
as opposed to dividing attention between slate and UMG (we can always add support for slate later if we need)

QOL soon
- don't require call to RegisterPythonSubclass - use a metaclass or something
- crash on import error of main
- reloadable modules - or maybe move this out of main to something that gets reloaded?
- prj.py needs to package up everything in Content/Scripts I think
- W i d e c h a r output during build for some reason
- UObject.GetName
- FVector/FRotator default args if omitted
- py console up/down arrow to go thru history

LATER
- the engine nulls out objs it kills, so we could have the tracker turn around and fiddle with the py obj - like set a flag in the
    py inst saying the engineObj is dead or something, and then have the py base classes check for self.engineObj is None
- in PIE, we leak a GameInstance each time you run (do we care? not sure)
- pyso spawner, py console like with UnrealEnginePython
- tools to auto-gen a lot of the binding code - template metaprogramming?, CppHeaderParser if needed
- interfaces defined in py and implementable by py?
    - we can declare that it implements the interface, but we have to register the functions of the interface

'''

