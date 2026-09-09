import cv2
import mediapipe as mp
import numpy as np
from twilio.rest import Client
import requests
import pygame
import threading
import time

pygame.mixer.init()
ALARM_FILE = "alarm.wav"

mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

CLOSED_COUNTER = 0
YAWN_COUNTER = 0

EYE_THRESHOLD = 0.015
MOUTH_THRESHOLD = 0.040
DANGER_FRAMES = 90
YAWN_FRAMES = 45

TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN  = "your_auth_token_here"
TWILIO_PHONE_NUM   = "+1234567890"
TARGET_PHONE_NUM   = "+91XXXXXXXXXX"

def play_local_alarm_in_background():
    try:
        siren = pygame.mixer.Sound(ALARM_FILE)
        siren.play(loops=-1)
        print("[ALARM THREAD] Cabin warning siren activated successfully!")
    except Exception as audio_err:
        print(f"[ALARM THREAD INFO] Audio playback skipped: {audio_err}")

with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5, refine_landmarks=True) as face, \
     mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    print("[INFO] SafeDrive AI Active. Monitoring driver metrics...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Webcam hardware disconnected or unavailable.")
            break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_results = face.process(rgb_frame)
        pose_results = pose.process(rgb_frame)

        trigger_emergency = False
        display_status = "Status: Monitoring Driver"
        status_color = (0, 255, 0)

        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                
                top_eye = face_landmarks.landmark[159]
                bottom_eye = face_landmarks.landmark[145]
                
                top_lip = face_landmarks.landmark[13]
                bottom_lip = face_landmarks.landmark[14]
                
                p1_eye = np.array([top_eye.x, top_eye.y])
                p2_eye = np.array([bottom_eye.x, bottom_eye.y])
                
                p1_lip = np.array([top_lip.x, top_lip.y])
                p2_lip = np.array([bottom_lip.x, bottom_lip.y])
                
                eye_distance = np.linalg.norm(p1_eye - p2_eye)
                mouth_distance = np.linalg.norm(p1_lip - p2_lip)
                
                if eye_distance < EYE_THRESHOLD:
                    CLOSED_COUNTER += 1
                else:
                    CLOSED_COUNTER = 0
                
                if CLOSED_COUNTER >= DANGER_FRAMES:
                    print("Emergency conditions verified via Sleep Detector!")
                    trigger_emergency = True
                    break

                if mouth_distance > MOUTH_THRESHOLD:
                    YAWN_COUNTER += 1
                    display_status = "ALERT: YAWNING DETECTED!"
                    status_color = (0, 165, 255)
                else:
                    YAWN_COUNTER = 0
                    
                if YAWN_COUNTER >= YAWN_FRAMES:
                    print("Emergency conditions verified via Yawn Detector!")
                    trigger_emergency = True
                    break

        if pose_results.pose_landmarks and not trigger_emergency:
            nose = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            if nose.y > 0.7:
                print("Emergency conditions verified via Crash Posture!")
                trigger_emergency = True

        if trigger_emergency:
            print("\n[CRITICAL INITIALIZATION] Activating vehicular defense layers...")
            
            sound_thread = threading.Thread(target=play_local_alarm_in_background)
            sound_thread.daemon = True
            sound_thread.start()
            
            cap.release()
            cv2.destroyAllWindows()
            
            print("[LOCATION] Fetching dynamic vehicle telemetry...")
            try:
                geo_response = requests.get('https://ipapi.co/json/', timeout=3)
                geo_data = geo_response.json()
                live_city = geo_data.get('city', 'Kanpur Area')
                live_region = geo_data.get('region', 'Uttar Pradesh')
                live_lat = geo_data.get('latitude', '26.4499')
                live_lon = geo_data.get('longitude', '80.3319')
                print(f"[SUCCESS] Incident targeted near: {live_city} ({live_lat}, {live_lon})")
            except Exception as loc_err:
                live_city, live_region, live_lat, live_lon = "Kanpur", "Uttar Pradesh", "26.4499", "80.3319"
                print(f"[FALLBACK] Geolocation timed out. Loading defaults. Error: {loc_err}")

            print("[TELECOM] Accessing Twilio global routing switches...")
            try:
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                dynamic_twiml = f'''
                <Response>
                    <Say voice="polly.Amy" loop="2">
                        Critical Alert. Automated telemetry system has verified driver collapse near {live_city}, {live_region}. 
                        Current satellite coordinates are latitude {live_lat}, and longitude {live_lon}. 
                        Please dispatch emergency rescue response units immediately.
                    </Say>
                </Response>
                '''
                call = client.calls.create(twiml=dynamic_twiml, from_=TWILIO_PHONE_NUM, to=TARGET_PHONE_NUM)
                print(f"[SUCCESS] Cellular bridge deployed. Tracking SID: {call.sid}")
            except Exception as telecom_err:
                print(f"[COMMUNICATION FAILURE] Outbound telecom pipeline broken: {telecom_err}")

            print("[SYSTEM HOLD] Maintenance window locked. Siren active for driver recovery...")
            time.sleep(5)
            pygame.mixer.stop()
            print("[SYSTEM OFF] Emergency protocol cycle finished.")
            
            break

        cv2.putText(frame, f"Closed Frames: {CLOSED_COUNTER}/{DANGER_FRAMES}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if CLOSED_COUNTER < DANGER_FRAMES else (0, 0, 255), 2)
        cv2.putText(frame, display_status, (30, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        cv2.imshow("SafeDrive AI - Production HUD", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()
              
