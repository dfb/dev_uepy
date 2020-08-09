// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#include "dev_uepy.h"
#include "uepy.h"
#include "common.h"
#include "Modules/ModuleManager.h"
#include "CActor.h"

void FinishPythonInit(py::module& uepy)
{
    LOG("Setting up dev_uepy-specific Python stuff");

    // inject into the uepy module stuff specific to our game module
    py::class_<ACActor, AActor, UnrealTracker<ACActor>>(uepy, "ACActor")
        .def_static("StaticClass", []() { return ACActor::StaticClass(); });
    py::class_<AColorChangingActor, AActor, UnrealTracker<AColorChangingActor>>(uepy, "AColorChangingActor")
        .def_static("StaticClass", []() { return AColorChangingActor::StaticClass(); });
    py::class_<UTestInterface, UInterface, UnrealTracker<UTestInterface>>(uepy, "UTestInterface")
        .def_static("StaticClass", []() { return UTestInterface::StaticClass(); });
        ;

    // each class should define one of these so that a generic UObject pointer can be downcasted (pybind11 can't always figure it out on its own)
    uepy.def("AsACActor", [](UObject *engineObj) -> ACActor* { return Cast<ACActor>(engineObj); }, py::return_value_policy::reference);
    uepy.def("AsAColorChangingActor", [](UObject *engineObj) { return Cast<AColorChangingActor>(engineObj); }, py::return_value_policy::reference);
}

void FdevuepyModule::StartupModule()
{
    FPythonDelegates::LaunchInit.AddStatic(&FinishPythonInit);
}

void FdevuepyModule::ShutdownModule()
{

}

IMPLEMENT_PRIMARY_GAME_MODULE(FdevuepyModule, dev_uepy, "dev_uepy" );

DEFINE_LOG_CATEGORY(DEVUEPY);

