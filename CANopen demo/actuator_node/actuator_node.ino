/*
Example of a Sensor node using the CanOpen library based on Canfestivino
Attach an actuator to pin 9 (this examples uses a SG90 servo)
Attach a MCP-2515 board using pin 10 as CS (you can change this in CO_can_Arduino.cpp if you need to)
  this example uses a Joy-It SBC-CAN01 MCP-2515 CAN Module
Upload sketch and open Serial Monitor (made sure baud is set to 115200)

Be sure to hook up both CANBus shields to the CAN network using CAN high and CAN low 
  Make sure not to mix up the cables. A suggestion is to hook them up using a breadboard for testing.

Once both sketches (sensor_node.ino and actuator_node.ino) are uploaded to two different arduinos

Run canopen_master_example.py on the Raspberry Pi system attached to CANbus network
 */

#include "canfestival.h" //#TODO move canfesival/canfestivino to a subfolder or something
#include "actuator_node.h" //generated using objdictedit.py

// These all need to be included because canfestival needs them <= according to original canfestivino
// commenting out does not result in compile errors, but may cause runtime errors

#include <SPI.h>
#include "mcp_can.h"
#include <Servo.h>

//#include <avr/io.h>
//#include <Arduino.h>
//#include "Timer.h"
//#include "digitalWriteFast.h"
//#include "BlinkPattern.h"


CO<3, 4> co;

// Setup the servo to pin 9
#define SENSOR_PIN A0

Servo actuator;                           //initialise the servo used in this example as an actuator
int val;                                  //holds mapped Actuator value

UNS32 writeActuatorCallback(const subindex * OD_entry, UNS16 bIndex, UNS8 bSubindex, UNS8 writeAccess) {
  Serial.print("Writing actuator:");
  Serial.println(Actuator);               //print incoming Actuator data (defined using objdictedit.py
  val = map(Actuator, 0, 1023, 0, 254);   //maps the value of the incoming Actuator data (0-1023) to a relative value between 0-254
  actuator.write(val);                    //move actuator
  delay(2);
  return 0;
}

void setup() {
  co.CO_Init(CAN_500KBPS, MCP_16MHz);     //intialise canopen via canbus
  //You can change CS pin in CO_can_Arduino.cpp line 8 (default: 10)

  actuator.attach(ACTUATOR_PIN);          //attach datapin of servo

  Serial.begin(115200);

  Serial.println("\nIf the following numbers are not 0, check OD callbacks and/or OD file");
  Serial.println(RegisterSetODentryCallBack(0x2001, 0, writeActuatorCallback), HEX);
  Serial.println("Setup Complete");
}

void loop() {
  co.CO_Cycle();
}
