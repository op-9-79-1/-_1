from eudplib import *


def onPluginStart():
    DoActions([  # Basic DatFile Actions
        SetMemory(0x663224, Add, 201326592),# units:Elevation Level  index:215    from 4 To 16
        SetMemory(0x6643DC, Add, 4),# units:Special Ability Flags  index:215    from 536872960 To 536872964
        SetMemory(0x66330C, Add, -83886080),# units:Sight Range  index:215    from 5 To 0
        SetMemory(0x66015C, Add, -983040),# units:What Sound Start  index:215    from 15 To 0
        SetMemory(0x662D9C, Add, -983040),# units:What Sound End  index:215    from 15 To 0
        SetMemory(0x662BBC, Add, -16),# units:StarEdit Placement Box Width  index:215    from 32 To 16
        SetMemory(0x662BBC, Add, -1048576),# units:StarEdit Placement Box Height  index:215    from 32 To 16
        SetMemory(0x661E80, Add, -8),# units:Unit Size Left  index:215    from 16 To 8
        SetMemory(0x661E80, Add, -524288),# units:Unit Size Up  index:215    from 16 To 8
        SetMemory(0x661E84, Add, -7),# units:Unit Size Right  index:215    from 15 To 8
        SetMemory(0x661E84, Add, -458752),# units:Unit Size Down  index:215    from 15 To 8
        SetMemory(0x663874, Add, 134217728),# units:Staredit Group Flags  index:215    from 128 To 136
    ])

