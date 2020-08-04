// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class FdevuepyModule : public FDefaultModuleImpl
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
};