// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class dev_uepyEditorTarget : TargetRules
{
	public dev_uepyEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;

		ExtraModuleNames.AddRange( new string[] { "dev_uepy" } );
	}
}
