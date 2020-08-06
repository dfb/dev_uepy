// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#pragma once

#include "uepy.h"
#include "CActor.generated.h"

UCLASS()
class DEV_UEPY_API ACActor : public AActor, public IPyBridgeMixin
{
	GENERATED_BODY()

public:	
	ACActor();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;
};

