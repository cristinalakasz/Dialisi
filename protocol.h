#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

// --- HEADER DEL PACCHETTO ---
#define PACKET_HEADER 0xAA

// --- STATI DEL PROGRAMMA ---
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

static inline uint8_t getExpectedPayloadLength(MessageID id) {
    switch(id) {
        // Formato: <i (int32_t) -> 4 byte
        case M_PROGRAM:          return 4; 
        
        // Formato: <f (float 32-bit) -> 4 byte
        case M_RATIO_DD:         return 4; 
        case M_FLUID_VELOCITY:   return 4; 
        
        // Formato: <? (bool) -> 1 byte
        case M_PUMP_1:           return 1; 
        case M_PUMP_2:           return 1; 
        
        // Formato: <? (bool) -> 1 byte
        case M_LED_UV:           return 1; 
        case M_LED_BLU:          return 1; 
        case M_LED_RED:          return 1; 
        
        // Formato: <f (float 32-bit) -> 4 byte
        case M_ABS_UV:           return 4; 
        case M_ABS_BLU:          return 4; 
        case M_ABS_RED:          return 4; 
        
        // Formato: <f (float 32-bit) -> 4 byte
        case M_RATE:             return 4; 
        
        // Nessun payload -> 0 byte
        case M_ACK:              return 0; 
        case M_NACK:             return 0; 
        
        // Messaggio sconosciuto
        default:                 return 0; 
    }
}

#endif