import uepy
from uepy import log, logTB, FVector, FRotator
import random, math, os, time

moduleDir = os.path.abspath(os.path.dirname(__file__))

class PyActor:
    # TODO: either auto-gen all this or, better yet, couldn't we inject the methods and properties directly from c++?
    def __init__(self, engineObj):
        self.engineObj = engineObj
        log('PyActor.__init__', engineObj)

    def GetWorld(self): return self.engineObj.GetWorld()
    def SetActorLocation(self, v): self.engineObj.SetActorLocation(v) # this works because engineObj is a pointer to a real instance, and we will also write wrapper code to expose these APIs anyway
    def GetActorLocation(self): return self.engineObj.GetActorLocation()
    def GetActorRotation(self): return self.engineObj.GetActorRotation()
    def SetActorRotation(self, r): self.engineObj.SetActorRotation(r)
    def BeginPlay(self): pass
    def Tick(self, dt): pass
    def CreateUStaticMeshComponent(self, name): return self.engineObj.CreateUStaticMeshComponent(name)
    def GetRootComponent(self): return self.engineObj.GetRootComponent()
    def SetRootComponent(self, s): self.engineObj.SetRootComponent(s)

    def OnSomeUserEvent(self): log('OnSomeUserEvent', self)

rock = uepy.LoadMesh('/Game/StarterContent/Props/SM_Rock.SM_Rock')
couch = uepy.LoadMesh('/Game/StarterContent/Props/SM_Couch.SM_Couch')
meshes = [rock, couch]
masterMat = uepy.LoadMaterial('/Game/MasterMat.MasterMat')
textures = [
    uepy.LoadTextureFromFile(os.path.join(moduleDir, 'kens.jpg')),
    uepy.LoadTextureFromFile(os.path.join(moduleDir, '..', 'pain.jpg')),
]

class MySO(PyActor):
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
            self.pos = [r*random.random()-r/2, r*random.random()-r/2, 0*random.random()]
            self.angle = 0
            self.speed = random.random() * 20
            self.angleTarget = random.random() * 2 * math.pi - math.pi
            self.dx = 0
            self.dy = 0
            self.SetRootComponent(self.CreateUStaticMeshComponent('mesh'))
            self.mesh = uepy.AsUStaticMeshComponent(self.GetRootComponent())
            self.mesh.SetStaticMesh(couch)
        except:
            logTB()

    def BeginPlay(self):
        log('BeginPlay')
        try:
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

            #log('TICK!!!', dt)
            if self.angleTarget is None and random.random() > 0.2:
                self.angleTarget = random.random() * 2 * math.pi - math.pi

            if self.angleTarget is not None:
                diff = abs(self.angle-self.angleTarget)
                if diff < 0.001:
                    # We're there, ish
                    self.angle = self.angleTarget
                    self.angleTarget = None
                else:
                    self.angle += (self.angleTarget-self.angle)/500*self.speed
                self.dx = self.speed*math.cos(self.angle)
                self.dy = self.speed*math.sin(self.angle)
                r = FRotator(0,0,0)
                r.yaw = self.angle * 360 / math.pi / 2
                self.SetActorRotation(r)

            x, y, z = self.pos
            x += self.dx
            y += self.dy
            self.pos = [x,y,z]
            v = FVector(x, y, z)
            self.SetActorLocation(v)
        except:
            logTB()

    def Other(self, what):
        return '[[[' + str(what) + ']]]'

MySO.engineClass = uepy.RegisterPythonSubclass('MySO', '/Script/dev_uepy.CActor', MySO)
# TODO: the above is a temp hack so we keep a ref to the UClass so we can spawn it from python

class AnotherSO(PyActor):
    def __init__(self, engineObj):
        try:
            super().__init__(uepy.AsACActor(engineObj))
            self.SetRootComponent(self.CreateUStaticMeshComponent('mesh'))
            self.mesh = uepy.AsUStaticMeshComponent(self.GetRootComponent())
            self.mesh.SetStaticMesh(couch)
        except:
            logTB()

    def BeginPlay(self):
        self.yaw = 0

    def Tick(self, dt):
        r = FRotator(0,0,0)
        self.yaw += dt * 10
        r.yaw = self.yaw
        self.SetActorRotation(r)

uepy.RegisterPythonSubclass('AnotherSO', '/Script/dev_uepy.CActor', AnotherSO)

BODY_MESH = uepy.LoadMesh('/Game/StarterContent/Props/SM_MatPreviewMesh_02.SM_MatPreviewMesh_02')
ARM_MESH = uepy.LoadMesh('/Game/StarterContent/Props/SM_Lamp_Ceiling.SM_Lamp_Ceiling')
RR = random.randrange

class SentryCommand:
    def __init__(self, actor, speed):
        self.actor = actor
        self.speed = speed
        self.t = 0

    def Done(self):
        return self.t >= 1.0

    def Begin(self):
        self.t = 0

    def Update(self, dt):
        self.t = min(1.0, self.t + dt * self.speed)
        return self.t

class WalkCommand(SentryCommand):
    def __init__(self, actor, speed, distance):
        super().__init__(actor, speed)
        self.distance = distance

    def Begin(self):
        super().Begin()
        self.pos = self.actor.GetActorLocation()
        yaw = self.actor.GetActorRotation().yaw
        self.dy = self.distance * math.sin(math.radians(yaw))
        self.dx = self.distance * math.cos(math.radians(yaw))

    def Update(self, dt):
        t = super().Update(dt)
        newLoc = FVector(self.pos.x + t*self.dx, self.pos.y + t*self.dy, self.pos.z)
        self.actor.SetActorLocation(newLoc)

    def __repr__(self):
        return '<Walk %.2f at %.2f, t=%.3f, dx,dy=%.2f,%.2f>' % (self.distance, self.speed, self.t, self.dx, self.dy)

class TurnCommand(SentryCommand):
    def __init__(self, actor, speed, degrees, dir):
        super().__init__(actor, speed)
        self.degrees = degrees
        self.dir = dir # 1 or -1

    def Begin(self):
        super().Begin()
        self.yaw = self.actor.GetActorRotation().yaw

    def Update(self, dt):
        t = super().Update(dt)
        newRot = FRotator(0,0,0)
        newRot.yaw = self.yaw + t*self.degrees*self.dir
        self.actor.SetActorRotation(newRot)

class Sentry(PyActor):
    def __init__(self, engineObj):
        try:
            super().__init__(uepy.AsACActor(engineObj))
            self.SetRootComponent(self.CreateUStaticMeshComponent('body'))
            self.body = uepy.AsUStaticMeshComponent(self.GetRootComponent())
            self.body.SetStaticMesh(BODY_MESH)
            self.body.SetRelativeScale3D(FVector(0.25, 0.25, 0.25))
            self.arm = uepy.AsUStaticMeshComponent(self.CreateUStaticMeshComponent('arm'))
            self.arm.SetStaticMesh(ARM_MESH)
            self.arm.AttachToComponent(self.body)
            self.arm.SetRelativeLocation(FVector(0,0,250))
        except:
            logTB()

    def BeginPlay(self):
        self.commands = [WalkCommand(self, 1, RR(200, 2000)), TurnCommand(self, 1, RR(10, 180), random.choice([1,-1]))]
        self.curCommand = None
        self.Update()

    def Update(self, dt=0):
        if self.curCommand is None:
            if self.commands:
                self.curCommand = self.commands.pop(0)
                self.curCommand.Begin()

        c = self.curCommand
        if c is not None:
            if c.Done():
                self.commands.append(c)
                self.curCommand = None
                # on next tick, switch to next command
            else:
                c.Update(dt)

    def Tick(self, dt):
        self.Update(dt)
        cur = self.arm.GetRelativeRotation()
        cur.roll += 1
        self.arm.SetRelativeRotation(cur)

uepy.RegisterPythonSubclass('Sentry', '/Script/dev_uepy.CActor', Sentry)

DOOR_MESH = uepy.LoadMesh('/Game/StarterContent/Props/SM_DoorFrame.SM_DoorFrame')
class ColorChanger(PyActor):
    def __init__(self, engineObj):
        try:
            super().__init__(uepy.AsAColorChangingActor(engineObj))
            self.SetRootComponent(self.CreateUStaticMeshComponent('body'))
            self.body = uepy.AsUStaticMeshComponent(self.GetRootComponent())
            self.body.SetStaticMesh(DOOR_MESH)
        except:
            logTB()

    def DoSomething(self, i):
        try:
            log('Do something!', self, i)
            self.SetActorRotation(FRotator(RR(0,360), RR(0,360), RR(0,360)))
        except:
            logTB()

uepy.RegisterPythonSubclass('ColorChanger', '/Script/dev_uepy.ColorChangingActor', ColorChanger)

#log('ACActor:', uepy.ACActor, uepy.ACActor.StaticClass().ImplementsInterface(uepy.UTestInterface.StaticClass()))
#log('ColorChanger:', uepy.AColorChangingActor, uepy.AColorChangingActor.StaticClass().ImplementsInterface(uepy.UTestInterface.StaticClass()))

class HackyWorldHookActor:
    '''Temporary hack until we have implemented GameInstance/State in Python: place one of these actors into the level
    (or spawn it on BeginPlay) so that from Python we can hook into a few different game events.'''
    def __init__(self, engineObj):
        self.engineObj = engineObj
        import sourcewatcher as S
        reload(S)
        S.log = log
        S.logTB = logTB
        self.watcher = S.SourceWatcher('scratchpad')

    def BeginPlay(self):
        log('HackyWorldHookActor.BeginPlay')

    def Tick(self, dt):
        self.watcher.Check()

HackyWorldHookActor.engineClass = uepy.RegisterPythonSubclass('HackyWorldHookActor', '/Script/uepy.WorldHookActor', HackyWorldHookActor)

