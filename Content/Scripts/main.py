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

THIS WEEK
- figure out how to handle R/W props on C++ classes - how that gets expressed in the PGLUE class
- create a baseline scriptrunner actor
- some way to configure uepy to use fully-qualified class names or not
- design and build a better way for dev mode, source watcher, etc. to exist
    - or at least clean it all up so that it's easy to enable it in a prj
        - spawn a sourcewatcher actor and persist it to your level
        - on begin play, have your level BP do it perhaps
        - but make it so that no other steps are required beyond that
        - what about in a built package? I think we have to have CGameState spawn one, after checking command line args
    - a little tricky right now since we don't have GameState/GameInstance written in Python yet
- document the "preferred" dev process
    - while modus (or at least PIE) are running, prolly in 2D mode, but maybe not so you can quickly get in VR and try it?
    - UEPYAssistantActor

NEXT WEEK, MAYBE
- fix leaking of bound delegates
- make dev mode work only in certain scenarios, e.g. a command line param is present or in editor
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
                        - a lot of the above could be logic in the relevant actors, so maybe for now our main use case is just the
                            global scriptrunner for demos and stuff, though it might be nice to have some helper scripts at some point
                            that are possibly running independently of the global one
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
        - is there some way to tell the nomad tab spawner to rebuild its widget? if so, we could maybe have it listen for changes?
            (this might be too much to ask for a nomad tab spawner, though we do want a lot of this functionality for normal actors and such)

        - fix leaking of delegates
        - fix crappy thing we do to keep delegates alive

        - expose to py a function for helping us detect editor vs game vs whatever
            - build vs prj.py run (CLI) vs PIE vs in editor pre-PIE

        - side quest: experiment to see if we /could/ expose some uprops to the editor, e.g. an editor-editable int prop for starters
            - if that works, see if we can also expose ufunctions too?? (maybe as a later 'todo')
        - start making Compile button not cause us to completely blow up

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

QOL soon
- keep delegates alive w/o saving a ref to them
- crash on import error of main
- prj.py needs to package up everything in Content/Scripts I think
- W i d e c h a r output during build for some reason
- UObject.GetName
- py console up/down arrow to go thru history
- py::str <--> FString, (note that we first have to expose FString via pybind11, then py::implicitly_convertible<py::str, FString>()
- default 3rd arg on createwidget call
- since in c++ only the bridge class implements the interface, we will have duplication of code, e.g. every subclass of AActor that in
    turn has a shim class for python will expose BeginPlay and have an impl for it. Maybe instead we can have some macro that defines
    all of the "standard" APIs we expose for all AActor subclasses, and then the shim classes have to define only new stuff in addition to
    that?

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
- impl a couple of operator overloads to see how they work, e.g. FVector + FVector
- APIs that take a UObject (e.g. uepy.CreateDynamicMaterialInstance) - can we let them pass foo.engineObj or just foo instead? like w/ classes?
- for instance type checking:
    expose a UObject API: is_a(UObjec& self, PyOrUClassObj klass) # for the plain uobj wrapped in py case
    expose on IPyBridgeMixin: .is_a(UClass), .is_a(py::class_)
    also is_subclass maybe?
    hmm, these are pretty tricky, because PyOrUClass stuff automatically takes us all the way up the inheritance tree to the glue class,
    so it could easily result in is_a=true for cases where it's not - maybe we require UClass params in that case? and then if you
    need to do py, you use isinstance like normal?
- hrm, auto-calls to super: if you don't override BeginPlay in our fake subclassing, does SuperBeginPlay get called like it should?
    - maybe instead of a for-sure call to e.g. BeginPlay, we test if it's present and if not we call super?
'''

