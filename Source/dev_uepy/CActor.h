// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#pragma once

#include "uepy.h"
#include "CActor.generated.h"

USTRUCT(BlueprintType)
struct FMyStruct
{
    GENERATED_BODY();
    UPROPERTY(BlueprintReadWrite, EditAnywhere) FVector moveAmount;
    UPROPERTY(BlueprintReadWrite, EditAnywhere) bool rotating;
};

UCLASS()
class DEV_UEPY_API ABobActor : public AActor
{
	GENERATED_BODY()

public:
	ABobActor() {}
	virtual void SomeAPI();

    UPROPERTY(BlueprintReadWrite) int bpProp = 100;
    int cProp = 5000;
};

UCLASS()
class DEV_UEPY_API ABobActor_CGLUE : public ABobActor, public IUEPYGlueMixin
{
	GENERATED_BODY()

	ABobActor_CGLUE();
protected:
	virtual void BeginPlay() override;
    virtual void Tick(float dt) override;
    virtual void SomeAPI() override;
};
