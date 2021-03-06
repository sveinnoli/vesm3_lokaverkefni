import json
from json.decoder import JSONDecodeError
from mfrc522 import SimpleMFRC522
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import os
rand_str = os.urandom(10).hex()

reader = SimpleMFRC522()
id = 'dabdabdab6969'
device_ids = ["1", "2"]

client_telemetry_topic = id + '/telemetry'
client_reload_topic = id + '/reload'
client_device_reset = id + '/reset'
client_name = id

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')

mqtt_client.loop_start()

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        try:
            if payload.get("command") == "reset":
                mqtt_client.publish(client_device_reset, "reset")
                print("reseting")
        except AttributeError:
            pass
    except JSONDecodeError:
        payload = message.payload.decode()
        
    print("Message received:", payload)
    

# Subscribe to all topics
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.subscribe(client_reload_topic)
    
mqtt_client.on_message = handle_telemetry

while True:
    try:
        id, text = reader.read()
        if text.strip() in device_ids:
            #Sends a reload command to esp32 with id of the scanned card
            print(f"sending reload command to device {text.strip()}")
            mqtt_client.publish(client_reload_topic, text.strip())
            #Change from time.sleep to time.time to avoid missing out on mqtt messages
            time.sleep(1)
    except Exception:
        GPIO.cleanup()
        raise

