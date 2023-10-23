# CURPOS Read and read and write PR[1] Cartesian Coordinates

#   Command to start mqtt broker
#      /usr/local/sbin/mosquitto -c /Users/gary/Documents/code/robot/lab4/mosquitto.conf
#       129.101.98.196

import sys
# sys.path.append('./pycomm3/pycomm3')
import struct
import random
import time
from robot_controller import robot
import paho.mqtt.client as mqtt
import sys
import time
import json
import FANUCethernetipDriver

# MQTT server details
# BROKER_IP = "129.101.98.194"
BROKER_IP = "172.20.10.6"
BROKER_PORT = 1883

cart_data = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
}

flag_data = {
    "dj_waiting": False,
    "dj_has_die": False,
    "bill_waiting": False,
    "bill_has_die": False
}


def on_publish(client, userdata, mid):
    print("Message Published...")


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("flag_data")
    client.subscribe("cart_data")


def on_disconnect(client, userdata, rc, properties=None):
    print(f"Disconnected with result code {rc}")


def on_message(client, userdata, msg):
    if msg.topic == "cart_data":
        print("Message received")
        print("Received payload:", msg.payload.decode())
        received_data = json.loads(msg.payload.decode())
        # cart_data['x'] = received_data.get('x', cart_data['x'])
        # cart_data['y'] = received_data.get('y', cart_data['y'])
        # cart_data['z'] = received_data.get('z', cart_data['z'])

        cart_data.update(received_data)
        print("FROM ON MESSAGE Cartesian values after Random x:", cart_data["x"], "(", type(cart_data["x"]), ")",
              " y:", cart_data["y"], "(", type(cart_data["y"]), ")",
              " z:", cart_data["z"], "(", type(cart_data["z"]), ")")


    if msg.topic == "flag_data":
        received_data = json.loads(msg.payload.decode())
        flag_data['dj_waiting'] = received_data.get('dj_waiting', flag_data['dj_waiting'])
        flag_data['dj_has_die'] = received_data.get('dj_has_die', flag_data['dj_has_die'])
        flag_data['bill_waiting'] = received_data.get('bill_waiting', flag_data['bill_waiting'])
        flag_data['bill_has_die'] = received_data.get('bill_has_die', flag_data['bill_has_die'])


client = mqtt.Client()
client.on_publish = on_publish
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(BROKER_IP, BROKER_PORT)
client.loop_start()

# This is just for testing MQTT
# while (True):off
#
#     client.publish("ROBOT_B_BILL", message, qos=1)
#     time.sleep(2)
# client.loop_end()


handoff = [390.062, -491.382, 431.861, -179.717, 1.903, -90.965]  # cartesian


def main():
    """! Main program entry"""


    # Generate a random value between -50 and 50 for x and y, 100 for z
    cart_data['x'] = random.uniform(-50.0, 50.0)
    cart_data['y'] = random.uniform(-50.0, 50.0)
    cart_data['z'] = random.uniform(-90.0, 90.0)

    time.sleep(10)


    # Publish Random offset
    cart_message = json.dumps(cart_data)
    client.publish("cart_data", cart_message, qos=1)
    print("I JUST PUBLISHED CARTESIAN")


    time.sleep(10)


    time.sleep(15)

    print("ROBOT STARTED")

    client.loop_stop()
    exit()















    # Reset temp_handoff
    temp_handoff = handoff
    # Apply random
    temp_handoff[0] += cart_data['x']
    temp_handoff[1] += cart_data['y']
    temp_handoff[2] += cart_data['z']

    flag_data['bill_has_die'] = True
    flag_data['bill_waiting'] = True
    message = json.dumps(flag_data)
    client.publish("flag_data", message, qos=1)

    # Tell DJ I have the die and I'm waiting for him
    flag_data['dj_waiting'] = True
    flag_data['dj_has_die'] = True
    message = json.dumps(flag_data)
    client.publish("flag_data", message, qos=1)

    # Goto approach handoff, wait for BILL
    while (1):
        if flag_data["dj_waiting"] == True:
            print("Cartesian values x:", cart_data["x"], " y:", cart_data["y"], " z:", cart_data["z"])

            # copy handoff cartesian, apply new cart_data from DJ to it
            temp_handoff = handoff
            # check cart_datas
            temp_handoff[0] += cart_data["x"]
            temp_handoff[1] += cart_data["y"]
            temp_handoff[2] += cart_data["z"]

            print("ROBOT STARTED")
            break
        else:
            print("Waiting for DJ")
            print("DJ flag data waiting:", flag_data["dj_waiting"], " die:", flag_data["dj_has_die"])
            time.sleep(1)

    # Wait for grasp
    time.sleep(5)
    # Tell DJ I have the die and I'm waiting for him
    flag_data['bill_has_die'] = True
    flag_data['bill_waiting'] = True
    message = json.dumps(flag_data)
    client.publish("flag_data", message, qos=1)

    # Wait for dj to move
    time.sleep(5)

    # Wait for DJ to release die
    # Goto approach handoff, wait for DJ
    while (1):
        if (flag_data["dj_has_die"] == False):
            time.sleep(2)

            break
        else:
            print("Waiting for DJ to release")
            print("DJ flag data waiting:", flag_data["dj_waiting"], " die:", flag_data["dj_has_die"])
            time.sleep(.5)

    # Wait for DJ to grasp, release
    while (1):
        if (flag_data["dj_has_die"] == True):
            print("OPEN GRIPPER")
            break
        else:
            print("Waiting for DJ to grasp")
            print("DJ flag data waiting:", flag_data["dj_waiting"], " die:", flag_data["dj_has_die"])
            time.sleep(.5)


if __name__ == "__main__":
    main()
