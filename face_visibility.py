import cv2


def check_face_visibility(frame, face):
    """
    Basic face-visibility check.

    Glasses are allowed.
    The check looks for whether enough useful facial
    detail is visible for recognition.
    """

    if frame is None or face is None:
        return False

    x, y, w, h = face[:4]

    x = max(0, int(x))
    y = max(0, int(y))
    w = int(w)
    h = int(h)

    if w <= 0 or h <= 0:
        return False

    # Crop face
    face_image = frame[
        y:y + h,
        x:x + w
    ]

    if face_image.size == 0:
        return False

    # Convert to grayscale
    gray = cv2.cvtColor(
        face_image,
        cv2.COLOR_BGR2GRAY
    )

    # Check whether the face contains
    # enough intensity variation.
    contrast = gray.std()

    # Very low variation usually means
    # the face is heavily obscured or unusable.
    if contrast < 15:
        return False

    return True