import cv2
import os
import csv

YUNET_MODEL = "models/face_detection_yunet_2023mar.onnx"
SFACE_MODEL = "models/face_recognition_sface_2021dec.onnx"
CSV_PATH = "data/students.csv"
PHOTO_FOLDER = "data/students"

detector = cv2.FaceDetectorYN.create(
    YUNET_MODEL,
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)

recognizer = cv2.FaceRecognizerSF.create(
    SFACE_MODEL,
    ""
)


def load_students():
    students = []

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for student in reader:

            photo_path = os.path.join(
                PHOTO_FOLDER,
                student["photo"]
            )

            students.append({
                "student_id": student["student_id"],
                "roll_number": student["roll_number"],
                "name": student["name"],
                "department": student["department"],
                "year": student["year"],
                "photo": photo_path
            })

    return students


def detect_faces(image):

    height, width = image.shape[:2]

    detector.setInputSize(
        (width, height)
    )

    _, faces = detector.detect(image)

    if faces is None:
        return []

    return faces


def get_face_status(image):

    faces = detect_faces(image)

    if len(faces) == 0:
        return "no_face"

    if len(faces) > 1:
        return "multiple_faces"

    return "single_face"


def get_feature(image):

    faces = detect_faces(image)

    # No face
    if len(faces) == 0:
        return None

    # More than one face
    if len(faces) > 1:
        return None

    face = faces[0]

    aligned_face = recognizer.alignCrop(
        image,
        face
    )

    feature = recognizer.feature(
        aligned_face
    )

    return feature


def recognize_student(camera_frame):

    face_status = get_face_status(
        camera_frame
    )

    # No face
    if face_status == "no_face":
        return None

    # Multiple faces
    if face_status == "multiple_faces":
        return None

    camera_feature = get_feature(
        camera_frame
    )

    if camera_feature is None:
        return None

    students = load_students()

    best_student = None
    best_score = -1

    for student in students:

        if not os.path.exists(
            student["photo"]
        ):
            continue

        registered_image = cv2.imread(
            student["photo"]
        )

        if registered_image is None:
            continue

        registered_feature = get_feature(
            registered_image
        )

        if registered_feature is None:
            continue

        score = recognizer.match(
            camera_feature,
            registered_feature,
            cv2.FaceRecognizerSF_FR_COSINE
        )

        if score > best_score:

            best_score = score
            best_student = student

    if best_student is not None:

        CONFIDENCE_THRESHOLD = 0.40

        if best_score < CONFIDENCE_THRESHOLD:
            return None

        best_student["confidence"] = float(
            best_score
        )

        return best_student

    return None