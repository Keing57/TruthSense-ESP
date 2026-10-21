#include <Arduino.h>

#define SENSOR_PIN 4

void setup() {
  Serial.begin(115200);
}

void loop() {
  int sensorValue = analogRead(SENSOR_PIN);
  Serial.println(sensorValue);
  delay(50);
}
