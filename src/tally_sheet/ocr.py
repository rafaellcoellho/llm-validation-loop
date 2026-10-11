import numpy as np
from rapidocr import RapidOCR

LINE_TOLERANCE = 0.6


class OcrReader:
    def __init__(self):
        self._engine = RapidOCR()

    def read(self, image):
        result = self._engine(np.array(image.convert("RGB")))
        if result.txts is None:
            return ""

        boxes = [
            _box_geometry(box, text) for box, text in zip(result.boxes, result.txts)
        ]

        return "\n".join(_join_line(line) for line in _group_lines(boxes))


def _box_geometry(box, text):
    ys = [point[1] for point in box]
    xs = [point[0] for point in box]

    return {"top": min(ys), "bottom": max(ys), "left": min(xs), "text": text}


def _group_lines(boxes):
    lines = []

    for box in sorted(boxes, key=lambda item: item["top"]):
        if lines and _same_line(lines[-1][-1], box):
            lines[-1].append(box)
        else:
            lines.append([box])

    return lines


def _same_line(previous, box):
    height = previous["bottom"] - previous["top"]

    return abs(box["top"] - previous["top"]) < height * LINE_TOLERANCE


def _join_line(line):
    return "  ".join(box["text"] for box in sorted(line, key=lambda item: item["left"]))
