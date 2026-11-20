"""Simple upper-body pose recognition using MediaPipe Pose."""

from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp


@dataclass
class PoseResult:
    landmarks: object
    detected_pose: Optional[str]


class PoseDetector:
    """Detects the two starter challenges: hands-up and T-pose."""

    def __init__(self, min_detection_confidence: float = 0.6,
                 min_tracking_confidence: float = 0.6) -> None:
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame) -> PoseResult:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._pose.process(rgb)
        if not result.pose_landmarks:
            return PoseResult(None, None)

        points = result.pose_landmarks.landmark
        pose = mp.solutions.pose

        left_shoulder = points[pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = points[pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_wrist = points[pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = points[pose.PoseLandmark.RIGHT_WRIST.value]
        left_elbow = points[pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = points[pose.PoseLandmark.RIGHT_ELBOW.value]

        visible = all(p.visibility > 0.5 for p in (
            left_shoulder, right_shoulder, left_wrist, right_wrist,
            left_elbow, right_elbow
        ))

        detected = None
        if visible:
            hands_up = (
                left_wrist.y < left_shoulder.y - 0.08
                and right_wrist.y < right_shoulder.y - 0.08
            )
            if hands_up:
                detected = "hands_up"
            else:
                shoulder_width = abs(left_shoulder.x - right_shoulder.x)
                arms_out = (
                    left_wrist.x < left_shoulder.x - shoulder_width * 0.35
                    and right_wrist.x > right_shoulder.x + shoulder_width * 0.35
                )
                wrists_level = (
                    abs(left_wrist.y - left_shoulder.y) < 0.18
                    and abs(right_wrist.y - right_shoulder.y) < 0.18
                )
                elbows_level = (
                    abs(left_elbow.y - left_shoulder.y) < 0.22
                    and abs(right_elbow.y - right_shoulder.y) < 0.22
                )
                if arms_out and wrists_level and elbows_level:
                    detected = "t_pose"

        return PoseResult(result.pose_landmarks, detected)

    def draw_landmarks(self, frame, landmarks) -> None:
        if landmarks is not None:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
            )

    def close(self) -> None:
        self._pose.close()
