from uepy import log, logTB
import uepy

try:
    # Add any 3rd party libs to sys.path
    import deps
    deps.Discover()
except:
    logTB()

def Init():
    '''called from ue4 when this module is loaded on startup (or, in dev, when the c++ game module is recompiled'''
    log('main.Init called')

# AVOID module-level stuff with side effects?
# TODO: we need better rules around what happens at module scope vs Init (and if Init is needed at all)
import myactors

try:
    import uepy.editor
    import editor_spawner
except ImportError:
    pass # not in editor

def OnPreBeginPIE():
    log('main.OnPreBeginPIE called')
    global myactors
    myactors = reload(myactors)

'''
replication? C->S events, S->multicast events, replicated variables & their initial state on a joining client

TODO
- impl a couple of operator overloads to see how they work, e.g. FVector + FVector

KEEPING ME UP AT NIGHT
(and for each, the risk: is it just a lot of work, is it the complexity, is it the unknowns?)
3) replication, inl initial state repl - doable, but may cause us to completely invent our own
    - or not, if we can solve the get-rid-of-Become problem, and the C++ class uprops any state vars (e.g. config)
4) interaction with legacy BP stuff (gamestate, gamemode) - doable, but maybe because we completely rip out the old stuff. also depends on replication if we go that route
    - maybe not: those things are callable from C++, no?

big projects / areas
- UMG / configurators (at some point: support for Ken's BP widgets or reimplement in C++/Python)
- delegates
- exposing more APIs, classes, structs, enums
- code cleanup, better macros, less repetition

classes plan
- make sure all exposed APIs that want a UClass now take a py::object& instead
- clean up py code to not ever have to call StaticClass! (fix any existing exposed APIs that take a UClass too, of course)

- in editor, see if we can auto-spawn the source watcher actor right after PIE if it's not present

- for now at least, still have pyClassMap in C++ to get from registered name to pyclass
- uepy exposes some sort of PyInst(UObject) func that returns the py instance or None
- APIs that take a UObject instance param - is there some way to let them take a pyinst as well and, in that case, auto get inst.engineObj?
    - is this needed? if so, what are some examples?
- for instance type checking:
    expose a UObject API: is_a(UObjec& self, PyOrUClassObj klass) # for the plain uobj wrapped in py case
    expose on IPyBridgeMixin: .is_a(UClass), .is_a(py::class_)

THIS WEEK
- make a better spawner tab that shows them all in a dropdown, and lets you spawn/respawn currently selected
- fix leaking of bound delegates
- make dev mode work only in certain scenarios, e.g. a command line param is present or in editor
- have a shortcut in uepy (so you can easily enter it from the py console) to spawn the hacky editor thing into the level
- start on a new and improved todo list

- remote access?
    - main.py or another module starts up a dev remote server for a web interface with:
        - logging w/ filtering
        - repl
        - maybe some custom buttons to trigger in-process actions

NEW DEV PROCESS TODO

- make uepy.devserver module
    - websocket connection
    - just supply a python class that does a websocket - real repl instead of repl in browser!
    - svelte-based UI + Ken's css thang (maybe later? we could probably get by with a single HTML file at first)
        wait, isn't there some thing built into python that does this already
    - on launch, use webbrowser.open to open the dev UI
    - setup websock conn
    - make uepy hook to get log output
    - repl support

    TODO
        - does our current approach to dev'ing SOs match the ideal or is it more based on how we used to dev BP SOs? What is the ideal?
            - goal: invest in making it so that dev'ing SOs in PIE vs build vs editor is pretty much the same
                - sidesteps all the weird issues with moving back and forth between PIE and editor
                - WYSIWYG because we're not building against editor mode
                - I think we can have an improved developer experience too
            - features
                - a remote repl so you can do interactive stuff
                - a log viewer
                - (maybe both the log viewer and the repl are web-based?)
                - repl includes some handy utils like inspecting scene/actors easily, loading a space, etc.
                - auto-reload of modified modules, with failsafe so that syntax errors, uncaught exceptions, etc. don't require a restart
                - some way to easiy load and run scripts too
            - hrm
                - we have several big features
                    - the remote control feature we played with for a bit
                    - SO dev process
                    - programmatic/parametric space construction
                    - scriptrunner
                    - production log viewer
                    - runtime debugging
                    - scriptable behaviors (light switches, control panels for blinds, auto-on lights, modify mood lighting)
                        - eventually, parts of modus itself could be rewritten as little snippets of code like this:
                            - load/save space
                            - resize space
                            - reset space
                            - see different space configurations
                - might they all be unified under a single umbrella feature?
                    - still have recording/playback support
                    - some standard way to tell modus to launch w/ a particular startup script
                    - modus.py provides a library of APIs for "doing stuff" specific to modus (load space, spawn SOs, record/play)
                    - modus_dev.py provides utils related to development (reloading SOs and dependencies)
                    - need some standard way to spawn a "script actor" that runs a snippet of code (one shot or stay alive and respond to
                        commands, etc.)
                        - including some way to easily make them load on start (use the startup script)
                    - the big hurdle seems to be that gameplay scripts need to by async in nature, while SOs, gamestate, etc. are more
                        manually managed to be finegrained pieces. They should share the same API in every way possible though.
                        - could we provide a common library that exposes a sync and an async API? Or maybe you access it through some API
                            object, and you request either a sync or an async instance?
                    - the solution, long term, is to always be async, i.e. get to the point where py SOs don't care about OnTick and such
                        and don't directly call into the engine too much either. Instead, we get to the point where SOs are built using
                        an API layer that we've built, one that is inherently async.
                    - to do this, we need to have a very well-defined interface for SOs in terms of what interactions you can do with them,
                        what they can do, and so on.
                - for now at least, it looks like we have two Python silos we have to stick with, until we can create a higher level, async
                    API layer for creating SOs:
                        - scripting interface: scriptable behaviors, demo scripts (scriptrunner)
                        - "programming" interface: SOs

            - what if on game start, we used python code to set things up how we want, e.g. load a space, spawn an actor, etc.
            - as part of that, it sets up code to watch one or more actors, or all actors of a class
            - on tick, we check to see if any dependencies have changed. if so, kill relevant actors, reload modules in order, respawn at locations
                - any way to get their other state and restore it? (make this generic and then for modus we can get/set state normally)
        - lib routine:
            - given a python obj, find its class' module
            - find all the filenames of all the modules it's based on
                - maintain some sort of ordering of who depends on whom
            - note their lastmod times
            - at any time, get a snapshot of all modules that have changed (again, in order)
        - later
            - dropdown with all known classes + refresh button to regen list of classes
            - spawn currently selected in drop down
            - "watch" checkbox to automatically kill & respawn obj as it changes (auto save loc/rot and use on respawn)
            - editbox+load button for loading space file
            - button to dump info on selected objects
        - have some py func that, given a py class for a UClass, can find the modules the py class depends on, track when they were last modified,
            and provide some reload API that you can call to reload any that have changed since last reload
        - have nomad tab spawner use this to reload the py modules right before creating the UUserWidget for the tab
        - is there some way to tell the nomad tab spawner to rebuild its widget? if so, we could maybe have it listen for changes?
            (this might be too much to ask for a nomad tab spawner, though we do want a lot of this functionality for normal actors and such)

        - fix leaking of delegates
        - fix crappy thing we do to keep delegates alive

        - create a UMG test actor
            - on start, creates a particular widget and adds it to the viewport
            - on tick, see if the widget's file has changed
            - if it has changed, remove the old widget, reload the widget's module, and add the widget to the viewport again

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

UMG vs SLATE: it looks like we can now do UUserWidget subulasses for editor panels, such that it probably makes the most sense to invest in UMG-based stuffs
as opposed to dividing attention between slate and UMG (we can always add support for slate later if we need)

?? should all the Cast methods use a reference return policy??

QOL soon
- don't require call to RegisterPythonSubclass - use a metaclass or something
- keep delegates alive w/o saving a ref to them
- crash on import error of main
- prj.py needs to package up everything in Content/Scripts I think
- W i d e c h a r output during build for some reason
- UObject.GetName
- py console up/down arrow to go thru history
- py::str <--> FString
- default 3rd arg on createwidget call
- since in c++ only the bridge class implements the interface, we will have duplication of code, e.g. every subclass of AActor that in
    turn has a shim class for python will expose BeginPlay and have an impl for it. Maybe instead we can have some macro that defines
    all of the "standard" APIs we expose for all AActor subclasses, and then the shim classes have to define only new stuff in addition to
    that?
- all py actors tick all the time - make that configurable

LATER
- the engine nulls out objs it kills, so we could have the tracker turn around and fiddle with the py obj - like set a flag in the
    py inst saying the engineObj is dead or something, and then have the py base classes check for self.engineObj is None
- in PIE, we leak a GameInstance each time you run (do we care? not sure)
- pyso spawner, py console like with UnrealEnginePython
- tools to auto-gen a lot of the binding code - template metaprogramming?, CppHeaderParser if needed
- interfaces defined in py and implementable by py?
    - we can declare that it implements the interface, but we have to register the functions of the interface
- a BPCall function, for calling BP from C++ / Python
    - BPCall(obj, funcName, argsProbablyWithTypeInfo) --> one or more return values
    - use obj->class->FindFunction, obj->ProcessEvent
    https://answers.unrealengine.com/questions/516440/ufunction-invoke.html
    https://answers.unrealengine.com/questions/7732/a-sample-for-calling-a-ufunction-with-reflection.html
    https://answers.unrealengine.com/questions/432681/how-to-pass-an-object-param-into-processevent.html
    https://forums.unrealengine.com/development-discussion/c-gameplay-programming/112236-call-ufunction-with-return-value-via-reflection
    https://forums.unrealengine.com/development-discussion/c-gameplay-programming/1508108-is-it-possible-to-infer-parameter-types-of-a-ufunction-in-code
    https://forums.unrealengine.com/development-discussion/c-gameplay-programming/1665895-pass-fstring-as-a-parameter-to-uobject-processevent-ufunction-void
    https://answers.unrealengine.com/questions/135649/how-could-i-call-a-blueprint-function-from-a-c-cod.html
    https://answers.unrealengine.com/questions/247249/call-a-blueprint-function-from-c.html
    https://answers.unrealengine.com/questions/116529/call-blueprint-functions-from-c.html
    https://github.com/iniside/ActionRPGGame/blob/master/Source/ActionRPGGame/Private/UI/Menu/ARLoginScreenView.cpp
'''

