// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.


#include "CActor.h"
#include "common.h"
#include "Kismet/GameplayStatics.h"

PYBIND11_EMBEDDED_MODULE(cactor, m) {
    py::class_<ADActor, AActor, UnrealTracker<ADActor>>(m, "ADActor")
        ;

    py::class_<ACActor, AActor, UnrealTracker<ACActor>>(m, "ACActor")
        .def_readwrite("mesh", &ACActor::mesh)
        ;

    m.def("casty", [](UObject *engineObj) -> ACActor*
    {
        return Cast<ACActor>(engineObj);
    }, py::return_value_policy::reference);

	m.def("spawn", [](UWorld *world, py::object pyclass) -> void
	{
		LOG("SPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
        FTransform transform;
        UClass *klass = FindObject<UClass>(ANY_PACKAGE, TEXT("AnotherSO"));
        ACActor * actor = world->SpawnActorDeferred<ACActor>(klass, transform);
        UGameplayStatics::FinishSpawningActor(actor, transform);
	});
}

// Sets default values
ACActor::ACActor() : AActor(), IPyBridgeMixin()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;
	mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("theMesh"));
    RootComponent = mesh;

    //auto asset = ConstructorHelpers::FObjectFinder<UStaticMesh>(TEXT("StaticMesh'/Game/StarterContent/Props/SM_Rock.SM_Rock'"));
    auto asset = ConstructorHelpers::FObjectFinder<UStaticMesh>(TEXT("StaticMesh'/Game/StarterContent/Props/SM_Couch.SM_Couch'"));
    mesh->SetStaticMesh(asset.Object);
}

// Called when the game starts or when spawned
void ACActor::BeginPlay()
{
    try {
        Super::BeginPlay();
        if (pyInst.ptr())
            pyInst.attr("BeginPlay")();
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}

// Called every frame
void ACActor::Tick(float DeltaTime)
{
    try {
        Super::Tick(DeltaTime);
        if (pyInst.ptr())
        {
            pyInst.attr("Tick")(DeltaTime);
            //std::string s = py::cast<std::string>(pyInst.attr("Other")(DeltaTime));
            //FString fs(s.c_str());
            //LOG("TICK: %s", *fs);
        }
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}

void ACActor::CallTehPythonGlobal(UObject *WorldContextObject)
{
    UWorld* world = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
    py::module ue = py::module::import("engine_startup");
    ue.attr("TehPythonGlobal")(world);
}

