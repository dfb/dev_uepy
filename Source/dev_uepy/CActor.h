// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#pragma once

#include "uepy.h"
#include "CActor.generated.h"

UCLASS()
class DEV_UEPY_API ACActor : public AActor, public IPyBridgeMixin
{
	GENERATED_BODY()

protected:
	virtual void BeginPlay() override;

public:	
	ACActor();
	virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable)
    void OnSomeUserEvent();
};

UINTERFACE(BlueprintType)
class UTestInterface : public UInterface
{
	GENERATED_BODY()
};

class ITestInterface
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable)
    void DoSomething(int i);
};

UCLASS()
class DEV_UEPY_API AColorChangingActor : public AActor, public IPyBridgeMixin, public ITestInterface
{
    GENERATED_BODY()

protected:
	virtual void BeginPlay() override;

public:	
    AColorChangingActor();
	virtual void Tick(float DeltaTime) override;
    virtual void DoSomething_Implementation(int i) override;
};
