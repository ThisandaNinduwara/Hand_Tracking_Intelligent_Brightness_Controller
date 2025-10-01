#define LED_PIN 6
int targetBrightness = 0;
int currentBrightness = 0;
float smoothFactor = 0.1;  // Adjust for smoothness (0.01-0.3)

void setup() {
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);
  Serial.begin(115200);
  while (!Serial);
  Serial.println("SMOOTH_LED_READY");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    int newTarget = input.toInt();
    
    if (newTarget >= 0 && newTarget <= 255) {
      targetBrightness = newTarget;
      Serial.print("TARGET_SET:");
      Serial.println(targetBrightness);
    }
  }
  
  // Smooth transition towards target
  if (currentBrightness != targetBrightness) {
    // Exponential smoothing
    currentBrightness += (targetBrightness - currentBrightness) * smoothFactor;
    
    // Ensure we reach exact target
    if (abs(targetBrightness - currentBrightness) < 1) {
      currentBrightness = targetBrightness;
    }
    
    analogWrite(LED_PIN, (int)currentBrightness);
  }
  
  delay(10);  // Small delay for stability
}