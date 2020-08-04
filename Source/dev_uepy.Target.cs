// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class dev_uepyTarget : TargetRules
{
	public dev_uepyTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;

		ExtraModuleNames.AddRange( new string[] { "dev_uepy" } );
        bUseLoggingInShipping = true;
	}
}
