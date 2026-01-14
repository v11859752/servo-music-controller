#include <Servo.h>

/*
  ============================================
  Servo Music Controller — RELEASE Firmware
  --------------------------------------------
  Commands over Serial (115200):

  ANGLE:<0-180>
  LED:<0-255>
  BUZZ:<frequency>
  STOP
  ============================================
*/

// ================== PIN CONFIG ==================
const uint8_t SERVO_PIN  = 9;
const uint8_t LED_PIN    = 3;
const uint8_t BUZZER_PIN = 6;

// ================== SERVO CONFIG =================
const uint8_t SERVO_MIN = 0;
const uint8_t SERVO_MAX = 180;
const uint8_t SERVO_CENTER = 90;

// максимальная скорость (градусов за шаг)
const uint8_t SERVO_STEP = 2;
// интервал обновления (мс)
const uint16_t SERVO_INTERVAL = 15;

// ================== GLOBALS ======================
Servo servo;

int currentAngle = SERVO_CENTER;
int targetAngle  = SERVO_CENTER;

unsigned long lastServoUpdate = 0;
bool buzzerActive = false;

// ================== SETUP ========================
void setup() {
  Serial.begin(115200);

  servo.attach(SERVO_PIN);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  servo.write(SERVO_CENTER);
  analogWrite(LED_PIN, 0);
  noTone(BUZZER_PIN);

  Serial.println("READY");
}

// ================== SERVO UPDATE =================
void updateServo() {
  unsigned long now = millis();
  if (now - lastServoUpdate < SERVO_INTERVAL) return;
  lastServoUpdate = now;

  if (currentAngle < targetAngle) {
    currentAngle += SERVO_STEP;
    if (currentAngle > targetAngle) currentAngle = targetAngle;
  } 
  else if (currentAngle > targetAngle) {
    currentAngle -= SERVO_STEP;
    if (currentAngle < targetAngle) currentAngle = targetAngle;
  }

  servo.write(currentAngle);
}

// ================== COMMAND HANDLER ===============
void handleCommand(String cmd) {
  cmd.trim();

  // -------- ANGLE --------
  if (cmd.startsWith("ANGLE:")) {
    int a = cmd.substring(6).toInt();
    a = constrain(a, SERVO_MIN, SERVO_MAX);
    targetAngle = a;
    return;
  }

  // -------- LED ----------
  if (cmd.startsWith("LED:")) {
    int v = cmd.substring(4).toInt();
    analogWrite(LED_PIN, constrain(v, 0, 255));
    return;
  }

  // -------- BUZZER -------
  if (cmd.startsWith("BUZZ:")) {
    int f = cmd.substring(5).toInt();
    if (f <= 0) {
      noTone(BUZZER_PIN);
      buzzerActive = false;
    } else {
      tone(BUZZER_PIN, f);
      buzzerActive = true;
    }
    return;
  }

  // -------- STOP ---------
  if (cmd == "STOP") {
    targetAngle = SERVO_CENTER;
    analogWrite(LED_PIN, 0);
    noTone(BUZZER_PIN);
    buzzerActive = false;
    return;
  }
}

// ================== LOOP =========================
void loop() {
  updateServo();

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }
}
