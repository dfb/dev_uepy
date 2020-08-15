// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.


#include "CActor.h"
#include "common.h"
#include "Kismet/GameplayStatics.h"

// Sets default values
ACActor::ACActor()
{
	PrimaryActorTick.bCanEverTick = true;
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

void ACActor::OnSomeUserEvent()
{
    try {
        pyInst.attr("OnSomeUserEvent")();
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}

AColorChangingActor::AColorChangingActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

// Called when the game starts or when spawned
void AColorChangingActor::BeginPlay()
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
void AColorChangingActor::Tick(float DeltaTime)
{
    try {
        Super::Tick(DeltaTime);
        pyInst.attr("Tick")(DeltaTime);
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}

/*
void AColorChangingActor::DoSomething_Implementation(int i)
{
    try {
        pyInst.attr("DoSomething")(i);
	} catch (std::exception e)
    {
        LOG("EXCEPTION %s", UTF8_TO_TCHAR(e.what()));
    }
}
*/
