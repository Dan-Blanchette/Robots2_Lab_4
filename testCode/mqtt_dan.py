import paho.mqtt.client as mqtt
import json
import random
import time

# MQTT server details
BROKER_IP = "129.101.98.194"
BROKER_PORT = 1883

cart_data = {
    "x": 1.23,
    "y": 4.56,
    "z": 7.89
}   



print(f'x_position: {cart_data["x"]}')

DJ_move_flag = {
    "robot_moving": False 
}


def on_publish(client, userdata, mid):
    print("Message Published...")
    

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("ROBOT_B_BILL")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    x = cart_data["x"]
    y = cart_data["y"]
    z = cart_data["z"]
    robot_move = DJ_move_flag["robot_moving"]
    print(f'x:{x}, y:{y}, z:{z}, robot_moving:{robot_move}')
    # print(f"Topic: {msg.topic}\nMessage: {msg.payload.decode()}")

cart_data["x"] = 100.0
print(f'new x: {cart_data["x"]}')
client = mqtt.Client()
client.on_publish = on_publish
client.on_message = on_message
client.on_connect = on_connect
client.connect(BROKER_IP, BROKER_PORT)
client.loop_start()

message = json.dumps(cart_data)

while(1):
   client.publish("ROBOT_A_DJ", message, qos=1)
   time.sleep(2)
client.loop_end()