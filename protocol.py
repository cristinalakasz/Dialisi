from enum import IntEnum

class ProgramState(IntEnum):
    P_STOP = 0
    P_PRINCIPAL = 1
    P_CLEAN = 2
    P_NOW_CALIBRATION = 3
    P_NOW_ABSORBANCE = 4

class MessageID(IntEnum):
    # Program (GUI -> STM32)
    M_PROGRAM = 0x01
    
    # Control (GUI -> STM32)
    M_RATIO_DD = 0x10
    M_FLUID_VELOCITY = 0x11
    M_PUMP_1 = 0x12
    M_PUMP_2 = 0x13
    
    # LED (GUI -> STM32)
    M_LED_UV = 0x14
    M_LED_BLU = 0x15
    M_LED_RED = 0x16
    
    # Absorbance (STM32 -> GUI)
    M_ABS_UV = 0x20
    M_ABS_BLU = 0x21
    M_ABS_RED = 0x22
    
    # Rate sampling (GUI -> STM32)
    M_RATE = 0x30
    
    # Service messages (viceversa)
    M_ACK = 0xFA
    M_NACK = 0xFB

PAYLOAD_FORMATS = {
    MessageID.M_PROGRAM: '<i',        # int 32-bit (4 byte)
    
    MessageID.M_RATIO_DD: '<f',       # float 32-bit (4 byte)
    MessageID.M_FLUID_VELOCITY: '<f', # float 32-bit (4 byte)
    MessageID.M_PUMP_1: '<?',         # bool (1 byte)
    MessageID.M_PUMP_2: '<?',         # bool (1 byte)
    
    MessageID.M_LED_UV: '<?',         # bool (1 byte)
    MessageID.M_LED_BLU: '<?',        # bool (1 byte)
    MessageID.M_LED_RED: '<?',        # bool (1 byte)
    
    MessageID.M_ABS_UV: '<f',         # float 32-bit (4 byte)
    MessageID.M_ABS_BLU: '<f',        # float 32-bit (4 byte)
    MessageID.M_ABS_RED: '<f',        # float 32-bit (4 byte)
    
    MessageID.M_RATE: '<f',           # float 32-bit (4 byte)
    
    MessageID.M_ACK: '',              # None (0 byte)
    MessageID.M_NACK: ''              # None (0 byte)
}