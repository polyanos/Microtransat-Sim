/*
Example of a Actuator node using the CanOpen library based on Canfestivino
Attach a sensor to A0 (this example uses a potentiometer)
Attach a MCP-2515 board using pin 10 as CS (you can change this in CO_can_Arduino.cpp if you need to)
  this example uses a Seeed-Studio CANBus shield MCP2515
Upload sketch and open Serial Monitor (made sure baud is set to 115200)
Run canopen_master_example.py on the Raspberry Pi system attached to canbus network
 */

#include "canfestival.h" //include the CANFestivino header file
#include "sensor_node.h" //generated using objdictedit.py


// These all need to be included because CANFestival needs them <= according to original CANFestivino
// commenting out does not result in compile errors, but may cause runtime errors

#include <SPI.h>
#include "mcp_can.h"

//#include <avr/io.h>
//#include <Arduino.h>
//#include "Timer.h"
//#include "digitalWriteFast.h"
//#include "BlinkPattern.h"
//#include <Servo.h>

CO<3, 4> co;

#define SENSOR_PIN A0                                               // Setup the potentiometer to analog pin 0

UNS32 readSensorCallback(const subindex * OD_entry, UNS16 bIndex, UNS8 bSubindex, UNS8 writeAccess) {
  Serial.print("Reading sensor: ");
  Serial.println(analogRead(SENSOR_PIN));                           //Reads potentiometer value

  if (!writeAccess)                                                 //prevents runtime errors
    delay(10);
  Sensor = analogRead(SENSOR_PIN);                                  //Assigns potentiometer value to Sensor object (defined using object dictionary)
  ObjDict_PDO_status[ObjDict_Data.currentPDO].event_trigger = 1;    //Pushes to CANopen network

  return 0;
}

void setup() {
  co.CO_Init(CAN_500KBPS, MCP_16MHz);                               //intialise canopen via canbus
  //You can change CS pin in CO_can_Arduino.cpp line 8 (default: 10)

  pinMode(SENSOR_PIN, INPUT);                                       //setup potmeter pin

  Serial.begin(115200);

  Serial.println("\nIf the following numbers are not 0, check OD callbacks and/or OD file");
  Serial.println((RegisterSetODentryCallBack(0x2000, 0, readSensorCallback)), HEX);
  Serial.println("Setup Complete");
}

void loop() {
  co.CO_Cycle();
}
