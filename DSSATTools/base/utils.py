"""
Utility functions that can be useful
"""
import chardet

def detect_encoding(file_path):
    # detect the file encoding before opening file
    detector = chardet.UniversalDetector()
    with open(file_path, "rb") as f:
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    return detector.result["encoding"]