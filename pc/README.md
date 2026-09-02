# PC / local model runtime

This folder is intended for the local model host that runs the Bonsai 27B class model or another compatible local LLM.

## Responsibilities

- host the local inference server
- expose a simple HTTP API to the Raspberry Pi
- optionally serve vision endpoints for camera analysis

## Suggested API flow

- `/health` -> returns service status
- `/chat` -> send prompt and get response
- `/vision` -> send an image and ask for description

## Notes

The PC should run the heavy model and provide the agent with a clean, simple interface.

## Example service entry point

- `server/app.py`
