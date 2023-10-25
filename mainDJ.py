# Advanced Robotics 2(CS 553) 
# Author: Dan Blanchette
# Date: 10/23/23
# Lab 4: Dice Passing Robots
# Ver: 2.0

# Description: This program will use MQTT to communicate cartesian offsets and robot "states"
# to my partner Gary Bank's program. We use Boolean flags to indicate feedback to the other robot
# for grabbing the dice and when each robot has arrived at is random walk position. The dice is then passed
# to his robot which will do its own random walk handoff and send me the new coordinate offset via the MQTT
# broker. # This program utilizes the University of Idaho Fanuc Python API driver, Paho MQTT, and Mosquitto
# acting as a local broker on Gary's laptop. 

import random
from robot_controller import robot
import paho.mqtt.client as mqtt
import json
import random
import time

# MQTT server details
BROKER_IP = "129.101.98.194"
BROKER_PORT = 1883
# DJ IP ADDRESS
drive_path = '129.101.98.215' # DJ

# Dictionary for Robot Hand off Start Location Pose
def_cart_data = {
    "x": 364.646,
    "y": 690.701,
    "z": 376.777,
    "w":-90.995,
    "p":-31.562,
 	 "r":-1.412
}

# Dictionary that will be used to update offset information for cartesian random walk
cart_data = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
}

flag_data = {
    "dj_waiting": False,
    "dj_has_die": False,
    "bill_waiting": False,
    "bill_has_die": False
}

# robot API class instance
crx10_dj = robot(drive_path)

def on_publish(client, userdata, mid):
    print(f'Message Published: {userdata}')
    
   
# Connect to broker verification
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("flag_data")
    client.subscribe("cart_data")

# Disconnect from Broker
def on_disconnect(client, userdata, rc, properties=None):
    print(f"Disconnected with result code {rc}")

# Topics to Subscribe to
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

# MQTT Client Setup
client = mqtt.Client()
client.on_publish = on_publish
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(BROKER_IP, BROKER_PORT)
client.loop_start()



def main():

# main program  
   # Local vars that hold the home and payload approach joint poses
   home = [3.6055996417999268,-1.5429623126983643,3.3683128356933594,-0.713886559009552,-4.529087066650391,-2.439002752304077]
   def_loc_grab = [17.481, 25.178, -51.212, 0.697,-38.636, 13.036] 
   
   # Start Robot Routine
   # Open the Gripper
   crx10_dj.shunk_gripper('open')
   # Go to the home position
   crx10_dj.write_joint_pose(home)
   crx10_dj.start_robot()

   # Move to pick up dice position
   crx10_dj.write_joint_pose(def_loc_grab)
   crx10_dj.start_robot()

   # DEBUG TESTING VAR CHECK
   # print(f'DJ is moving:{move_flag}')
   # print(f'{moving}')

   # Close the gripper (non-blocking)
   crx10_dj.shunk_gripper('close')
   # Update the has die flag and publish to topic for Gary to subscribe to
   flag_data["dj_has_die"] = True
   message = json.dumps(flag_data)
   # publish grab flag as true and send to Gary's lappy
   client.publish("flag_data", message, qos=1)
   print(f'I just sent Gary This Value:{message}')
   
# Applying random offset to dictionary
   cart_data["x"] = random.uniform(-50.0, 50.0)
   print(f'x_off: {cart_data["x"]}')
   cart_data["y"] = random.uniform(-50.0, 50.0)
   print(f'y_off: {cart_data["y"]}')
   cart_data["z"] = random.uniform(-90.0, 90.0)
   print(f'z_off: {cart_data["z"]}')
   # Sends offset data to Gary
   message2 = json.dumps(cart_data)
   client.publish("cart_data", message2, qos=2)
   
   # Add the random offset to the default point of reference for the hand off
   crx10_dj.write_cartesian_position(def_cart_data["x"] + cart_data["x"], def_cart_data["y"] + cart_data["y"], def_cart_data["z"] + cart_data["z"],
                                     def_cart_data["w"], def_cart_data["p"], def_cart_data["r"])
   # move to that position
   crx10_dj.start_robot()

   # Send Gary's computer the waiting to hand off flag set as True
   flag_data["dj_waiting"] = True
   message1 = json.dumps(flag_data)
   print("DJ is waiting to hand off")
   client.publish("flag_data", message1, qos=1)
   
   # Poll Bill to see if robot has dice
   while(1):
   # Bill has the dice
        if(flag_data["bill_has_die"] == True):
            # DJ Opens gripper
            crx10_dj.shunk_gripper("open")
            # Reset DJ has dice flag to False
            flag_data['dj_has_die'] = False
            # Send Flag update to Gary's PC
            message2 = json.dumps(flag_data)
            client.publish("flag_data", message2, qos=1)

            #if DJ has dice is false, ok to -500mm y-axis retract
            if(flag_data["dj_has_die"]== False):
                print("Retracting.........")
                crx10_dj.write_cartesian_position(364.646, 190.701, 376.777, -90.995, -31.562, -1.412)
                crx10_dj.start_robot()
                time.sleep(0.2)
                break
        else:
            # debug statements
            print("waiting for Bill to grab")
            print(f'Bill Status:{flag_data["bill_has_die"]}')
            time.sleep(3)

   # Poll to see if Bill has die and Bill is waiting

   while(1):

        if(flag_data["bill_has_die"] == True and flag_data["bill_waiting"] == True):
            # move y+ 10mm to grab dice
            crx10_dj.write_cartesian_position(def_cart_data["x"] + cart_data["x"], def_cart_data["y"] + cart_data["y"] + 10, def_cart_data["z"] + cart_data["z"])
            crx10_dj.start_robot()
            # close the gripper
            crx10_dj.shunk_gripper('close')
            # set flags 
            flag_data["dj_has_die"] = True
            flag_data["dj_waiting"] = False
            # update gripper flag is closed and DJ has the dice
            # and isn't waiting any more.
            message3 = json.dumps(flag_data)
            client.publish("flag_data", message3, qos=1)
            break


        else:
            print("Waiting for Bill to let go")
            print(f'Bill Dice Status:{flag_data["bill_has_die"]}')
            print(f'Bill Waiting Status:{flag_data["bill_waiting"]}')
            time.sleep(3)
    
   # wait for false flag from bill's gripper   
   while(1):
       print(f'Bill has die == {flag_data["bill_has_die"]}')
       if (flag_data["bill_has_die"] == False):
            # ok to move to default pick up/drop off position
            crx10_dj.write_joint_pose(def_loc_grab)
            crx10_dj.start_robot()
            
            # DICE CAN BE STICKY WHEN PLACING
            # Wait 1.5 seconds after opening then go home
            crx10_dj.shunk_gripper('open')
            time.sleep(1.5)
            crx10_dj.write_joint_pose(home)
            crx10_dj.start_robot()
            break


# REPETION 2

   # Go to the home position
   crx10_dj.write_joint_pose(home)
   crx10_dj.start_robot()

   # Get the dice from the default
   crx10_dj.write_joint_pose(def_loc_grab)
   crx10_dj.start_robot()

   # print statements for debugging flag data
   # print(f'DJ is moving:{move_flag}')

   # close gripper
   crx10_dj.shunk_gripper('close')
   # set DJ has die flag to True
   flag_data["dj_has_die"] = True
   # Convert to JSON string and Publish Flag Data to Broker
   message = json.dumps(flag_data)
   # publish grab flag as true and send to Gary's lappy
   client.publish("flag_data", message, qos=1)
   # Runtime Debugging Print Statement
   print(f'I just sent Gary This Value:{message}')
   
# Applying random offset to dictionary
   cart_data["x"] = random.uniform(-50.0, 50.0)
   print(f'x_off: {cart_data["x"]}')
   cart_data["y"] = random.uniform(-50.0, 50.0)
   print(f'y_off: {cart_data["y"]}')
   cart_data["z"] = random.uniform(-90.0, 90.0)
   print(f'z_off: {cart_data["z"]}')
   # Sends offset data to Gary
   message2 = json.dumps(cart_data)
   client.publish("cart_data", message2, qos=2)
   
   # Add received offset from Bill and add to default reference values
   crx10_dj.write_cartesian_position(def_cart_data["x"] + cart_data["x"], def_cart_data["y"] + cart_data["y"], def_cart_data["z"] + cart_data["z"],
                                     def_cart_data["w"], def_cart_data["p"], def_cart_data["r"])
   crx10_dj.start_robot()


   flag_data["dj_waiting"] = True
   message1 = json.dumps(flag_data)
   print("DJ is waiting to hand off")
   client.publish("flag_data", message1, qos=1)
   
   # Poll Bill to see if robot has dice
   while(1):
   # Bill has the dice
        if(flag_data["bill_has_die"] == True):
            # DJ Opens gripper
            crx10_dj.shunk_gripper("open")
            # Reset DJ has dice flag to False
            flag_data['dj_has_die'] = False
            # Send Flag update to Gary's PC
            message2 = json.dumps(flag_data)
            client.publish("flag_data", message2, qos=1)

            #if DJ has dice is false, ok to -500mm y-axis retract
            if(flag_data["dj_has_die"]== False):
                # From current position, retract 500mm on y-axis
                crx10_dj.write_cartesian_position(def_cart_data["x"], def_cart_data["y"] - 500, def_cart_data["z"],
                                                  def_cart_data["w"], def_cart_data["p"], def_cart_data["r"])
                crx10_dj.start_robot()
                time.sleep(0.5)
                print("Done Going Home Now.........")
                crx10_dj.write_joint_pose(home)
                crx10_dj.start_robot()
                break
        else:
            # debug statements
            print("waiting for Bill to take dice")
            print(f'Bill Status:{flag_data["bill_has_die"]}')
            time.sleep(3)


if __name__=="__main__":
    main()  

client.loop_stop()
