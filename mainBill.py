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
BROKER_IP = "129.101.98.194"
BROKER_PORT = 1883

cart_data = {
    "x": 0,
    "y": 0,
    "z": 0,
}

flag_data = {
    "dj_waiting": False,
    "dj_moving": False,
    "dj_has_die": False,
    "bill_waiting": False,
    "bill_moving": False,
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
        received_data = json.loads(msg.payload.decode())
        cart_data['x'] = received_data.get('x', cart_data['x'])  # if first value DNE, grab second value
        cart_data['y'] = received_data.get('y', cart_data['y'])
        cart_data['z'] = received_data.get('z', cart_data['z'])
    if msg.topic == "flag_data":
        received_data = json.loads(msg.payload.decode())
        flag_data['dj_waiting'] = received_data.get('dj_waiting', flag_data['dj_waiting'])
        flag_data['dj_moving'] = received_data.get('dj_moving', flag_data['dj_moving'])
        flag_data['dj_has_die'] = received_data.get('dj_has_die', flag_data['dj_has_die'])
        flag_data['bill_waiting'] = received_data.get('bill_waiting', flag_data['bill_waiting'])
        flag_data['bill_moving'] = received_data.get('bill_moving', flag_data['bill_moving'])
        flag_data['bill_has_die'] = received_data.get('bill_has_die', flag_data['bill_has_die'])




    # x = data['x']
    # y = data['y']
    # z = data['z']
    # robot_moving = data['robot_moving']
    # print(f"x: {x}, y: {y}, z: {z}, robotMoving: {robot_moving}")


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

drive_path = '129.101.98.214'  # CRX10 BILL

pose1 = [0.0, -2.409282387816347e-06, 0.009522347711026669, -0.024758676066994667, -0.018449142575263977,
         0.0247572660446167]  # Home position
pose2 = [-9.638092994689941, -9.305192947387695, -11.088014602661133, -1.9604847431182861, -78.9268798828125,
         -80.95472717285156]  # Approach Handoff
pose3 = [-38.522300720214844, 6.566395282745361, -11.665398597717285, -1.7110475301742554, -79.27543640136719,
         -52.11516189575195]  # Handoff

handoff = [384.062, -491.382, 431.861, -179.717, 1.903, -90.965]  # cartesian


def main():
    """! Main program entry"""
    print("Cartesian values x:",  cart_data["x"], " y:", cart_data["y"], " z:", cart_data["z"])

    # Create new robot object
    crx10 = robot(drive_path)

    # Set robot speed
    crx10.set_speed(200)

    # Open Gripper
    crx10.onRobot_gripper_close(150, 20)


    print("Cartesian values x:",  cart_data["x"], " y:", cart_data["y"], " z:", cart_data["z"])

    # Move arm lift die off belt
    crx10.set_pose(pose1)
    crx10.start_robot()
    # while(crx10.is_moving()):
    #     message = {
    #         "bill_waiting": False,
    #         "bill_moving": False,
    #         "bill_has_die": False
    #     }
    #     client.publish("flag_data", json.dumps(message), qos=1)

    temp_handoff = handoff
    # check cart_datas
    temp_handoff[0] += cart_data["x"]
    temp_handoff[1] += cart_data["y"]
    temp_handoff[2] += cart_data["z"]

    # Move arm to handoff approach
    crx10.set_pose(pose2)
    crx10.start_robot()


    # Goto approach handoff, wait for DJ
    while(1):
        if(flag_data["dj_waiting"] == True):
            crx10.send_coords(temp_handoff[0], temp_handoff[1], temp_handoff[2], temp_handoff[3], temp_handoff[4], temp_handoff[5])
            crx10.start_robot()
            break
        else:
            print("Waiting for DJ")
            print("DJ flag data waiting:", flag_data["dj_waiting"], " moving:", flag_data["dj_moving"], " die:", flag_data["dj_has_die"])
            time.sleep(1)


    # #grasp die
    crx10.onRobot_gripper_close(80,20)

    #Tell DJ I have the die and I'm waiting for him
    flag_data['bill_has_die'] = True
    flag_data['bill_waiting'] = True
    message = json.dumps(flag_data)
    client.publish("flag_data", message, qos=1)

    # Wait for DJ to release die
    # Goto approach handoff, wait for DJ
    while(1):
        if(flag_data["dj_has_die"] == False):
            crx10.set_pose(pose1)
            crx10.start_robot()
            break
        else:
            print("Waiting for DJ to release")
            print("DJ flag data waiting:", flag_data["dj_waiting"], " moving:", flag_data["dj_moving"], " die:", flag_data["dj_has_die"])
            time.sleep(.5)


if __name__ == "__main__":
    main()