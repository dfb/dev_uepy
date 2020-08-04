#pragma once

#include "uepy.h"
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class DEV_UEPY_API UMyGameInstance : public UGameInstance
{
	GENERATED_BODY()
    py::object pyInst;

public:
    UMyGameInstance();
    virtual void OnStart() override;
	virtual void Init();
	virtual void Shutdown();
	virtual void StartGameInstance();
	virtual TSubclassOf<AGameModeBase> OverrideGameModeClass(TSubclassOf<AGameModeBase> GameModeClass, const FString& MapName, const FString& Options, const FString& Portal) const override;
	//virtual FGameInstancePIEResult InitializeForPlayInEditor(int32 PIEInstanceIndex, const FGameInstancePIEParameters& Params);
	//virtual FGameInstancePIEResult StartPlayInEditorGameInstance(ULocalPlayer* LocalPlayer, const FGameInstancePIEParameters& Params);
	//virtual FGameInstancePIEResult PostCreateGameModeForPIE(const FGameInstancePIEParameters& Params, AGameModeBase* GameMode);
	//virtual void OnWorldChanged(UWorld* OldWorld, UWorld* NewWorld) {}
	//virtual class AGameModeBase* CreateGameModeForURL(FURL InURL, UWorld* InWorld);

};
