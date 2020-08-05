import uepy
from uepy import log, logTB
import random, math, os

moduleDir = os.path.abspath(os.path.dirname(__file__))

def Init():
    '''called from ue4 when this module is loaded on startup (or, in dev, when the c++ game module is recompiled'''
    log('ue_startup.Init called')

'''
replication? C->S events, S->multicast events, replicated variables & their initial state on a joining client

for each class we want to extend in py:
- create a CPP class
- create a Py class

for each method we want to be able to override in py:
- CPP half has a pass-through impl that calls the py inst
- PY half has a default impl

for each API we want to be able to call from PY
- pybind exposes wrapper for that API (both for "us" but for other code that gets a pointer to one of these objs)
- for subclasses, PY half has a trampoline method that calls same API on self.engineObj

TODO
- impl a couple of operator overloads to see how they work, e.g. FVector + FVector

LATER
? pyso spawner, py console like with UnrealEnginePython
? how to implement game mode, game state, game instance in py?
? tools to auto-gen a lot of the binding code - template metaprogramming?, CppHeaderParser if needed

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
        - start work on housekeeper (custom holder class?)
        - extend actor to manage its own components, add some new components, update the mesh at runtime, etc.
        - delegates
        - impl far more engine APIs callable from python
        - member vars read/write

Hmm... no, doing all of that manually for now wouldn't be that bad - unfun, but definitely doable even if lots of DRY violations.

at this point, it seems like everything except testing it in a build is in the "can do, just need to go do it" camp, with the first item on that list
being the housekeeper, because we can't really get very far without that. New plan:
    - module loading order
        - want our py classes to be "always" available, e.g. BP Spawn Actor From Class can use them
        - plugin classes and py modules need to be loaded before game stuffs
            - want game module to be able to build on uepy builtin
        - gotta work in builds, too

    END GOAL
        - stuff runs properly in a working build
        - in editor, py classes are available "always"
        - game module on load can patch uepy module
        - uepy.AsACActor, .AsActor, .etc methods (some provided by game module)

    TODO
        - can we add classes to uepy instead of in a separate embedded module?
        - just to push things along:
            - have CActor not have a mesh comp, but add it all via python
            - have py actor add a child comp or two as well
        - have a CActor delegate member (or maybe there already is one) and bind/unbind a listener on it


    - add rudimentary uepy plugin to modus 4.23
    - start hacking until we have 1 fully functional PSO
    - verify ok in a packaged build
    - add in a py-based configurator
    - again, verify in a packaged build
    - tackle things like event binding, replication, spawning
    - port existing PSOs while also adding in helpers to reduce manual stuffs
    - get scriptrunner working again
    - port all the remaining py stuff and rip out UnrealEnginePython
    - port game mode, instance, state, etc. out of BP
    - massive code cleanup to reduce all the duplication and cruft from the earlier hacking

QOL soon
- crash on import error of engine_startup
- reloadable modules - or maybe move this out of engine_startup to something that gets reloaded?

LATER
- the engine nulls out objs it kills, so we could have the tracker turn around and fiddle with the py obj - like set a flag in the
    py inst saying the engineObj is dead or something
- in PIE, we leak a GameInstance each time you run (do we care? not sure)

'''
class PSketchObject:
    # TODO: either auto-gen all this or, better yet, couldn't we inject the methods and properties directly from c++?
    def __init__(self, engineObj):
        self.engineObj = engineObj
        log('PSketchObject.__init__', engineObj)

    def GetWorld(self): return self.engineObj.GetWorld()
    def SetActorLocation(self, v): return self.engineObj.SetActorLocation(v) # this works because engineObj is a pointer to a real instance, and we will also write wrapper code to expose these APIs anyway
    def SetActorRotation(self, r): self.engineObj.SetActorRotation(r)
    def BeginPlay(self): pass

    @property
    def mesh(self): return self.engineObj.mesh

rock = uepy.LoadMesh('/Game/StarterContent/Props/SM_Rock.SM_Rock')
couch = uepy.LoadMesh('/Game/StarterContent/Props/SM_Couch.SM_Couch')
meshes = [rock, couch]
masterMat = uepy.LoadMaterial('/Game/MasterMat.MasterMat')
textures = [
    uepy.LoadTextureFromFile(os.path.join(moduleDir, 'kens.jpg')),
    uepy.LoadTextureFromFile(os.path.join(moduleDir, '..', 'pain.jpg')),
]

class MySO(PSketchObject):
    def __init__(self, engineObj):
        # NOTE: (pay attention, cuz it took me half a day to figure this out)
        # we use the polymorphic_type_hook in uepy.h to make pybind11 aware of engine types so that, given a UObject pointer, it can perform
        # automatic downcasting. Unfortunately, we can't use game-specific types in there (in part because that table is declared in uepy and isn't
        # easily movable into our game module). When we create new UClass objs for our py subclasses, the constructor passes the engine obj to this
        # __init__ function, but since the constructor is generic code, all it has at that point is a UObject pointer, so engineObj gets passed to us
        # as such, but we need pybind to instead downcast it to e.g. ACActor in this case, but there's no way for the constructor code to know how to
        # do that because it's all template-based. So instead we receive an engineObj here and then require the game module to expose a casting API
        # so that we can get pybind11 to send us a properly downcasted variable, which we store for future calls.
        try:
            log('MySO.__init__', engineObj, '(pre-casty)')
            super().__init__(uepy.AsACActor(engineObj))
            r = 1000
            self.pos = [r*random.random(), r*random.random(), r*random.random()]
            self.angle = 0
            self.angleTarget = random.random() * 2 * math.pi
            self.dx = 0
            self.dy = 0
        except:
            logTB()

    def BeginPlay(self):
        log('BeginPlay')
        try:
            self.mesh.SetStaticMesh(rock)
            self.billy = self.mesh
            self.mat = uepy.CreateDynamicMaterialInstance(self.engineObj, masterMat)
            log('Created dynamic mat?', not not self.mat)
            if self.mat:
                self.mesh.SetMaterial(0, self.mat)
        except:
            logTB()

    def Tick(self, dt):
        try:
            if random.random() > 0.99:
                #log('Switching!')
                self.mesh.SetStaticMesh(random.choice(meshes))
                self.mat.SetTextureParameterValue('texture', random.choice(textures))

            if self.billy and random.random() > 0.99:
                #log('CLEARING REF TO MESH', self.billy)
                self.billy = None

            #log('TICK!!!', dt)
            if self.angleTarget is None and random.random() > 0.2:
                self.angleTarget = random.random() * 2 * math.pi

            if self.angleTarget is not None:
                diff = abs(self.angle-self.angleTarget)
                if diff < 0.001:
                    # We're there, ish
                    self.angle = self.angleTarget
                    self.angleTarget = None
                else:
                    self.angle += (self.angleTarget-self.angle)/500
                self.dx = math.cos(self.angle)
                self.dy = math.sin(self.angle)
                r = uepy.FRotator(0,0,0)
                r.yaw = self.angle * 360 / math.pi / 2
                self.SetActorRotation(r)

            x, y, z = self.pos
            x += self.dx
            y += self.dy
            self.pos = [x,y,z]
            v = uepy.FVector(x, y, z)
            self.SetActorLocation(v)
        except:
            logTB()

    def Other(self, what):
        return '[[[' + str(what) + ']]]'

uepy.RegisterPythonSubclass('MySO', '/Script/dev_uepy.CActor', MySO)

class AnotherSO(PSketchObject):
    def __init__(self, engineObj):
        try:
            super().__init__(uepy.AsACActor(engineObj))
        except:
            logTB()

    def BeginPlay(self):
        self.yaw = 0

    def Tick(self, dt):
        r = uepy.FRotator(0,0,0)
        self.yaw += dt * 10
        r.yaw = self.yaw
        self.SetActorRotation(r)

uepy.RegisterPythonSubclass('AnotherSO', '/Script/dev_uepy.CActor', AnotherSO)

