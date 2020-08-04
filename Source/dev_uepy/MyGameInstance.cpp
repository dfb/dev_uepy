#include "MyGameInstance.h"
#include "common.h"

UMyGameInstance::UMyGameInstance() : UGameInstance()
{
    if (Py_IsInitialized()) // this is called really early to create the CDO, and in that situation it's before engine_startup, and we don't want to create a pyinst anyway
    {
        auto m = py::module::import("MyGameInstance");
        m.reload(); // TODO: make this conditional?
        pyInst = m.attr("MyGameInstance")((UGameInstance*)this); // without this cast, at runtime we get an error because pybind doesn't know how to pass UMyGameInstance
    }
}

void UMyGameInstance::OnStart()
{
    try {
        Super::OnStart();
        if (pyInst.ptr())
            pyInst.attr("OnStart")();
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
    }
}

void UMyGameInstance::Init()
{
    try {
        Super::Init();
        if (pyInst.ptr())
            pyInst.attr("Init")();
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
    }
}

void UMyGameInstance::Shutdown()
{
    try {
        Super::Shutdown();
        if (pyInst.ptr())
            pyInst.attr("Shutdown")();
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
    }
}

void UMyGameInstance::StartGameInstance()
{
    try {
        Super::StartGameInstance(); // TODO: let subclasses decide whether or not to call this
        if (pyInst.ptr())
            pyInst.attr("StartGameInstance")();
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
    }
}

TSubclassOf<AGameModeBase> UMyGameInstance::OverrideGameModeClass(TSubclassOf<AGameModeBase> GameModeClass, const FString& MapName, const FString& Options, const FString& Portal) const
{
    LOG("Skipping game mode override");
    return GameModeClass;
    try {
        if (pyInst.ptr())
        {
            py::object klass = pyInst.attr("OverrideGameModeClass")(GameModeClass, MapName, Options, Portal);
            return py::cast<TSubclassOf<AGameModeBase>>(klass);
        }
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
        LERROR("Using default game mode");
    }
    return GameModeClass;
}

