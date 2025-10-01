# Hand Tracking Intelligent Brightness Controller  

An intelligent brightness controller that uses **hand tracking and Arduino Nano** for touch-free control. Computer vision (OpenCV + Mediapipe) detects hand gestures, which are mapped to brightness levels. These values are sent to the Arduino Nano via serial communication, and the Nano controls LED/display brightness using PWM.  

---

## ✨ Features  
- Real-time **hand tracking with Mediapipe + OpenCV**  
- **Gesture-based brightness control** (finger distance → brightness)  
- **Arduino Nano integration** via serial communication  
- **PWM output** for smooth LED/display dimming  
- Easy to set up and run  

---

## 🔧 Tech Stack  
- **Python 3.x**  
  - OpenCV  
  - Mediapipe  
  - PySerial  
- **Arduino Nano**  
  - Arduino IDE  
  - PWM pin for LED control  

---

## 🚀 Getting Started  

### 1. Install Python dependencies  
```bash
pip install opencv-python mediapipe pyserial
