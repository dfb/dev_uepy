# Creates a tab/window in the editor for spawning Python-based actors
import uepy, time
from uepy import umg, editor
from uepy import log, logTB

class SpawnerTab(uepy.UUserWidget_PGLUE):
    def __init__(self):
        log('SpawnerTab.__init__', self.engineObj)
        self.num = int(time.time())

    def Construct(self, vboxRoot):
        log('editor_spawner.SpawnerTab.Construct:', vboxRoot)
        vboxRoot = umg.UVerticalBox.Cast(vboxRoot)

        margin = uepy.FMargin(5,5,5,5)

        # Row: combo box of class names + refresh button
        hb = umg.UHorizontalBox.Cast(umg.CreateWidget(vboxRoot, umg.UHorizontalBox, 'hb'))
        slot = umg.UVerticalBoxSlot.Cast(vboxRoot.AddChild(hb))
        slot.SetPadding(margin)

        self.comboBox = umg.UComboBoxString.Cast(umg.CreateWidget(hb, umg.UComboBoxString, 'comboBox'))
        umg.UHorizontalBoxSlot.Cast(hb.AddChild(self.comboBox)).SetPadding(margin)
        for i in range(10):
            self.comboBox.AddOption('item %d' % i)
        self.hackCombo = self.comboBox.BindOnSelectionChanged(self.OnSelectionChanged)

        refreshButton = umg.UButton.Cast(umg.CreateWidget(hb, umg.UButton, 'refreshButton'))
        umg.UHorizontalBoxSlot.Cast(hb.AddChild(refreshButton)).SetPadding(margin)
        label = umg.UTextBlock.Cast(umg.CreateWidget(refreshButton, umg.UTextBlock, 'textblock'))
        label.SetText('Refresh')
        refreshButton.SetContent(label)
        self.hackRefresh = refreshButton.BindOnClicked(self.OnClick) # TODO: we save a ref to keep the delegate alive, bah!

        # Row: checkbox (delete old instances) + text
        hb = umg.UHorizontalBox.Cast(umg.CreateWidget(vboxRoot, umg.UHorizontalBox, 'hb2'))
        slot = umg.UVerticalBoxSlot.Cast(vboxRoot.AddChild(hb))
        slot.SetPadding(margin)

        self.locationCheckbox = umg.UCheckBox.Cast(umg.CreateWidget(hb, umg.UCheckBox, 'checkbox'))
        umg.UHorizontalBoxSlot.Cast(hb.AddChild(self.locationCheckbox)).SetPadding(margin)
        self.locationCheckbox.SetIsChecked(True)
        self.hackCheck = self.locationCheckbox.BindOnCheckStateChanged(self.OnCheckStateChanged)

        label = umg.UTextBlock.Cast(umg.CreateWidget(hb, umg.UTextBlock, 'label'))
        slot = umg.UHorizontalBoxSlot.Cast(hb.AddChild(label))
        slot.SetVerticalAlignment(uepy.enums.EVerticalAlignment.Center)
        slot.SetPadding(margin)
        label.SetText('Delete old instances before spawning')

    def OnClick(self, *args, **kwargs):
        log('ON CLIKC', self, args, kwargs)
        import myactors as m
        world = editor.GetWorld()
        log('WORLD:', world)
        uepy.SpawnActor(world, m.HackyWorldHookActor)
        log('SPAWNED!')

    def OnSelectionChanged(self, *args, **kwargs):
        log('ON SELCH', self, args, kwargs)

    def OnCheckStateChanged(self, *args, **kwargs):
        log('ON CHECK', self, args, kwargs)

editor.RegisterNomadTabSpawner(SpawnerTab, 'uepy Spawner')

'''
UEditableTextBox
SEditableTextBox w/ hint_text
'''

