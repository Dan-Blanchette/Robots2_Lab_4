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

def_cart_data = {
    "x": 364.646,
    "y": 690.701,
    "z": 376.777,
    "w":-90.995,
    "p":-31.562,
 	 "r":-1.412
}

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

# rpbot API class instance
crx10_dj = robot(drive_path)

def on_publish(client, userdata, mid):
    print("Message Published...")
    
# def randCart():
#    cart_offset["x_os"] = random.uniform(-50.0, 50.0)
#    print(f'x_off: {cart_offset["x_os"]}')
#    cart_offset["y_os"] = random.uniform(-50.0, 50.0)
#    print(f'y_off: {cart_offset["y_os"]}')
#    cart_offset["z_os"] = random.uniform(-90.0, 90.0)
#    print(f'z_off: {cart_offset["z_os"]}')
#    message2 = json.dumps(cart_offset)
#    client.publish("cart_offset", message2, qos=1)

#    crx10_dj.write_cartesian_position(def_cart_data["x"],def_cart_data["y"],def_cart_data["z"],
#                                      def_cart_data["w"],def_cart_data["p"],def_cart_data["r"])
#    crx10_dj.start_robot()

   

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

   home = [3.6055996417999268,-1.5429623126983643,3.3683128356933594,-0.713886559009552,-4.529087066650391,-2.439002752304077]
   def_loc_grab = [17.481, 25.178, -51.212, 0.697,-38.636, 13.036] 
   # cartesian moves
   # move flag variable
   move_flag = crx10_dj.is_moving()
   
   # Start Robot Routine
   # Open the Gripper
   crx10_dj.shunk_gripper('open')
   # Go to the home position
   crx10_dj.write_joint_pose(home)
   crx10_dj.start_robot()


   crx10_dj.write_joint_pose(def_loc_grab)
   crx10_dj.start_robot()
   # print(f'DJ is moving:{move_flag}')
   # print(f'{moving}')
   crx10_dj.shunk_gripper('close')
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
                print("Retracting.........")
                crx10_dj.write_cartesian_position(364.646, 190.701, 376.777, -90.995, -31.562, -1.412)
                crx10_dj.start_robot()
                time.sleep(0.5)
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

            crx10_dj.shunk_gripper('close')
            flag_data["dj_has_die"] = True
            #update gripper flag is closed
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
            
            crx10_dj.shunk_gripper('open')
            crx10_dj.write_joint_pose(home)
            crx10_dj.start_robot()
            break

if __name__=="__main__":
    main()  

client.loop_stop()
