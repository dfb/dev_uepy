// Copyright 2016-2020 FractalMob, LLC. All Rights Reserved.

#include "dev_uepy.h"
#include "uepy.h"
#include "common.h"
#include "Modules/ModuleManager.h"
#include "CActor.h"

void FinishPythonInit(py::module& uepy)
{
    LOG("Setting up dev_uepy-specific Python stuff");
    py::object glueclasses = uepy.attr("glueclasses");

    py::class_<ABobActor, AActor, UnrealTracker<ABobActor>>(uepy, "ABobActor")
        .def("SomeAPI", [](ABobActor& self) { self.SomeAPI(); })
        .def_static("StaticClass", []() { return ABobActor::StaticClass(); })
        .def_static("Cast", [](UObject *w) { return Cast<ABobActor>(w); }, py::return_value_policy::reference)
        .def_readwrite("bpProp", &ABobActor::bpProp)
        .def_readwrite("cProp", &ABobActor::cProp)
        ;
    py::class_<ABobActor_CGLUE, ABobActor, UnrealTracker<ABobActor_CGLUE>>(glueclasses, "ABobActor_CGLUE")
        .def_static("StaticClass", []() { return ABobActor_CGLUE::StaticClass(); })
        .def_static("Cast", [](UObject *w) { return Cast<ABobActor_CGLUE>(w); }, py::return_value_policy::reference)
        ;

    py::class_<FMyStruct>(uepy, "FMyStruct")
        .def(py::init<>())
        .def_readwrite("moveAmount", &FMyStruct::moveAmount)
        .def_readwrite("rotating", &FMyStruct::rotating)
        ;
}

void FdevuepyModule::StartupModule()
{
    FUEPyDelegates::LaunchInit.AddStatic(&FinishPythonInit);
}

void FdevuepyModule::ShutdownModule()
{

}

IMPLEMENT_PRIMARY_GAME_MODULE(FdevuepyModule, dev_uepy, "dev_uepy" );

DEFINE_LOG_CATEGORY(DEVUEPY);

