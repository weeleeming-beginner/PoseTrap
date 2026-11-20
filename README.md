# PoseTrap

PoseTrap is a local, consent-based pose challenge and funny-video maker. It uses your webcam to recognise a couple of simple poses, records only when you press the record key, and asks you to review a clip before exporting it.

## Features

- Live webcam preview with a pose guide
- Two starter challenges: **Hands Up** and **T-Pose**
- On-device pose detection with MediaPipe
- Manual recording controls (nothing records until you press `R`)
- Review a recording before exporting or deleting it
- Adds a playful caption to the exported video
- Optional background music using FFmpeg
- No cloud upload, face recognition, or automatic sharing

> **Consent matters:** Tell everyone who may appear in the video what the app does and get their permission before recording. Keep clips private unless everyone agrees to share them.

## 1. Requirements

- Python 3.10–3.12 (64-bit recommended)
- A webcam
- Windows, macOS, or Linux
- Optional: FFmpeg, if you want to add a music track

## 2. Install

Open a terminal in this project folder.

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ubuntu / WSL

For a webcam app, run this in a Linux desktop session with camera access. A Windows webcam may not be available inside WSL by default; if the camera does not open, run PoseTrap directly on Windows.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run

```bash
python app.py
```

If you have more than one camera, choose its index:

```bash
python app.py --camera 1
```

## 4. Controls

| Key | Action |
|---|---|
| `R` | Start / stop recording |
| `N` | Next pose challenge |
| `Q` or `Esc` | Quit |
| `E` | Export after reviewing a clip |
| `D` | Delete the reviewed clip |

When recording stops, a review window opens. Press **E** to create the final captioned video or **D** to discard it. The app does not upload or share anything.

## 5. Optional background music

Install FFmpeg and place an audio file you have permission to use in the project folder. Then run:

```bash
python app.py --music music.mp3
```

PoseTrap first creates the captioned video, then asks FFmpeg to combine it with your music. If FFmpeg is not installed or the audio file cannot be used, the captioned silent video is still exported.

Use music you own or are licensed to use.

## Project structure

```text
PoseTrap/
├── app.py
├── pose_detector.py
├── video_export.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Troubleshooting

- **Camera won't open:** close other apps using the webcam; try `--camera 1`.
- **Import error for MediaPipe:** use Python 3.10, 3.11, or 3.12 in a fresh virtual environment, then reinstall requirements.
- **WSL cannot see the camera:** run the project in Windows, or configure camera access for your Linux environment.
- **Pose not detected:** stand far enough back for your upper body and arms to be visible, and make sure the room has enough light.

## Current version

This is the first MVP. It recognises two simple upper-body poses. More challenges, selectable editing styles, and richer sound effects can be added in later versions.
