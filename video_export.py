"""Caption a reviewed clip and optionally add a music track."""

import shutil
import subprocess
from pathlib import Path

import cv2


def export_captioned_video(
    source: Path,
    destination: Path,
    caption: str,
    music: Path | None = None,
) -> Path:
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open recorded clip: {source}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    destination.parent.mkdir(parents=True, exist_ok=True)

    silent_path = destination.with_name(destination.stem + "_silent.mp4")
    writer = cv2.VideoWriter(
        str(silent_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError("Could not create the output video.")

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        # Add a dark strip so the caption stays readable.
        strip_height = max(54, height // 9)
        overlay = frame.copy()
        cv2.rectangle(
            overlay, (0, height - strip_height), (width, height),
            (20, 20, 20), -1
        )
        frame = cv2.addWeighted(overlay, 0.72, frame, 0.28, 0)
        font_scale = max(0.65, width / 1100)
        thickness = max(1, width // 700)
        cv2.putText(
            frame, caption[:70], (20, height - strip_height // 3),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255),
            thickness, cv2.LINE_AA
        )
        writer.write(frame)

    capture.release()
    writer.release()

    if music and music.exists() and shutil.which("ffmpeg"):
        command = [
            "ffmpeg", "-y", "-i", str(silent_path), "-stream_loop", "-1",
            "-i", str(music), "-shortest", "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(destination),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            silent_path.unlink(missing_ok=True)
            return destination
        except (subprocess.CalledProcessError, OSError):
            # Keep a valid silent export if FFmpeg/music muxing fails.
            pass

    silent_path.replace(destination)
    return destination
