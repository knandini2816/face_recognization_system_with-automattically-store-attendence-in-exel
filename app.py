import streamlit as st
import cv2
import time

from modules.face_recognition import (
    recognize_student,
    get_face_status,
    detect_faces
)

from modules.image_quality import (
    check_brightness,
    improve_lighting
)

from modules.anti_spoofing import LivenessDetector

from database.attendance import (
    mark_attendance,
    already_marked,
    get_current_session,
    record_capture,
    get_capture_count
)


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Smart Face Recognition Attendance",
    page_icon="📷",
    layout="centered"
)

st.title(
    "📷 Smart Face Recognition Attendance System"
)

st.write(
    "Each student must start the camera, "
    "verify their face and submit attendance."
)


# ==================================================
# SESSION STATE
# ==================================================

if "camera_running" not in st.session_state:
    st.session_state.camera_running = False

if "recognized_student" not in st.session_state:
    st.session_state.recognized_student = None

if "capture_count" not in st.session_state:
    st.session_state.capture_count = 0


# ==================================================
# START SCREEN
# ==================================================

if (
    not st.session_state.camera_running
    and st.session_state.recognized_student is None
):

    st.info(
        "👤 Ready for the next student."
    )

    if st.button(
        "▶️ Start Camera",
        use_container_width=True
    ):

        st.session_state.camera_running = True

        st.session_state.recognized_student = None

        st.session_state.capture_count = 0

        st.rerun()


# ==================================================
# CAMERA
# ==================================================

if (
    st.session_state.camera_running
    and st.session_state.recognized_student is None
):

    camera_placeholder = st.empty()

    status_placeholder = st.empty()

    status_placeholder.info(
        "📷 Camera opening... "
        "Look at the camera."
    )


    camera = cv2.VideoCapture(0)


    if not camera.isOpened():

        st.error(
            "❌ Unable to open camera."
        )

        st.session_state.camera_running = False

        st.stop()


    liveness_detector = LivenessDetector()

    student_found = None


    # ==================================================
    # CAMERA LOOP
    # ==================================================

    for _ in range(300):

        ret, frame = camera.read()

        if not ret:
            continue


        # ----------------------------------------------
        # IMAGE QUALITY
        # ----------------------------------------------

        if not check_brightness(frame):

            status_placeholder.warning(
                "💡 Low lighting detected. "
                "Improving image..."
            )

            frame = improve_lighting(frame)


        # ----------------------------------------------
        # DISPLAY
        # ----------------------------------------------

        display_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        camera_placeholder.image(
            display_frame,
            channels="RGB",
            use_container_width=True
        )


        # ----------------------------------------------
        # FACE STATUS
        # ----------------------------------------------

        face_status = get_face_status(frame)


        if face_status == "no_face":

            status_placeholder.info(
                "👀 No face detected. "
                "Please look at the camera."
            )

            continue


        if face_status == "multiple_faces":

            status_placeholder.warning(
                "⚠️ Only ONE student should "
                "be in front of the camera."
            )

            continue


        # ----------------------------------------------
        # FACE DETECTION
        # ----------------------------------------------

        faces = detect_faces(frame)

        if len(faces) != 1:
            continue

        face = faces[0]


        # ----------------------------------------------
        # LIVENESS
        # ----------------------------------------------

        live = liveness_detector.check(
            frame,
            face
        )


        if not live:

            status_placeholder.info(
                "👤 Face detected. "
                "Please move slightly."
            )

            continue


        # ----------------------------------------------
        # RECOGNITION
        # ----------------------------------------------

        student = recognize_student(frame)


        if student is not None:

            student_found = student


            # ==========================================
            # RECORD CAPTURE FOR THIS STUDENT
            # ==========================================

            total_count = record_capture(
                student["student_id"]
            )

            st.session_state.capture_count = (
                total_count
            )


            status_placeholder.success(
                f"✅ Face recognized! "
                f"Capture Count: {total_count}"
            )

            break


        else:

            status_placeholder.warning(
                "❌ Face not recognized. "
                "Please try again."
            )


    # ==================================================
    # RELEASE CAMERA
    # ==================================================

    camera.release()


    # ==================================================
    # STUDENT FOUND
    # ==================================================

    if student_found is not None:

        st.session_state.recognized_student = (
            student_found
        )

        st.session_state.camera_running = False

        st.rerun()


    else:

        st.session_state.camera_running = False

        st.warning(
            "⚠️ No registered student was recognized."
        )

        st.info(
            "Click ▶️ Start Camera to try again."
        )

        st.stop()


# ==================================================
# STUDENT DETAILS
# ==================================================

if st.session_state.recognized_student is not None:

    student = st.session_state.recognized_student


    st.success(
        "✅ Face recognized successfully!"
    )


    st.subheader(
        "👤 Student Details"
    )


    st.write(
        f"**Name:** {student['name']}"
    )

    st.write(
        f"**Roll Number:** "
        f"{student['roll_number']}"
    )

    st.write(
        f"**Department:** "
        f"{student['department']}"
    )

    st.write(
        f"**Year:** "
        f"{student['year']}"
    )


    # ----------------------------------------------
    # CAPTURE COUNT
    # ----------------------------------------------

    capture_count = get_capture_count(
        student["student_id"]
    )

    st.write(
        f"**📸 Capture Count:** "
        f"{capture_count}"
    )


    # ----------------------------------------------
    # CONFIDENCE
    # ----------------------------------------------

    confidence = student.get(
        "confidence",
        0
    )

    st.write(
        f"**Recognition Confidence:** "
        f"{confidence:.2f}"
    )


    # ==================================================
    # SESSION
    # ==================================================

    current_session = get_current_session()


    if current_session is None:

        st.warning(
            "⏰ Attendance is currently closed."
        )

        st.info(
            "Morning: 9:00 AM - 12:00 PM\n\n"
            "Afternoon: 1:00 PM - 4:00 PM"
        )


        if st.button(
            "🔄 Return to Start",
            use_container_width=True
        ):

            st.session_state.recognized_student = None

            st.session_state.camera_running = False

            st.session_state.capture_count = 0

            st.rerun()


    else:

        st.info(
            f"🕐 Current Session: "
            f"**{current_session}**"
        )


        # ==================================================
        # DUPLICATE ATTENDANCE
        # ==================================================

        if already_marked(
            student["student_id"]
        ):

            st.warning(
                "⚠️ Attendance Already Marked"
            )

            st.write(
                f"{student['name']} "
                f"({student['roll_number']}) "
                f"has already submitted attendance "
                f"for this session."
            )


            if st.button(
                "🔄 Return to Start",
                use_container_width=True
            ):

                st.session_state.recognized_student = None

                st.session_state.camera_running = False

                st.session_state.capture_count = 0

                st.rerun()


        # ==================================================
        # SUBMIT ATTENDANCE
        # ==================================================

        else:

            if st.button(
                "✅ Submit Attendance",
                use_container_width=True
            ):

                success = mark_attendance(
                    student,
                    capture_count
                )


                if success:

                    st.success(
                        "✅ Attendance submitted successfully!"
                    )

                    st.info(
                        "💾 Saved to SQLite and Excel."
                    )

                    time.sleep(1)


                    # ----------------------------------
                    # RESET
                    # ----------------------------------

                    st.session_state.recognized_student = None

                    st.session_state.camera_running = False

                    st.session_state.capture_count = 0


                    # ----------------------------------
                    # NEXT STUDENT STARTS FROM BEGINNING
                    # ----------------------------------

                    st.rerun()


                else:

                    st.error(
                        "❌ Attendance could not be submitted."
                    )