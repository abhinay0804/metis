"""
Logo redaction using OpenCV template matching.
Loads logo templates from a directory and finds occurrences in input images.
Returns bounding boxes and can draw redaction boxes (black rectangles).
"""

from typing import List, Tuple, Dict, Any
import os
import cv2
import numpy as np


class LogoRedactor:
    def __init__(self, templates_dir: str = "templates/logos", match_threshold: float = 0.85):
        self.templates_dir = templates_dir
        self.match_threshold = match_threshold
        self.templates: List[Tuple[str, np.ndarray]] = []
        self._load_templates()

    def _load_templates(self) -> None:
        if not os.path.isdir(self.templates_dir):
            return
        for fname in os.listdir(self.templates_dir):
            path = os.path.join(self.templates_dir, fname)
            if not os.path.isfile(path):
                continue
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is None:
                continue
            # Convert to BGR for consistency; handle alpha channel by dropping it
            if img.ndim == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            self.templates.append((fname, img))

    def find_logos(self, image_bgr: np.ndarray) -> List[Dict[str, Any]]:
        if image_bgr is None or not self.templates:
            return []
        detections: List[Dict[str, Any]] = []
        img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        for tname, tmpl in self.templates:
            tmpl_gray = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
            th, tw = tmpl_gray.shape[:2]
            if img_gray.shape[0] < th or img_gray.shape[1] < tw:
                continue
            res = cv2.matchTemplate(img_gray, tmpl_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.match_threshold)
            for pt_y, pt_x in zip(*loc):
                x, y = int(pt_x), int(pt_y)
                detections.append({
                    "template": tname,
                    "bbox": [x, y, x + tw, y + th],
                    "score": float(res[pt_y, pt_x])
                })
        # Non-maximum suppression (simple): merge overlapping boxes
        detections = self._nms(detections, iou_threshold=0.3)
        return detections

    def _nms(self, detections: List[Dict[str, Any]], iou_threshold: float = 0.3) -> List[Dict[str, Any]]:
        if not detections:
            return detections
        boxes = np.array([d["bbox"] for d in detections], dtype=np.float32)
        scores = np.array([d.get("score", 1.0) for d in detections], dtype=np.float32)
        idxs = scores.argsort()[::-1]
        keep: List[int] = []
        while idxs.size > 0:
            i = idxs[0]
            keep.append(i)
            if idxs.size == 1:
                break
            iou = self._compute_iou(boxes[i], boxes[idxs[1:]])
            idxs = idxs[1:][iou < iou_threshold]
        return [detections[i] for i in keep]

    def _compute_iou(self, box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
        x1 = np.maximum(box[0], boxes[:, 0])
        y1 = np.maximum(box[1], boxes[:, 1])
        x2 = np.minimum(box[2], boxes[:, 2])
        y2 = np.minimum(box[3], boxes[:, 3])
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area_box = (box[2] - box[0]) * (box[3] - box[1])
        area_boxes = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        union = area_box + area_boxes - inter + 1e-6
        return inter / union

    def redact(self, image_bgr: np.ndarray, detections: List[Dict[str, Any]], color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        if not detections:
            return image_bgr
        redacted = image_bgr.copy()
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            cv2.rectangle(redacted, (x1, y1), (x2, y2), color, thickness=-1)
        return redacted


