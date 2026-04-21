#include "CRC8.h"

CRC8 crc(0x07, 0x00, 0x00, false, false); 

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop()
{
  if (Serial.available() > 0)
  {
    if (Serial.read() == 0xAA)
    {
      unsigned long t;

      t = millis();
      while (Serial.available() < 1) { if (millis() - t > 100) return; }
      byte id = Serial.read();

      t = millis();
      while (Serial.available() < 1) { if (millis() - t > 100) return; }
      byte len = Serial.read();
      
      t = millis();
      while (Serial.available() < len) { if (millis() - t > 100) return; }
      byte payload[len];
      for (int i = 0; i < len; i++)
      {
        payload[i] = Serial.read();
      }

      t = millis();
      while (Serial.available() < 1) { if (millis() - t > 100) return; }
      byte receivedCrc = Serial.read();
      crc.restart();
      crc.add(id);
      crc.add(len);
      for (int i = 0; i < len; i++)
        crc.add(payload[i]);

      if (crc.getCRC() == receivedCrc)
      {
        Serial.write(0xAA);
        Serial.write(0xFA);
        Serial.write(0x0);
        crc.restart();
        crc.add(0xFA);
        crc.add(0x0);
        Serial.write(crc.getCRC());
        if (id == 0x01 && payload[0] == 1)
        {
          digitalWrite(LED_BUILTIN, HIGH);
        }
        if (id == 0x01 && payload[0] == 0)
        {
          digitalWrite(LED_BUILTIN, LOW);
        }
      }
      else
      {
        Serial.write(0xAA);
        Serial.write(0xFB);
        Serial.write(0x0);
        crc.restart();
        crc.add(0xFB);
        crc.add(0x0);
        Serial.write(crc.getCRC());
      }
    }
  }
}