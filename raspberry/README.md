# Raspberry Pi code

This folder contains the Raspberry-side orchestration layer.

## Responsibilities

- manage audio input/output
- run the local robot agent
- call tools
- bridge commands to Arduino over serial
- optionally call the local model server on the PC

## Suggested runtime flow

1. Receive spoken sentence or text command
2. Send high-level intent to local model or agent
3. Decide which tool to call
4. Trigger voice output or gestures
5. Send final commands to Arduino

## Main entry point

- `app/main.py`
