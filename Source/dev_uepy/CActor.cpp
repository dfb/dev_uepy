// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.


#include "CActor.h"
#include "common.h"
#include "Kismet/GameplayStatics.h"

// Sets default values
ACActor::ACActor()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;
	//RootComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("theMesh"));

    //auto asset = ConstructorHelpers::FObjectFinder<UStaticMesh>(TEXT("StaticMesh'/Game/StarterContent/Props/SM_Rock.SM_Rock'"));
    //auto asset = ConstructorHelpers::FObjectFinder<UStaticMesh>(TEXT("StaticMesh'/Game/StarterContent/Props/SM_Couch.SM_Couch'"));
    //mesh->SetStaticMesh(asset.Object);
}

// Called when the game starts or when spawned
void ACActor::BeginPlay()
{
    try {
        Super::BeginPlay();
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
        pyInst.attr("Tick")(DeltaTime);
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}

