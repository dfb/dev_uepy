import uepy
from uepy import log, logTB, FVector, FRotator
import random, math, os, time

moduleDir = os.path.abspath(os.path.dirname(__file__))

rock = uepy.LoadMesh('/Game/StarterContent/Props/SM_Rock.SM_Rock')
couch = uepy.LoadMesh('/Game/StarterContent/Props/SM_Couch.SM_Couch')
meshes = [rock, couch]
masterMat = uepy.LoadMaterial('/Game/MasterMat.MasterMat')
textures = [
    uepy.LoadTextureFromFile(os.path.join(moduleDir, 'kens.jpg')),
    uepy.LoadTextureFromFile(os.path.join(moduleDir, '..', 'pain.jpg')),
]

class MySO(uepy.AActor_PGLUE):
    def __init__(self):
        # NOTE: (pay attention, cuz it took me half a day to figure this out)
        # we use the polymorphic_type_hook in uepy.h to make pybind11 aware of engine types so that, given a UObject pointer, it can perform
        # automatic downcasting. Unfortunately, we can't use game-specific types in there (in part because that table is declared in uepy and isn't
        # easily movable into our game module). When we create new UClass objs for our py subclasses, the constructor passes the engine obj to this
        # __init__ function, but since the constructor is generic code, all it has at that point is a UObject pointer, so engineObj gets passed to us
        # as such, but we need pybind to instead downcast it to e.g. ACActor in this case, but there's no way for the constructor code to know how to
        # do that because it's all template-based. So instead we receive an engineObj here and then require the game module to expose a casting API
        # so that we can get pybind11 to send us a properly downcasted variable, which we store for future calls.
        try:
            self.SetActorTickEnabled(True)
            r = 1000
            self.pos = [r*random.random()-r/2, r*random.random()-r/2, 0*random.random()]
            self.angle = 0
            self.speed = random.random() * 20
            self.angleTarget = random.random() * 2 * math.pi - math.pi
            self.dx = 0
            self.dy = 0
            self.SetRootComponent(self.CreateUStaticMeshComponent('mesh'))
            self.mesh = uepy.UStaticMeshComponent.Cast(self.GetRootComponent())
            self.mesh.SetStaticMesh(couch)
        except:
            logTB()

    def BeginPlay(self):
        self.SuperBeginPlay()
        try:
            self.mat = uepy.CreateDynamicMaterialInstance(self.engineObj, masterMat)
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

class SubSO(MySO):
    def __init__(self):
        super().__init__()
        self.speed *= 10

class AnotherSO(uepy.AActor_PGLUE):
    def __init__(self):
        try:
            self.SetActorTickEnabled(True)
            self.SetRootComponent(self.CreateUStaticMeshComponent('mesh'))
            self.mesh = uepy.UStaticMeshComponent.Cast(self.GetRootComponent())
            self.mesh.SetStaticMesh(couch)
        except:
            logTB()

    def BeginPlay(self):
        self.SuperBeginPlay()
        self.yaw = 0

    def Tick(self, dt):
        r = FRotator(0,0,0)
        self.yaw += dt * 10
        r.yaw = self.yaw
        self.SetActorRotation(r)

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

class Sentry(uepy.AActor_PGLUE):
    def __init__(self):
        try:
            self.SetActorTickEnabled(True)
            self.SetRootComponent(self.CreateUStaticMeshComponent('body'))
            self.body = uepy.UStaticMeshComponent.Cast(self.GetRootComponent())
            self.body.SetStaticMesh(BODY_MESH)
            self.body.SetRelativeScale3D(FVector(0.25, 0.25, 0.25))
            self.arm = uepy.UStaticMeshComponent.Cast(self.CreateUStaticMeshComponent('arm'))
            self.arm.SetStaticMesh(ARM_MESH)
            self.arm.AttachToComponent(self.body)
            self.arm.SetRelativeLocation(FVector(0,0,250))
        except:
            logTB()

    def BeginPlay(self):
        self.SuperBeginPlay()
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

DOOR_MESH = uepy.LoadMesh('/Game/StarterContent/Props/SM_DoorFrame.SM_DoorFrame')
class ColorChanger(uepy.AActor_PGLUE):
    def __init__(self):
        try:
            self.SetActorTickEnabled(True)
            self.SetRootComponent(self.CreateUStaticMeshComponent('body'))
            self.body = uepy.UStaticMeshComponent.Cast(self.GetRootComponent())
            self.body.SetStaticMesh(DOOR_MESH)
        except:
            logTB()

    def DoSomething(self, i):
        try:
            log('Do something!', self, i)
            self.SetActorRotation(FRotator(RR(0,360), RR(0,360), RR(0,360)))
        except:
            logTB()

class HackyWorldHookActor(uepy.AActor_PGLUE):
    '''Temporary hack until we have implemented GameInstance/State in Python: place one of these actors into the level
    (or spawn it on BeginPlay) so that from Python we can hook into a few different game events.'''
    def __init__(self):
        self.SetActorTickEnabled(True)
        import sourcewatcher as S
        reload(S)
        S.log = log
        S.logTB = logTB
        self.watcher = S.SourceWatcher('scratchpad')

    def BeginPlay(self):
        self.SuperBeginPlay()
        log('HackyWorldHookActor.BeginPlay')

    def Tick(self, dt):
        self.watcher.Check()

def Boom():
    for a in uepy.GetAllActorsOfClass(uepy.GetWorld(), MySO):
        p = uepy.PyInst(a)
        p.angle = p.angleTarget = 0

class ABobActor_PGLUE(uepy.AActor_PGLUE):
    def SomeAPI(self): self.engineObj.SomeAPI()

bases = [b for b in ABobActor_PGLUE.__bases__ if b != object]
log('BOB PGLUE:', type(ABobActor_PGLUE) is uepy.PyGlueMetaclass, bases)

class MyBob(ABobActor_PGLUE, metaclass=uepy.PyGlueMetaclass):
    def __init__(self):
        try:
            log('MyBob.__init__', self.engineObj)
            self.count = 0
            self.SetActorTickEnabled(True)
        except:
            logTB()

    def Tick(self, dt):
        self.count += 1
        if not self.count % 100:
            log('TICKING', self.count)

    def SomeAPI(self):
        log('MyBob.SomeAPI ya\'ll!!!')

def B2():
    for a in uepy.GetAllActorsOfClass(uepy.GetWorld(), MyBob):
        log('A:', a) #, a.engineObj)
        a.SomeAPI()
B2()
