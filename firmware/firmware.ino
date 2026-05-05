#include <Servo.h>

// --- DEFINIZIONE PIN ---
#define SERVO_PIN 6
#define LED_PIN 8
#define PHOTO_PIN A0

Servo myServo;

// --- COSTANTI PROTOCOLLO ---
const uint8_t HEADER = 0xAA;

// ID Messaggi
const uint8_t M_PROGRAM    = 0x01;
const uint8_t M_RATIO_DD   = 0x10;
const uint8_t M_LED_UV     = 0x14;
const uint8_t M_ABS_UV     = 0x20;
const uint8_t M_RATE       = 0x30; // <-- NUOVO: ID per il Sampling Rate
const uint8_t M_ACK        = 0xFA;
const uint8_t M_NACK       = 0xFB;

// Stati del Programma
const int32_t P_PRINCIPAL  = 1;

// --- VARIABILI DI STATO ---
bool isRunning = false;
unsigned long lastSendTime = 0;
unsigned long sendInterval = 1000; // <-- NUOVO: Ora è una variabile dinamica (default 1s)

// --- FUNZIONE CRC-8 ---
// Corrisponde esattamente a crcmod.mkCrcFun(0x107, initCrc=0x00, rev=False)
uint8_t calculateCRC8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// --- INVIO PACCHETTI SERIALI ---
void sendPacket(uint8_t id, const uint8_t* payload, uint8_t len) {
    uint8_t crcData[34]; // Buffer per calcolare il CRC (ID + Len + Payload)
    crcData[0] = id;
    crcData[1] = len;
    
    if (len > 0 && payload != nullptr) {
        memcpy(&crcData[2], payload, len);
    }
    
    uint8_t crc = calculateCRC8(crcData, 2 + len);
    
    Serial.write(HEADER);
    Serial.write(id);
    Serial.write(len);
    if (len > 0 && payload != nullptr) {
        Serial.write(payload, len);
    }
    Serial.write(crc);
}

void sendAck() {
    sendPacket(M_ACK, nullptr, 0);
}

void sendNack() {
    sendPacket(M_NACK, nullptr, 0);
}

void setup() {
    Serial.begin(115200);
    
    myServo.attach(SERVO_PIN);
    pinMode(LED_PIN, OUTPUT);
    pinMode(PHOTO_PIN, INPUT);
    
    // Stato iniziale (spento)
    digitalWrite(LED_PIN, LOW);
    myServo.write(0);
}

void loop() {
    // ==========================================
    // 1. RICEZIONE E PARSING DEI COMANDI DA GUI
    // ==========================================
    if (Serial.available() > 0) {
        if (Serial.read() == HEADER) {
            uint32_t startTime = millis();
            
            // Aspetta di ricevere ID e Lunghezza (con timeout di 20ms)
            while(Serial.available() < 2) {
                if (millis() - startTime > 20) return; 
            }
            
            uint8_t id = Serial.read();
            uint8_t len = Serial.read();
            
            // Aspetta il Payload e il CRC byte
            startTime = millis();
            while(Serial.available() < len + 1) {
                 if (millis() - startTime > 20) return;
            }
            
            uint8_t payload[16];
            if (len > 0) {
                Serial.readBytes(payload, len);
            }
            uint8_t receivedCrc = Serial.read();
            
            // Verifica integrità CRC
            uint8_t crcData[34];
            crcData[0] = id;
            crcData[1] = len;
            if (len > 0) {
                memcpy(&crcData[2], payload, len);
            }
            uint8_t computedCrc = calculateCRC8(crcData, 2 + len);
            
            if (computedCrc == receivedCrc) {
                sendAck(); // Segnala alla GUI che il pacchetto è OK
                
                // --- GESTIONE DEI COMANDI ---
                
                if (id == M_PROGRAM && len == 4) {
                    int32_t state;
                    memcpy(&state, payload, 4); // Converte i 4 byte in Int32
                    
                    if (state == P_PRINCIPAL) {
                        isRunning = true;
                    } else {
                        isRunning = false;
                        digitalWrite(LED_PIN, LOW); // Spegne in sicurezza
                    }
                } 
                else if (id == M_RATIO_DD && len == 4 && isRunning) {
                    float ratio;
                    memcpy(&ratio, payload, 4); // Converte i 4 byte in Float
                    
                    // La tua GUI invia un valore da 1 a 100. Lo mappiamo ai gradi del Servo (0-180).
                    int angle = map((long)ratio, 1, 100, 0, 180);
                    angle = constrain(angle, 0, 180);
                    myServo.write(angle);
                }
                else if (id == M_LED_UV && len == 1 && isRunning) {
                    bool ledState = payload[0]; // 1 byte Bool
                    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
                }
                // --- NUOVO: GESTIONE SAMPLING RATE ---
                else if (id == M_RATE && len == 4) {
                    float rateSlider;
                    memcpy(&rateSlider, payload, 4); // Float 32 bit
                    
                    // Slider: 0 = 10 sec (10000ms), 100 = 1 sec (1000ms)
                    long interval = map((long)rateSlider, 0, 100, 10000, 1000);
                    sendInterval = constrain(interval, 1000, 10000);
                }
                
            } else {
                sendNack(); // Errore di comunicazione, richiede reinvio
            }
        }
    }

    // ==========================================
    // 2. LETTURA SENSORI (SOLO QUANDO ATTIVO)
    // ==========================================
    if (isRunning) {
        if (millis() - lastSendTime >= sendInterval) { // Usa il nuovo intervallo dinamico
            lastSendTime = millis();
            
            // Legge il fotoresistore (con il tuo circuito: Buio = ~1023, Luce = verso lo 0)
            int rawPhoto = analogRead(PHOTO_PIN);
            
            // Inverte e scala il valore
            int mappedPhoto = map(rawPhoto, 1023, 0, 0, 100);
            
            // Limita il valore
            mappedPhoto = constrain(mappedPhoto, 0, 100);
            
            // Converte in float ('<f')
            float photoVal = (float)mappedPhoto; 
            
            // Invia il valore alla GUI
            sendPacket(M_ABS_UV, (uint8_t*)&photoVal, sizeof(float));
        }
    }
}