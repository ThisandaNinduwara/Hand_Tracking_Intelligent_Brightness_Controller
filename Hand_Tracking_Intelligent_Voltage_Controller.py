import cv2
import mediapipe as mp
import math
import time
import serial
import serial.tools.list_ports

# MediaPipe hands model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Landmark indices
THUMB_TIP = 4
INDEX_TIP = 8
PALM_BASE = 0  # Wrist
INDEX_MCP = 5  # Base of index finger


# Serial connection to Arduino Nano
def connect_to_arduino():
    """Find and connect to Arduino Nano automatically"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Common Arduino identifiers
        if 'arduino' in port.description.lower() or 'ch340' in port.description.lower() or 'usb serial' in port.description.lower():
            try:
                ser = serial.Serial(port.device, 115200, timeout=1)
                time.sleep(2)  # Wait for connection to establish
                print(f"Connected to Arduino on {port.device}")
                return ser
            except:
                continue
    print("Arduino not found. Please check connection.")
    return None


def map_value(value, in_min, in_max, out_min, out_max):
    """Maps distance to brightness (0-255)"""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def send_brightness(ser, value):
    """Send brightness value to Arduino Nano over Serial"""
    try:
        ser.write(f"{value}\n".encode())  # Send value with newline
        return True
    except:
        return False


def main():
    # Connect to Arduino
    arduino = connect_to_arduino()
    if arduino is None:
        return

    cap = cv2.VideoCapture(1)
    last_brightness = -1
    update_interval = 0.1  # seconds
    last_update = time.time()

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Flip and convert image
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        height, width, _ = image.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw all hand landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get pixel coordinates for key points
                thumb = hand_landmarks.landmark[THUMB_TIP]
                thumb_px = (int(thumb.x * width), int(thumb.y * height))

                index = hand_landmarks.landmark[INDEX_TIP]
                index_px = (int(index.x * width), int(index.y * height))

                palm_base = hand_landmarks.landmark[PALM_BASE]
                palm_base_px = (int(palm_base.x * width), int(palm_base.y * height))

                index_mcp = hand_landmarks.landmark[INDEX_MCP]
                index_mcp_px = (int(index_mcp.x * width), int(index_mcp.y * height))

                # Draw line between finger tips (green)
                cv2.line(image, thumb_px, index_px, (0, 255, 0), 3)

                # Draw circles at finger tips
                cv2.circle(image, thumb_px, 10, (255, 0, 0), -1)  # Blue thumb
                cv2.circle(image, index_px, 10, (0, 0, 255), -1)  # Red index

                # Calculate actual pixel distance between tips
                pixel_distance = math.sqrt((thumb_px[0] - index_px[0]) ** 2 +
                                           (thumb_px[1] - index_px[1]) ** 2)

                # Calculate PALM WIDTH (reference for normalization)
                palm_width = math.sqrt((palm_base_px[0] - index_mcp_px[0]) ** 2 +
                                       (palm_base_px[1] - index_mcp_px[1]) ** 2)

                # Calculate normalized distance
                normalized_distance = pixel_distance / palm_width

                # Map to LED brightness
                MIN_DISTANCE = 0.22
                MAX_DISTANCE = 1.4
                brightness = map_value(normalized_distance, MIN_DISTANCE, MAX_DISTANCE, 0, 255)
                brightness = max(0, min(255, brightness))

                # Only send updates periodically
                if (brightness != last_brightness and
                        (time.time() - last_update) > update_interval):
                    if send_brightness(arduino, brightness):
                        last_brightness = brightness
                        last_update = time.time()

                # Display distance text at midpoint
                midpoint = ((thumb_px[0] + index_px[0]) // 2, (thumb_px[1] + index_px[1]) // 2)
                cv2.putText(image, f"{int(pixel_distance)}px", midpoint,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # Display debug info
                cv2.putText(image, f"Norm. Distance: {normalized_distance:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(image, f"Brightness: {brightness}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Hand Tracking - Serial Control', image)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC key to exit
            break

    # Cleanup
    if arduino:
        arduino.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()