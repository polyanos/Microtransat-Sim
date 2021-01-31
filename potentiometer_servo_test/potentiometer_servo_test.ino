//this sketch can be used to test out servos and a potentiometer on a single arduino

#include <Servo.h>
#include <SPI.h>

#define ACT_1 9 //init servo pins
#define ACT_2 10
#define potPin A0   //init potentiometer pin

int potValue=0;

Servo act1;   //init servos
Servo act2; 

void setup() {
  Serial.begin(115200);
  pinMode(potPin, INPUT); //attach potentiometer pin
  act1.attach(ACT_1); //attach datapin of servo1
  act2.attach(ACT_2); //attach datapin of servo2
}

void loop() {
  potValue = analogRead(potPin);  //read potentiometer state
  potValue = map(potValue,0,1023,0,255);  //map the potentiometer value(0-1024) to be able to use it on the servos (0-255)
  Serial.println(potValue);

  act1.attach(ACT_1); //attach datapin of servo
  act2.attach(ACT_2); //attach datapin of servo

  act1.write(potValue);   //write mapped values to actuators
  act2.write(potValue);
}
