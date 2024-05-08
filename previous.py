import cv2
import mediapipe as mp

# Initialize mediapipe Holistic model
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture
cap = cv2.VideoCapture(0)

k=1

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform holistic landmark detection
        holistic_results = holistic.process(rgb_frame)
        
        if holistic_results.face_landmarks:
            # Extract nose bridge end point
            nose_bridge_landmark = holistic_results.face_landmarks.landmark[33]
            ih, iw, _ = frame.shape
            nose_bridge_x = int(nose_bridge_landmark.x * iw)
            nose_bridge_y = int(nose_bridge_landmark.y * ih)
            # print(nose_bridge_x, nose_bridge_y)

            shoulder_right_landmark = holistic_results.pose_landmarks.landmark[11]
            shoulder_left_landmark = holistic_results.pose_landmarks.landmark[12]
            print(shoulder_left_landmark, shoulder_right_landmark)
            # if k==1:
            #         print(shoulder_left_landmark.z, "\n\n", shoulder_right_landmark.z)
                    #k=0
            #print(shoulder_right_landmark-shoulder_left_landmark)

            shoulder_left_z_value = shoulder_left_landmark.z
            shoulder_right_z_value = shoulder_right_landmark.z
            shoulder_left_x_value = shoulder_left_landmark.x
            shoulder_right_x_value = shoulder_right_landmark.x
            shoulder_left_y_value = shoulder_left_landmark.y
            shoulder_right_y_value = shoulder_right_landmark.y

            #print(type(shoulder_left_z_value))

            if abs(abs(shoulder_left_z_value) - abs(shoulder_right_z_value)) > 0.08:
                print("You Are wrong -> z -axis")
                break
            else:
                print("RIGHT")
                break
            
            #print(shoulder_right_y_value, shoulder_left_y_value)

            # Draw a circle at the nose bridge end point
            cv2.circle(frame, (nose_bridge_x, nose_bridge_y), 5, (0, 255, 0), -1)

            # Draw face landmarks
            mp_drawing.draw_landmarks(frame, holistic_results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)

            # Draw pose landmarks (including shoulders)
            mp_drawing.draw_landmarks(frame, holistic_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            # Draw left hand landmarks
            # mp_drawing.draw_landmarks(frame, holistic_results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            # # Draw right hand landmarks
            # mp_drawing.draw_landmarks(frame, holistic_results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        cv2.imshow('Nose Bridge Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()