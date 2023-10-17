import os
import random
from robot_controller import robot

drive_path = '129.101.98.215' # DJ
# drive_path = '129.101.98.198' # Digital DJ



def main():

# main program 

   crx10_dj = robot(drive_path)
   # joint moves
   home = [3.6055996417999268,-1.5429623126983643,3.3683128356933594,-0.713886559009552,-4.529087066650391,-2.439002752304077]
   grab = [13.7835693359375,23.362775802612305,-52.080665588378906,-1.1174789667129517,-39.579307556152344,16.08687400817871] 
   # cartesian moves
   

   crx10_dj.shunk_gripper('open')
   crx10_dj.write_joint_pose(home)
   crx10_dj.start_robot()

   crx10_dj.write_joint_pose(grab)
   crx10_dj.start_robot()
   crx10_dj.shunk_gripper('close')

   # crx10_dj.write_joint_pose(handoff1)
   # crx10_dj.send_coords(364.646, 690.701, 376.777, -90.995, -31.562, -1.412)
   crx10_dj.send_coords(364.646, 690.701, 476.777, -90.995, -31.562, -1.412)

   crx10_dj.start_robot()
   



if __name__=="__main__":
    main()  