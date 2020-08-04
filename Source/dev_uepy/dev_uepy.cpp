// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#include "dev_uepy.h"
#include "uepy.h"
#include "common.h"
#include "Modules/ModuleManager.h"

UPyObjectTracker *TRACKER = nullptr;

void FdevuepyModule::StartupModule()
{
	TRACKER = NewObject<UPyObjectTracker>();
}

void FdevuepyModule::ShutdownModule()
{

}

IMPLEMENT_PRIMARY_GAME_MODULE(FdevuepyModule, dev_uepy, "dev_uepy" );

DEFINE_LOG_CATEGORY(DEVUEPY);

