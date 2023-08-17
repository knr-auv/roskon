from enum import Enum

class MessageFromOkon(Enum):
    PID = 0x0
    CL_MATRIX = 0x1
    HEART_BEAT = 0x2
    SERVICE_CONFIRM = 0x3

class MessageToOkon(Enum):
    REQUEST = 0x0
    SERVICE = 0x1
    STICKS = 0x2
    MODE = 0x3
    CL_STATUS = 0x4

class MessageToOkonRequest(Enum):
    PID = 0x0
    CL_MATRIX = 0x1

class MessageToOkonService(Enum):
    ENTER = 0x0
    REBOOT = 0x1
    UPDATE_CL_MATRIX = 0x2
    ENABLE_DIRECT_MOTORS_CTRL = 0x3
    DISABLE_DIRECT_MOTORS_CTRL = 0x4
    DIRECT_THRUSTERS_CTRL = 0x5
    DIRECT_MATRIX_THRUSTERS_CTRL = 0x6
    SAVE_SETTINGS = 0x7
    LOAD_SETTINGS = 0x8
    NEW_PIDS = 0x9
