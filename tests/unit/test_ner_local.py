import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from server.detectors.ensemble_detector import EnsembleDetector

text = "NAMA ABHINAY 23BPS1080 RYALI LAKSHMAN 23BPS1026"

try:
    detector = EnsembleDetector()
    print("Detections:")
    for d in detector.detect_entities(text):
        print(d)
except Exception as e:
    import traceback
    traceback.print_exc()
