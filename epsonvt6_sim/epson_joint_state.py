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


class JointStatePublisherNode(Node):
    def __init__(self):
        super().__init__('epson_joint_state')

        # Get the urdf file
        pkgPath = FindPackageShare(package='epsonvt6_sim').find('epsonvt6_sim')
        urdf_path=os.path.join(pkgPath, 'urdf/epsonvt6.urdf')
        urdf_desc = xacro.process_file(urdf_path)
        self.ik_chain = ikpy.chain.Chain.from_urdf_file(urdf_path, active_links_mask=[False, True, True, True, True, True, True])

        #set same paramter types as the epson_vt6 script
        self.declare_parameter("robot_position_topic", "robot_position")
        self.declare_parameter("robot_initial_pos", [0.0, 700.0, 300.0, 0.0, 0.0, 0.0]) # x y z pitch roll yaw

        # create joint state publisher for rviz2
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_joint_states) # Publish every 0.1 seconds

        robot_position_topic = (
            self.get_parameter("robot_position_topic")
            .get_parameter_value()
            .string_value
        )

        self.robot_position_sub = self.create_subscription(RobotPosition, robot_position_topic, self.subscribe_robot_position, 2)

        self.joint_names = ['base_swivel_joint', 'swivel_arm_joint', 'wrist_joint', 'hand_joint', 'finger_joint', 'tip_joint']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                
        # Set initial position
        self.initial_position = Pose()
        self.initial_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.next_pose = Pose()
        self.next_pose = self.initial_position


    def publish_joint_states(self):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = self.joint_names

        joint_state_msg.position = self.joint_positions
        self.joint_state_publisher.publish(joint_state_msg)
        self.get_logger().info(f'Publishing Joint States: {self.joint_positions}')
        self.get_logger().info(f'\ninital postion: {self.initial_position}')

    ## TODO: Find what publisher is posting the roboto position data (robot_position) but get system to work
    ## to see why nodes are not being published
    def subscribe_robot_position(self, msg):
        self.next_pose.position.x = msg.pose.position.x
        self.next_pose.position.y = msg.pose.position.y
        self.next_pose.position.z = msg.pose.position.z

        self.next_pose.orientation.x = msg.pose.orientation.x
        self.next_pose.orientation.y = msg.pose.orientation.y
        self.next_pose.orientation.z = msg.pose.orientation.z
        
        # the new joint angles
        new_pose = self.ik_chain.inverse_kinematics([(self.next_pose.position.x) (self.next_pose.position.y) (self.next_pose.position.z)],
                                           [(self.next_pose.orientation.x) (self.next_pose.orientation.y) (self.next_pose.orientation.z)])
        self.joint_positions[0]=new_pose[1]
        self.joint_positions[1]=new_pose[2]
        self.joint_positions[2]=new_pose[3]
        self.joint_positions[3]=new_pose[4]
        self.joint_positions[4]=new_pose[5]
        self.joint_positions[5]=new_pose[6]
        

def main(args=None):
    rclpy.init(args=args)
    node = JointStatePublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()