import serial
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# UART Configuration
UART_PORT = '/dev/ttyACM2'    # Change to your port (COM3 for Windows)
BAUDRATE = 115200             # Match your device's baud rate
TIMEOUT = 1                   # Read timeout in seconds

# MQTT Configuration
MQTT_BROKER = "192.168.127.1" # Your broker IP
MQTT_PORT = 1883              # Default MQTT port
MQTT_TOPIC = "input"      # Topic to publish to

def setup_uart():
    """Initialize UART connection"""
    try:
        ser = serial.Serial(
            port=UART_PORT,
            baudrate=BAUDRATE,
            timeout=TIMEOUT
        )
        print(f"Connected to UART port {UART_PORT} at {BAUDRATE} baud")
        return ser
    except Exception as e:
        print(f"UART connection failed: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}")
    else:
        print(f"MQTT connection failed with code {rc}")

def main():
    # Initialize UART
    ser = setup_uart()
    if not ser:
        return

    # Initialize MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    
    try:
        # Connect to MQTT broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()

        while True:
            if ser.in_waiting > 0:
                # Read UART data
                raw_data = ser.readline().decode('utf-8').strip()
                
                if raw_data:  # Only process if we got data
                    print(f"UART Received: {raw_data}")
                    
                    # Create JSON payload with timestamp
                    payload = json.dumps({
                        "data": raw_data,
                        "timestamp": datetime.now().isoformat(),
                        "source": "UART"
                    })
                    
                    # Publish to MQTT
                    mqtt_client.publish(MQTT_TOPIC, payload, qos=1)
                    print(f"Published to MQTT: {payload}")

            time.sleep(0.1)  # Small delay to prevent CPU overload

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ser.close()
        mqtt_client.disconnect()
        print("Cleanup complete")

if __name__ == "__main__":
    main()