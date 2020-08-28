// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.


#include "CActor.h"
#include "common.h"
#include "Kismet/GameplayStatics.h"

void ABobActor::SomeAPI()
{
    LOG("Doing the API!");
}

ABobActor_CGLUE::ABobActor_CGLUE() { PrimaryActorTick.bCanEverTick = true; PrimaryActorTick.bStartWithTickEnabled = false; }
void ABobActor_CGLUE::BeginPlay() { Super::BeginPlay(); try { pyInst.attr("BeginPlay")(); } catchpy; }
void ABobActor_CGLUE::Tick(float dt) { try { pyInst.attr("Tick")(dt); } catchpy; }
void ABobActor_CGLUE::SomeAPI() { try { pyInst.attr("SomeAPI")(); } catchpy; }


