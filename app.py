import time
import threading
import serial
import numpy as np
from flask import Flask, jsonify, request
import config

# =====================================================
# MUSIC MAP
# =====================================================
NOTE_TO_ANGLE = {
    "C": 30, "D": 50, "E": 70,
    "F": 90, "G": 110, "A": 130, "B": 150
}

NOTE_TO_FREQ = {
    "C": 261, "D": 293, "E": 329,
    "F": 349, "G": 392, "A": 440, "B": 493
}

COMMAND_INTERVAL = 1.0 / config.COMMAND_RATE_HZ

# =====================================================
# STATE
# =====================================================
state = {
    "mode": "IDLE",
    "locked": False,
    "playing": False
}

# =====================================================
# ARDUINO CLASS
# =====================================================
class Arduino:
    def __init__(self, cfg):
        self.name = cfg["name"]
        self.port = cfg["port"]
        self.enabled = cfg.get("enabled", True)
        self.ser = None
        self.last_send = 0
        if self.enabled:
            self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(
                self.port,
                config.SERIAL_BAUD,
                timeout=0.1
            )
            time.sleep(2)
            print(f"✅ {self.name} connected ({self.port})")
        except Exception as e:
            print(f"❌ {self.name} error:", e)
            self.enabled = False

    def send(self, cmd):
        if not self.enabled:
            return
        now = time.time()
        if now - self.last_send < COMMAND_INTERVAL:
            return
        self.last_send = now
        try:
            self.ser.write((cmd + "\n").encode())
        except:
            self.enabled = False

    def angle(self, a):
        a = int(np.clip(a, config.SERVO_MIN, config.SERVO_MAX))
        self.send(f"ANGLE:{a}")

    def led(self, v):
        if config.ENABLE_LED:
            self.send(f"LED:{int(np.clip(v,0,255))}")

    def buzzer(self, f):
        if config.ENABLE_BUZZER:
            self.send(f"BUZZ:{int(f)}")

    def stop(self):
        self.send("STOP")

# =====================================================
# INIT
# =====================================================
arduinos = [
    Arduino(a) for a in config.ARDUINOS if a.get("enabled", True)
]

app = Flask(__name__)

# =====================================================
# SAFETY
# =====================================================
def stop_all():
    state["playing"] = False
    state["mode"] = "IDLE"
    for a in arduinos:
        a.stop()

# =====================================================
# MUSIC MODE
# =====================================================
def play_notes(notes):
    if state["locked"]:
        return

    state["locked"] = True
    state["mode"] = "MUSIC"
    state["playing"] = True

    for n in notes:
        if not state["playing"]:
            break
        if n not in NOTE_TO_ANGLE:
            continue

        angle = NOTE_TO_ANGLE[n]
        freq = NOTE_TO_FREQ[n]

        if len(arduinos) > 0:
            arduinos[0].angle(angle)
            arduinos[0].buzzer(freq)
            arduinos[0].led(180)

        if len(arduinos) > 1:
            arduinos[1].angle(180 - angle)
            arduinos[1].buzzer(freq * 2)
            arduinos[1].led(120)

        time.sleep(config.NOTE_DELAY)

    stop_all()
    state["locked"] = False

# =====================================================
# API
# =====================================================
@app.route("/api/status")
def api_status():
    return jsonify(state)

@app.route("/api/play", methods=["POST"])
def api_play():
    if state["locked"]:
        return jsonify(success=False, error="busy")

    data = request.json
    notes = data.get("notes", [])

    threading.Thread(
        target=play_notes,
        args=(notes,),
        daemon=True
    ).start()

    return jsonify(success=True)

@app.route("/api/stop")
def api_stop():
    stop_all()
    return jsonify(success=True)

# =====================================================
# START
# =====================================================
if __name__ == "__main__":
    print("🚀 Servo Music Controller")
    print("🔧 Edit config.py to configure ports")
    app.run(host="0.0.0.0", port=5000)

