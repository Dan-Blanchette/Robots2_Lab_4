import os
import random
from robot_controller import robot
import paho.mqtt.client as mqtt
import json
import random
import time

# MQTT server details
BROKER_IP = "129.101.98.194"
BROKER_PORT = 1883

drive_path = '129.101.98.215' # DJ

cart_data = {
    "x": 1.23,
    "y": 4.56,
    "z": 7.89
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
        received_data = json.loads(msg.payload.decode())
        cart_data['x'] = received_data.get('x', cart_data['x'])  # if first value DNE, grab second value
        cart_data['y'] = received_data.get('y', cart_data['y'])
        cart_data['z'] = received_data.get('z', cart_data['z'])
        
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



def main():

# main program 

   crx10_dj = robot(drive_path)
   # joint moves
   home = [3.6055996417999268,-1.5429623126983643,3.3683128356933594,-0.713886559009552,-4.529087066650391,-2.439002752304077]
   def_loc_grab = [13.7835693359375,23.362775802612305,-52.080665588378906,-1.1174789667129517,-39.579307556152344,16.08687400817871] 
   # cartesian moves
   # move flag variable
   move_flag = crx10_dj.is_moving()

   crx10_dj.shunk_gripper('open')
   crx10_dj.write_joint_pose(home)
   crx10_dj.start_robot()
   # print(f'{moving}')


   crx10_dj.write_joint_pose(def_loc_grab)
   crx10_dj.start_robot()
   # print(f'DJ is moving:{move_flag}')
   # print(f'{moving}')
   crx10_dj.shunk_gripper('close')
   flag_data["dj_has_die"] = True
   message = json.dumps(flag_data)
   client.publish("flag_data", message, qos=1)
   

   # crx10_dj.write_joint_pose(handoff)
   crx10_dj.write_cartesian_position(364.646, 690.701, 476.777, -90.995, -31.562, -1.412)
   move_flag = crx10_dj.is_moving()
   crx10_dj.start_robot()
   if (move_flag == 0):
      flag_data["dj_waiting"] = True
      print("I'm waiting..............................")
   message = json.dumps(flag_data)
   client.publish("flag_data", message, qos=1)
   print("end of prog")
   client.loop_end()
   

   # while(1):
   #    client.publish("ROBOT_A_DJ", message, qos=1)
   #    time.sleep(2)
   #    client.loop_end()




if __name__=="__main__":
    main()  

