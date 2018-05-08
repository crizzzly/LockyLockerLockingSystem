#include <Arduino.h>

#define NUMLOCKS 3    // define number of locks you want to switch
#define WAIT     8000 // wait for 8 sec

int doors [] = { 3, 4, 5 }; // on which pins are the locks connected
bool doorStates [NUMLOCKS]; // array to save the doorStates

bool gotdoorStates       = false; // read new values or not?
unsigned long prevMillis = 0;     // save the current millis to compare if wait time is over

// Using http://slides.justen.eng.br/python-e-arduino as refference

void setup()
{
    // later: include error handling if NUMLOCKS != sizeof(doors)
    pinMode(doors[0], OUTPUT);
    pinMode(doors[1], OUTPUT);
    pinMode(doors[2], OUTPUT);
    Serial.begin(9600);
}

void loop()
{
    // save incoming values to doorStates if Serial connection is available
    if (Serial.available()) {
        for (int i = 0; i < NUMLOCKS; i++) {
            doorStates[i] = Serial.read();
        }
        // set gotdoorStates to true that loop won't run next digitalWrite accidentially
        gotdoorStates = true;
    }
    // unlock the doors
    if (gotdoorStates) {
        for (int i = 0; i < NUMLOCKS; i++) {
            digitalWrite(doors[i], doorStates[i]);
        }

        // Check if enough time has passed to lock doors again
        unsigned long currentMillis = millis();
        if (currentMillis - prevMillis >= WAIT) {
            prevMillis = currentMillis;
            for (int i = 0; i < NUMLOCKS; i++) {
                digitalWrite(doors[i], 0);
            }
            gotdoorStates = false;
        }
    }
}
