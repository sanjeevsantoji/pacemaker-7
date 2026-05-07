import numpy as np
import time
import random

class DigitalTwin:
    def __init__(self):
        # Heart state
        self.heart_rate = 70  # BPM
        self.sampling_rate = 100  # Hz
        self.time_step = 1.0 / self.sampling_rate
        
        # Pacemaker parameters
        self.target_bpm = 60
        self.escape_interval = 60.0 / self.target_bpm  # seconds
        self.refractory_period = 0.25  # seconds
        
        # Internal states
        self.last_beat_time = time.time()
        self.last_pacer_fire = 0
        self.battery_level = 100.0
        self.lead_integrity = 1.0  # 1.0 is perfect, 0 is fractured
        
        # Simulation flags
        self.attack_active = False
        self.attack_type = None  # 'dos', 'battery_drain'
        self.failure_active = False
        
    def generate_ecg_point(self, t):
        """Simulates a single ECG data point based on current state."""
        # Base ECG wave (synthetic)
        # P-wave, QRS-complex, T-wave
        # This is a highly simplified model for visualization
        
        phase = (t % (60.0 / self.heart_rate)) / (60.0 / self.heart_rate)
        
        val = 0
        # P-wave
        if 0.1 <= phase <= 0.2:
            val += 0.1 * np.exp(-((phase - 0.15)**2) / 0.001)
        # QRS-complex
        if 0.35 <= phase <= 0.45:
            val += 1.0 * np.exp(-((phase - 0.4)**2) / 0.0001)
            val -= 0.2 * np.exp(-((phase - 0.38)**2) / 0.0001)
            val -= 0.2 * np.exp(-((phase - 0.42)**2) / 0.0001)
        # T-wave
        if 0.6 <= phase <= 0.8:
            val += 0.2 * np.exp(-((phase - 0.7)**2) / 0.005)
            
        # Add noise
        val += np.random.normal(0, 0.02)
        
        # Apply Lead Failure (Signal attenuation/noise)
        if self.failure_active:
            val *= self.lead_integrity
            val += np.random.normal(0, 0.3) # Heavy noise for fracture
            
        return val

    def update(self):
        """Updates the pacemaker state machine."""
        current_time = time.time()
        since_last_beat = current_time - self.last_beat_time
        
        # AI/Monitoring data point
        status = "NORMAL"
        
        # 1. Sensing Logic
        # (In a real system, this would detect the QRS complex)
        
        # 2. Pacing Logic
        if since_last_beat > self.escape_interval:
            # Pacer fires!
            self.last_pacer_fire = current_time
            self.last_beat_time = current_time
            self.battery_level -= 0.001 # Normal consumption
            status = "PACING"
            
        # 3. Attack Simulation
        if self.attack_active:
            if self.attack_type == 'battery_drain':
                self.battery_level -= 0.05 # Rapid drain
                status = "ATTACK: BATTERY_DRAIN"
            elif self.attack_type == 'dos':
                # Force rapid pacing
                self.escape_interval = 0.3 # 200 BPM - dangerous!
                status = "ATTACK: DoS"
        else:
            self.escape_interval = 60.0 / self.target_bpm
            
        return {
            "timestamp": current_time,
            "battery": max(0, self.battery_level),
            "lead_integrity": self.lead_integrity,
            "status": status,
            "heart_rate": self.heart_rate
        }

    def trigger_attack(self, type):
        self.attack_active = True
        self.attack_type = type

    def stop_attack(self):
        self.attack_active = False
        self.attack_type = None

    def trigger_failure(self):
        self.failure_active = True
        self.lead_integrity = 0.2

    def reset_system(self):
        self.attack_active = False
        self.failure_active = False
        self.lead_integrity = 1.0
        self.battery_level = 100.0
