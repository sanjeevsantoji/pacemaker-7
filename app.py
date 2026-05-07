from flask import Flask, render_template, jsonify, request
from digital_twin import DigitalTwin
from ai_engine import AIEngine
from blockchain_auth import pulse_chain
import time
import threading

app = Flask(__name__)

# Initialize components
twin = DigitalTwin()
ai = AIEngine()

# Shared state for real-time data
data_buffer = []
max_buffer_size = 100

def simulation_loop():
    """Background thread to run the simulation."""
    global data_buffer
    while True:
        # Update twin state
        status = twin.update()
        
        # Simulate AI prediction
        # Features: variance (derived from timing), drain rate, noise level
        # In a real system, we'd calculate these over a window
        variance = 0.5 if twin.attack_type == 'dos' else 0.01
        drain = 0.05 if twin.attack_type == 'battery_drain' else 0.001
        noise = 0.3 if twin.failure_active else 0.02
        
        prediction = ai.predict([variance, drain, noise])
        
        # Get latest ECG point
        ecg_val = twin.generate_ecg_point(time.time())
        
        # Package data
        data_point = {
            "time": time.time(),
            "ecg": ecg_val,
            "battery": status['battery'],
            "status": status['status'],
            "ai_prediction": prediction['prediction'],
            "ai_confidence": prediction['confidence']
        }
        
        data_buffer.append(data_point)
        if len(data_buffer) > max_buffer_size:
            data_buffer.pop(0)
            
        time.sleep(0.05) # 20Hz update for UI

# Start simulation thread
sim_thread = threading.Thread(target=simulation_loop, daemon=True)
sim_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(data_buffer)

@app.route('/api/command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    auth_token = data.get('token')
    
    # Simulate Blockchain Authorization
    if auth_token == "DOCTOR_SECURE_TOKEN":
        if cmd == "RESET":
            twin.reset_system()
            pulse_chain.add_block("Authorized System Reset by Doctor")
        elif cmd == "FIX_LEAD":
            twin.failure_active = False
            twin.lead_integrity = 1.0
            pulse_chain.add_block("Authorized Lead Repair Procedure")
        return jsonify({"status": "success", "message": f"Command {cmd} executed and logged to blockchain."})
    else:
        return jsonify({"status": "error", "message": "Unauthorized command! Access denied."}, 403)

@app.route('/api/attack', methods=['POST'])
def trigger_attack():
    data = request.json
    type = data.get('type')
    if type == 'reset':
        twin.stop_attack()
    else:
        twin.trigger_attack(type)
    return jsonify({"status": "attack_updated"})

@app.route('/api/failure', methods=['POST'])
def trigger_failure():
    twin.trigger_failure()
    return jsonify({"status": "failure_triggered"})

@app.route('/api/blockchain')
def get_blockchain():
    return jsonify(pulse_chain.get_chain_data())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
