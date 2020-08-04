#include "MyGameState.h"
#include "common.h"

AMyGameState::AMyGameState() : AGameState()
{
    if (Py_IsInitialized()) // this is called really early to create the CDO, and in that situation it's before engine_startup, and we don't want to create a pyinst anyway
    {
        auto m = py::module::import("MyGameState");
        m.reload(); // TODO: make this conditional
        pyInst = m.attr("MyGameState")((AGameState*)this); // without this cast, at runtime we get an error
    }
}

void AMyGameState::HandleBeginPlay()
{
    try {
        Super::HandleBeginPlay();
        if (pyInst.ptr())
            pyInst.attr("HandleBeginPlay")();
    } catch (std::exception e)
    {
        LERROR("%s", UTF8_TO_TCHAR(e.what()));
    }
}

