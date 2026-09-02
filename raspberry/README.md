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

## Run

The virtual environment contains the Raspberry dependencies. Start Rafiki from
this directory with:

```bash
source .venv/bin/activate
python app/main.py "dis-moi quelque chose"
```

Voice output uses `espeak-ng` and the default PipeWire sink. Set
`RAFIKI_VOICE_ENABLED=false` to disable speech.

To use the webcam microphone and speech recognition:

```bash
python app/main.py --listen
```

Listening records five seconds at a time and uses the local French Vosk model.
Listening starts when speech is detected and stops after a short silence. Set
`RAFIKI_LISTEN_SECONDS` to change the maximum duration,
`RAFIKI_VOICE_THRESHOLD` to override the automatic microphone sensitivity, or
`RAFIKI_AUDIO_DEVICE` to select another ALSA capture device.

Speech uses the local French Piper voice model and falls back to `espeak-ng` if
the model is unavailable.

To test the webcam without starting the robot loop:

```bash
python app/main.py --capture
```

The image is captured from `/dev/video0` and written to `/tmp/rafiki/latest.jpg`.
Set `RAFIKI_CAMERA_DEVICE` or `RAFIKI_CAMERA_OUTPUT` to change these defaults.
When `RAFIKI_VISION_ENABLED=true`, the model decides whether to call
`capture_camera`; the user's exact wording does not trigger the camera directly.
