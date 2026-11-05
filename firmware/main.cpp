#include <Arduino.h>

#define SENSOR_PIN 4
const int WINDOW_SIZE = 20;

int readings[WINDOW_SIZE] = {0};
int readIndex = 0;
long total = 0;
int average = 0;

void setup() {
  Serial.begin(115200);
  int initialValue = analogRead(SENSOR_PIN);
  for (int i = 0; i < WINDOW_SIZE; i++) {
    readings[i] = initialValue;
    total += initialValue;
  }
}

void loop() {
  int rawValue = analogRead(SENSOR_PIN);
  total = total - readings[readIndex];
  readings[readIndex] = rawValue;
  total = total + readings[readIndex];
  readIndex = (readIndex + 1) % WINDOW_SIZE;
  average = total / WINDOW_SIZE;

  Serial.print("{\"raw\": ");
  Serial.print(rawValue);
  Serial.print(", \"filtered\": ");
  Serial.print(average);
  Serial.println("}");

  delay(50);
}
