// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.


#include "CActor.h"
#include "common.h"
#include "Kismet/GameplayStatics.h"

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

