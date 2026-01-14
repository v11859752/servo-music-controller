# =====================================================
# USER CONFIGURATION FILE
# =====================================================
# ⚠️ Этот файл редактируется пользователем
# ⚠️ app.py НЕ НУЖНО менять
# =====================================================

# ---------------- BUILD ----------------
BUILD_MODE = "RELEASE"   # RELEASE / DEV

# ---------------- SERIAL ----------------
SERIAL_BAUD = 115200

ARDUINOS = [
    {
        "name": "left_servo",
        "port": "COM5",        # Windows: COM5 | Linux: /dev/ttyUSB0
        "enabled": True
    },
    {
        "name": "right_servo",
        "port": "COM7",
        "enabled": True
    }
]

# ---------------- COMMAND RATE ----------------
COMMAND_RATE_HZ = 20   # не больше 30

# ---------------- MUSIC ----------------
NOTE_DELAY = 0.15      # задержка между нотами

# ---------------- SERVO ----------------
SERVO_MIN = 0
SERVO_MAX = 180
SERVO_CENTER = 90

# ---------------- FEATURES ----------------
ENABLE_BUZZER = True
ENABLE_LED = True
