import paho.mqtt.client as mqtt
import socket
import os
import time

# MQTT server details
BROKER_IP = "129.101.98.194"
BROKER_PORT = 1883

def on_publish(client, userdata, mid):
    print("Message Published...")
    

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("#")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}\nMessage: {msg.payload.decode()}")

client = mqtt.Client()
client.on_publish = on_publish
client.on_message = on_message
client.on_connect = on_connect
client.connect(BROKER_IP, BROKER_PORT)
client.loop_start()

while(1):
   client.publish("ROBOT_A_DJ", "Hi I'm DJ", qos=1)
   time.sleep(2)
client.loop_end()