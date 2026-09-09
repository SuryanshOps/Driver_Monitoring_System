<div align="center">

# 🚗 SafeDrive AI: Integrated Driver Monitoring & Telematics

<!-- Replace 'assets/demo.gif' with the path to your actual GIF once recorded -->
<img src="assets/demo.gif" alt="SafeDrive AI Demo" width="700" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

<br>

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange.svg)](https://google.github.io/mediapipe/)
[![Twilio](https://img.shields.io/badge/Twilio-API-red.svg)](https://www.twilio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*An edge-ready computer vision safety system designed to prevent accidents through real-time fatigue detection and automated emergency response.*

</div>

---

## 📖 Table of Contents
1. [Overview & System Features](#-overview--system-features)
2. [Video Demonstration](#-video-demonstration)
3. [System Architecture & Tech Stack](#-system-architecture--tech-stack)
4. [In-Depth Mechanism & Mathematics](#-in-depth-mechanism--mathematics)
5. [Emergency Action Protocol](#-emergency-action-protocol)
6. [Prerequisites & Installation](#-prerequisites--installation)
7. [Usage Guide](#-usage-guide)
8. [Future Roadmap](#-future-roadmap)

---

## 🌌 Overview & System Features

SafeDrive AI is a complete, beginner-friendly telematics and computer vision system designed to enhance profile value for engineering applications. By combining multi-modal structural tracking with defensive cloud routing pipelines, it provides high-impact real-world usability.

* **Multi-Modal Fatigue Profiling:** Monitors both eye separation (PERCLOS tracking) and wide yawns (Mouth Opening Ratio) continuously via facial landmarks.
* **Asynchronous Alarm Pipeline:** Spins off a local cabin warning siren using Pygame onto an independent background thread, preventing frame lockup.
* **Network Geolocation Mapping:** Automatically queries global internet routers to pull live city names and coordinates within 3 seconds, injecting coordinates seamlessly into emergency payloads.
* **Comprehensive Linear Continuity:** Pins the local warning, device isolation loop, network ping, and Twilio voice API dispatches under a single controlled logical umbrella block.

---

## 🎥 Video Demonstration

<!-- Replace YOUR_YOUTUBE_VIDEO_ID with the actual ID of your YouTube video. -->
[![Watch the Demo](https://img.youtube.com/vi/YOUR_YOUTUBE_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUR_YOUTUBE_VIDEO_ID)

> **Click the image above to watch the live simulation of the fatigue detection and emergency SOS routing!**

---

## 🏗️ System Architecture & Tech Stack

| Technology | Purpose in Project |
| :--- | :--- |
| **Python** | The core programming language powering the multi-threaded logic and state machines. |
| **OpenCV (cv2)** | Handles video feed ingestion, RGB color conversion, and drawing the dynamic Heads-Up Display (HUD). |
| **MediaPipe** | Deploys two simultaneous neural networks: `FaceMesh` (for high-precision eye/lip tracking) and `Pose` (for overall body/head alignment). |
| **NumPy** | Performs rapid vector mathematics to calculate L2 Euclidean distances between facial landmarks. |
| **Twilio API** | Routes programmatic voice calls over global cellular networks during critical failures. |
| **Pygame & Threading** | Handles asynchronous audio playback (`alarm.wav`) to prevent thread-locking during emergency events. |

---

## 🧠 In-Depth Mechanism & Mathematics

The accuracy of SafeDrive AI relies on geometric calculations mapped over continuous time-buffers. Here is how the detection algorithms work under the hood.

### 1. Ocular Analysis (Sleep Detection)
The MediaPipe `FaceMesh` network is activated with `refine_landmarks=True` to map extra high-precision points around the eyes. We isolate:
* **Node 159:** Top Eyelid
* **Node 145:** Bottom Eyelid

We calculate the exact distance between these points using the **L2 Euclidean Norm**:
`Distance = √((x2 - x1)² + (y2 - y1)²)`

* **Threshold Logic:** If the normalized distance drops below `0.015`, the eye is classified as "closed".
* **Time-Buffering:** A single blink should not trigger the alarm. The system increments a `CLOSED_COUNTER` only during consecutive closed frames. If the counter reaches `90 frames` (approximately 3 seconds at 30 FPS), the Sleep Emergency Protocol is triggered. Opening the eyes instantly resets the counter to zero.

### 2. Fatigue Analysis (Yawn Detection)
Using a similar methodology, we track the inner lips:
* **Node 13:** Top Inner Lip
* **Node 14:** Bottom Inner Lip

If the Euclidean distance between these points exceeds `0.040`, a yawn is registered. Sustaining this distance for `45 consecutive frames` triggers a critical fatigue alert.

### 3. Slouch & Crash Posture Detection
MediaPipe's `Pose` network tracks the driver's overall skeletal structure. We isolate the **Nose Landmark**. 
* In the normalized MediaPipe coordinate space, `Y=0` is the top of the frame and `Y=1.0` is the bottom.
* If the Nose drops below `Y = 0.75`, it mathematically indicates the driver's head has slumped severely downward toward the steering wheel.
* A buffer of `60 frames` (~2 seconds) is required to verify a crash posture, filtering out quick glances at the dashboard.

---

## 🚨 Emergency Action Protocol

When any of the three danger thresholds are breached, the script locks into an emergency state machine executing the following sequence:

1. **Multithreaded Siren:** Spawns a background daemon thread utilizing `pygame.mixer` to continuously loop an audio file (`alarm.wav`) to jolt the driver awake.
2. **Resource Reallocation:** Shuts down the webcam feed and OpenCV windows to free up CPU cycles for network communications.
3. **Dynamic Geolocation:** Queries `https://ipapi.co/json/` via the `requests` library to fetch the vehicle's live latitude, longitude, and region. A 3-second timeout prevents the system from hanging in dead zones.
4. **Cellular Dispatch:** Constructs a dynamic TwiML (Twilio Markup Language) script containing the telemetry data, utilizing the Amazon Polly "Amy" voice. 
5. **Outbound Call:** Bypasses local hardware limitations by routing the SOS call through Twilio's cloud infrastructure directly to a target phone number.

---

## ⚙️ Prerequisites & Installation

### Prerequisites
* A functional webcam positioned on the dashboard or steering column.
* Python 3.8+ installed on your local machine or edge device.
* A Twilio Developer account (for cellular SOS routing).
* An audio file named `alarm.wav` in the root directory.

### Installation Steps

**1. Clone the Source Code**
```bash
git clone https://github.com/SuryanshOps/Driver_Minitoring_System.git
cd Driver_Monitoring_System
```

**2. Virtual Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install opencv-python mediapipe numpy twilio requests pygame
```

**4. Configure Telematics (Twilio)**
Open `safedrive_ai_production.py` and replace the placeholder credentials with your Twilio dashboard keys:
```python
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN  = "your_auth_token_here"
TWILIO_PHONE_NUM   = "+1234567890"
TARGET_PHONE_NUM   = "+91XXXXXXXXXX"
```

---

## 🚀 Usage Guide

1. Place your `alarm.wav` sound file in the same folder as the script.
2. Launch the monitoring system:
   ```bash
   python safedrive_ai_production.py
   ```
3. A HUD window will appear displaying live tracking metrics for your eyes and posture. 
4. **To Test Sleep Detection:** Close your eyes for 3 seconds.
5. **To Test Crash Posture:** Duck your head below the bottom 25% of the camera frame for 2 seconds.
6. **To Exit:** Press the `q` key on your keyboard to safely break the monitoring loop and release hardware resources.

---

## 🗺️ Future Roadmap

* [ ] **Infrared Camera Support:** Integrate IR spectrum analysis for flawless nighttime and low-light tracking inside the cabin.
* [ ] **GPS Hardware Integration:** Replace IP-based geolocation with serial communication to a dedicated GPS module for extreme precision in dead zones.
* [ ] **Gaze Tracking:** Monitor pupil direction to detect dangerous levels of distraction (e.g., staring at a phone instead of the road).

---

<div align="center">
<b>Developed with 💡 by Suryansh Kushwaha</b><br>
<i>Advancing vehicular safety through edge computing and artificial intelligence.</i>
</div>
