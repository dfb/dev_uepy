// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#pragma once

#include "uepy.h"
#include "GameFramework/GameState.h"
#include "MyGameState.generated.h"

/**
 * 
 */
UCLASS()
class DEV_UEPY_API AMyGameState : public AGameState
{
	GENERATED_BODY()
    py::object pyInst;
	
public:
    AMyGameState();
    virtual void HandleBeginPlay() override;
};
