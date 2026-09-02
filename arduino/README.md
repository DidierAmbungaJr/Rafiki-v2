# Arduino Mega code

This folder holds the Arduino firmware for the robot body.

## Responsibilities

- show facial expressions on the TFT 3.5" screen
- control the two leg servos
- run simple animations and postures
- accept commands from the Raspberry over serial

## Suggested command protocol

JSON commands like:

```json
{"type":"expression","value":"happy"}
{"type":"posture","value":"dance"}
{"type":"servo","left":30,"right":-30}
{"type":"idle"}
```

## Entry point

- `firmware/rafiki_mega.ino`
