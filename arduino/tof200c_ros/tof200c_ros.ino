#include "Adafruit_VL53L0X.h"

// SHUT 핀 번호 설정
#define SHT_LOX1 4 

Adafruit_VL53L0X lox = Adafruit_VL53L0X();

void setup() {
  Serial.begin(115200);

  // SHUT 핀을 출력 모드로 설정
  pinMode(SHT_LOX1, OUTPUT);

  // 1. 센서 리셋 (잠시 껐다가 켜기)

  digitalWrite(SHT_LOX1, LOW);  // 센서 끄기
  delay(10);
  digitalWrite(SHT_LOX1, HIGH); // 센서 켜기
  delay(10);

  // 2. 센서 초기화
  if (!lox.begin()) {

    while (1);
  }

  Serial.println(F("VL53L0X 측정 시작...\n"));
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;
    
  lox.rangingTest(&measure, false); 

  if (measure.RangeStatus != 4) {

    Serial.println(measure.RangeMilliMeter);
  } 

  delay(50);
}