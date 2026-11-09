
import cv2
import mediapipe as mp
import numpy as np


class SegmentationEngine:

    def __init__(self):

        self.mp_selfie = mp.solutions.selfie_segmentation

        self.segmenter = self.mp_selfie.SelfieSegmentation(
            model_selection=0
        )

        self.last_mask = None

    def remove_background(self, camera_frame, background):

        # Resize background if dimensions do not match
        if background.shape[:2] != camera_frame.shape[:2]:
            background = cv2.resize(
                background,
                (camera_frame.shape[1], camera_frame.shape[0])
            )

        # Convert camera frame to RGB
        rgb = cv2.cvtColor(
            camera_frame,
            cv2.COLOR_BGR2RGB
        )

        # Run person segmentation
        results = self.segmenter.process(rgb)

        if results.segmentation_mask is None:
            return camera_frame

        # Smooth segmentation mask
        mask = cv2.GaussianBlur(
            results.segmentation_mask,
            (7, 7),
            0
        )

        mask = np.clip(mask, 0, 1)

        # Blend using OpenCV instead of float32 arrays
        mask = (mask * 255).astype(np.uint8)

        foreground = cv2.bitwise_and(
            camera_frame,
            camera_frame,
            mask=mask
        )

        inverse_mask = cv2.bitwise_not(mask)

        background_part = cv2.bitwise_and(
            background,
            background,
            mask=inverse_mask
        )

        output = cv2.add(
            foreground,
            background_part
        )

        return output

    def close(self):

        self.segmenter.close()
