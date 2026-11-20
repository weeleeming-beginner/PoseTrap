"""PoseTrap: a local, consent-based webcam pose challenge."""

import argparse
from datetime import datetime
from pathlib import Path
import sys

import cv2

from pose_detector import PoseDetector
from video_export import export_captioned_video


CHALLENGES = [
    {
        "id": "hands_up",
        "title": "HANDS UP!",
        "hint": "Raise BOTH hands above your shoulders",
        "caption": "I HAVE BEEN SUMMONED 🙌",
    },
    {
        "id": "t_pose",
        "title": "T-POSE!",
        "hint": "Stretch both arms out like the letter T",
        "caption": "ASSERTING DOMINANCE IN T-POSE",
    },
]


def draw_text(frame, text, y, scale=0.75, color=(255, 255, 255)):
    cv2.putText(
        frame, text, (22, y), cv2.FONT_HERSHEY_SIMPLEX,
        scale, color, 2, cv2.LINE_AA
    )


def review_clip(path: Path) -> bool:
    """Show the clip and return True only when the user approves export."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        print("Could not open the recording for review.")
        return False

    print("\nREVIEW: watch the clip in the preview window.")
    print("Press E to approve export, or D to discard it.")
    delay = max(1, int(1000 / (cap.get(cv2.CAP_PROP_FPS) or 24)))
    approved = False

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = cap.read()
            if not ok:
                break
        draw_text(frame, "REVIEW YOUR CLIP", 38, 0.8, (0, 230, 255))
        draw_text(frame, "E = EXPORT    D = DISCARD", 76, 0.65)
        cv2.imshow("PoseTrap - Review", frame)
        key = cv2.waitKey(delay) & 0xFF
        if key in (ord("e"), ord("E")):
            approved = True
            break
        if key in (ord("d"), ord("D"), 27):
            break

    cap.release()
    cv2.destroyWindow("PoseTrap - Review")
    return approved


def main():
    parser = argparse.ArgumentParser(description="PoseTrap webcam pose challenge")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    parser.add_argument("--music", type=Path, help="Optional music file for the final export")
    args = parser.parse_args()

    print("PoseTrap is a local pose challenge.")
    print("Only record people who know about the recording and have agreed.")
    try:
        consent = input("Have everyone who may appear agreed to be recorded? [y/N] ")
    except EOFError:
        return
    if consent.strip().lower() != "y":
        print("No recording started. Get permission first.")
        return

    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        print("Could not open the webcam. Try --camera 1 or close other camera apps.")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = PoseDetector()
    challenge_index = 0
    recording = False
    writer = None
    recording_path = None
    pose_streak = 0
    completed = False
    fps = camera.get(cv2.CAP_PROP_FPS)
    if not fps or fps < 5:
        fps = 30.0

    Path("recordings").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)

    print("\nControls: R record/stop | N next challenge | Q quit")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Lost the webcam feed.")
                break

            frame = cv2.flip(frame, 1)
            challenge = CHALLENGES[challenge_index]
            result = detector.process(frame)
            detector.draw_landmarks(frame, result.landmarks)

            if result.detected_pose == challenge["id"]:
                pose_streak += 1
            else:
                pose_streak = 0

            if pose_streak >= 8:
                completed = True

            draw_text(frame, "POSETRAP", 36, 0.9, (0, 220, 255))
            draw_text(frame, challenge["title"], 78, 0.8)
            draw_text(frame, challenge["hint"], 116, 0.58)
            status = "POSE COMPLETE! NICE ONE" if completed else "Waiting for pose..."
            draw_text(frame, status, 158, 0.65,
                      (80, 255, 80) if completed else (255, 255, 255))

            if recording:
                draw_text(frame, "● RECORDING  (R to stop)", 202, 0.65, (0, 0, 255))
                writer.write(frame)
            else:
                draw_text(frame, "NOT RECORDING  (R to start)", 202, 0.6, (80, 220, 255))

            draw_text(frame, "R: record/stop   N: next pose   Q: quit", frame.shape[0] - 22, 0.55)
            cv2.imshow("PoseTrap - Live Camera", frame)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), ord("Q"), 27):
                break
            elif key in (ord("n"), ord("N")) and not recording:
                challenge_index = (challenge_index + 1) % len(CHALLENGES)
                pose_streak = 0
                completed = False
            elif key in (ord("r"), ord("R")):
                if not recording:
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    recording_path = Path("recordings") / f"pose_{stamp}.mp4"
                    height, width = frame.shape[:2]
                    writer = cv2.VideoWriter(
                        str(recording_path),
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        fps, (width, height)
                    )
                    if not writer.isOpened():
                        print("Could not start video recording.")
                        writer = None
                        recording_path = None
                        continue
                    recording = True
                    print(f"Recording started: {recording_path}")
                else:
                    recording = False
                    writer.release()
                    writer = None
                    print(f"Recording stopped: {recording_path}")
                    cv2.destroyWindow("PoseTrap - Live Camera")
                    if review_clip(recording_path):
                        caption = CHALLENGES[challenge_index]["caption"]
                        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output = Path("exports") / f"posetrap_{stamp}.mp4"
                        try:
                            final_path = export_captioned_video(
                                recording_path, output, caption, args.music
                            )
                            print(f"Export approved: {final_path}")
                        except RuntimeError as exc:
                            print(f"Export failed: {exc}")
                    else:
                        recording_path.unlink(missing_ok=True)
                        print("Clip discarded.")
                    recording_path = None
                    pose_streak = 0
                    completed = False
                    cv2.namedWindow("PoseTrap - Live Camera")

    finally:
        if writer is not None:
            writer.release()
        camera.release()
        detector.close()
        cv2.destroyAllWindows()
        print("PoseTrap closed. Your videos stay on this device.")


if __name__ == "__main__":
    main()
