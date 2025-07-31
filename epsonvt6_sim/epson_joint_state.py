import ikpy.chain
import ikpy.inverse_kinematics
import rclpy
from launch_ros.substitutions import FindPackageShare
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose
from std_msgs.msg import Int8
from robot_arm_interfaces.msg import RobotPosition, PrintingPoint
import xacro
import os
import math
import pandas as pd
import numpy as np


class JointStatePublisherNode(Node):
    def __init__(self):
        super().__init__('epson_joint_state')

        # Get the urdf file
        pkgPath = FindPackageShare(package='epsonvt6_sim').find('epsonvt6_sim')
        urdf_path=os.path.join(pkgPath, 'urdf/epsonvt6.urdf')
        urdf_desc = xacro.process_file(urdf_path)
        self.ik_chain = ikpy.chain.Chain.from_urdf_file(urdf_path, active_links_mask=[False, True, True, True, True, True, True])

        # create joint state publisher for rviz2
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_joint_states) # Publish every 0.1 seconds


        self.declare_parameter("robot_position_topic", "robot_position")
        self.declare_parameter("robot_initial_pos", [0.0, 700.0, 250.0, 0.0, 0.0, 0.0])
        robot_position_topic = (
            self.get_parameter("robot_position_topic")
            .get_parameter_value()
            .string_value
        )
        self.initial_position = (
            self.get_parameter("robot_initial_pos")
            .get_parameter_value()
            .double_array_value
        )
        self.robot_tool = 3
        self.robot_position = RobotPosition()
        self.robot_position.tool_system.tool = self.robot_tool
        self.robot_position.tool_system.pose.position.x = self.initial_position[0]
        self.robot_position.tool_system.pose.position.y = self.initial_position[1]
        self.robot_position.tool_system.pose.position.z = self.initial_position[2]
        self.robot_position.tool_system.pose.orientation.x = self.initial_position[3]
        self.robot_position.tool_system.pose.orientation.y = self.initial_position[4]
        self.robot_position.tool_system.pose.orientation.z = self.initial_position[5]

        self.robot_position.camera_system.tool = self.robot_tool
        self.robot_position.camera_system.pose.position.x = self.initial_position[0]
        self.robot_position.camera_system.pose.position.y = self.initial_position[1]
        self.robot_position.camera_system.pose.position.z = self.initial_position[2]
        self.robot_position.camera_system.pose.orientation.x = self.initial_position[3]
        self.robot_position.camera_system.pose.orientation.y = self.initial_position[4]
        self.robot_position.camera_system.pose.orientation.z = self.initial_position[5]


        self.robot_position_sub = self.create_subscription(
            RobotPosition, robot_position_topic, self.robot_position_callback, 2
        )


        # Setup joints
        self.joint_names = ['base_swivel_joint', 'swivel_arm_joint', 'wrist_joint', 'hand_joint', 'finger_joint', 'tip_joint']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.initial_position = Pose()
        self.initial_position.position.x = self.joint_positions[0]
        self.initial_position.position.y = self.joint_positions[1]
        self.initial_position.position.z = self.joint_positions[2]

        self.initial_position.orientation.x = self.joint_positions[3]
        self.initial_position.orientation.y = self.joint_positions[4]
        self.initial_position.orientation.z = self.joint_positions[5]

        self.next_pose = Pose()
        self.next_pose.position = self.initial_position.position
        self.next_pose.orientation = self.initial_position.orientation
                




    def publish_joint_states(self):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = self.joint_names



        joint_state_msg.position = self.joint_positions
        self.joint_state_publisher.publish(joint_state_msg)
        self.get_logger().info(f'Publishing Joint States: {self.joint_positions}')


    ## TODO: Find what publisher is posting the roboto position data (robot_position) but get system to work
    ## to see why nodes are not being published
    def robot_position_callback(self, msg):
        self.robot_position.tool_system.tool = msg.tool_system.tool
        self.robot_position.tool_system.pose.position.x = (
            msg.tool_system.pose.position.x
        )
        self.robot_position.tool_system.pose.position.y = (
            msg.tool_system.pose.position.y
        )
        self.robot_position.tool_system.pose.position.z = (
            msg.tool_system.pose.position.z
        )
        self.robot_position.tool_system.pose.orientation.x = (
            msg.tool_system.pose.orientation.x
        )
        self.robot_position.tool_system.pose.orientation.y = (
            msg.tool_system.pose.orientation.y
        )
        self.robot_position.tool_system.pose.orientation.z = (
            msg.tool_system.pose.orientation.z
        )
      

        # the new joint angles
        posX=self.robot_position.tool_system.pose.position.x
        posY=self.robot_position.tool_system.pose.position.y
        posZ=self.robot_position.tool_system.pose.position.z
        orX=self.robot_position.tool_system.pose.orientation.x
        orY=self.robot_position.tool_system.pose.orientation.y
        orZ=self.robot_position.tool_system.pose.orientation.z
        position=np.array([posX, posY, posZ])
        orientation=np.array([orX, orY, orZ])

        self.get_logger().info(f'position: {position}')
        self.get_logger().info(f'orientation: {orientation}')

        # Error here  
        self.next_pose = self.ik_chain.inverse_kinematics(position, orientation)
        # And error here
        self.joint_positions[0]=self.next_pose[1]
        self.joint_positions[1]=self.next_pose[2]
        self.joint_positions[2]=self.next_pose[3]
        self.joint_positions[3]=self.next_pose[4]
        self.joint_positions[4]=self.next_pose[5]
        self.joint_positions[5]=self.next_pose[6]
        # self.get_logger().info(f'subscribing States: {self.joint_positions}')

        
    
        

def main(args=None):
    rclpy.init(args=args)
    node = JointStatePublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()