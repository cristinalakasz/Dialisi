#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    P_STOP            = 0,
    P_PRINCIPAL       = 1,
    P_CLEAN           = 2,
    P_NOW_CALIBRATION = 3,
    P_NOW_ABSORBANCE  = 4
} ProgramState;

typedef enum {
    // Program (GUI -> STM32)
    M_PROGRAM          = 0x01,
    
    // Control (GUI -> STM32)
    M_RATIO_DD         = 0x10,
    M_FLUID_VELOCITY   = 0x11,
    M_PUMP_1           = 0x12,
    M_PUMP_2           = 0x13,
    
    // LED (GUI -> STM32)
    M_LED_UV           = 0x14,
    M_LED_BLU          = 0x15,
    M_LED_RED          = 0x16,
    
    // Absorbance (STM32 -> GUI)
    M_ABS_UV           = 0x20,
    M_ABS_BLU          = 0x21,
    M_ABS_RED          = 0x22,
    
    // Rate sampling (GUI -> STM32)
    M_RATE             = 0x30,
    
    // Service messages (viceversa)
    M_ACK              = 0xFA,
    M_NACK             = 0xFB
} MessageID;

#endif