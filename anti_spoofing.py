import math


class LivenessDetector:

    def __init__(self):

        self.previous_center = None
        self.movement_detected = False


    def reset(self):

        self.previous_center = None
        self.movement_detected = False


    def check(self, frame, face):

        if frame is None or face is None:
            return False

        x, y, w, h = face[:4]

        center_x = x + w / 2
        center_y = y + h / 2

        current_center = (
            center_x,
            center_y
        )

        if self.previous_center is None:

            self.previous_center = current_center

            return False

        previous_x, previous_y = self.previous_center

        movement = math.sqrt(
            (center_x - previous_x) ** 2 +
            (center_y - previous_y) ** 2
        )

        self.previous_center = current_center

        if movement >= 3:

            self.movement_detected = True

        return self.movement_detected