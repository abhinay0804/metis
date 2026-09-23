import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from server.detectors.ensemble_detector import EnsembleDetector

text = "JOHN DOE EMP001234 JANE SMITH EMP005678"

try:
    detector = EnsembleDetector()
    print("Detections:")
    for d in detector.detect_entities(text):
        print(d)
except Exception as e:
    import traceback
    traceback.print_exc()
