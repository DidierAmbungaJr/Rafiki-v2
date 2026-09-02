# Rafiki Robot Companion

This repository contains a simple but solid scaffold for a local robot companion built around:

- Raspberry Pi 5 as orchestrator
- Arduino Mega for body control
- PC local model runtime for Bonsai or a compatible local LLM
- voice + vision tools
- no visible reasoning, only tool-driven behavior

## Project layout

- `raspberry/`: Raspberry orchestration layer
- `arduino/`: Mega firmware for servos and TFT expressions
- `pc/`: local LLM or API host for the model runtime

## Architecture

```text
User speech / interaction
        |
        v
 Raspberry Pi 5
   - STT
   - TTS
   - tool orchestration
   - serial bridge to Arduino
   - local agent loop
        |
        +----> Arduino Mega ----> 2 servos + TFT screen
        |
        +----> PC local LLM ----> Bonsai 27B / compatible local model
        |
        +----> Camera (on demand only)
```

## Important design choices

- Vision is used only on demand
- No reasoning chain is exposed to the user
- The model decides high-level intents, not low-level servo values
- Hardware safety is handled by the Raspberry + Arduino boundary

## Suggested MVP

1. Listen to the user
2. Respond with voice
3. Show expression on TFT
4. Trigger simple leg motion
5. Support vision only when asked

This scaffold is intentionally small and resilient for an embedded robot project.
