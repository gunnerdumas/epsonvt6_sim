from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import xacro

def generate_launch_description():
    ld=LaunchDescription()
    pkgPath = FindPackageShare(package='robot_arm_6axis').find('robot_arm_6axis')
    urdf_path=os.path.join(pkgPath, 'urdf/epsonvt6.urdf.xacro')
    rviz_config_path=os.path.join(pkgPath, 'rviz/config.rviz')
    robot_description_config = xacro.process_file(urdf_path)
    

    
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    gui=LaunchConfiguration('gui')
    urdf_model=LaunchConfiguration('urdf_model')
    use_robot_state_pub=LaunchConfiguration('use_robot_state_pub')
    rviz_config_file=LaunchConfiguration('rviz_config_file')
    use_rviz=LaunchConfiguration('use_rviz')

    declare_urdf_path=DeclareLaunchArgument(name='urdf_model', default_value=urdf_path)
    
    declare_use_robot_state_pub=DeclareLaunchArgument(name='use_robot_state_pub', default_value='True')
    
    declare_use_joint_state_pub=DeclareLaunchArgument(name='gui', default_value='True')
    
    declare_use_rviz=DeclareLaunchArgument(name='use_rviz', default_value='True')
    
    delcare_rviz_config_file=DeclareLaunchArgument(name='rviz_config_file', default_value=rviz_config_path)
    
    declare_use_sim_time=DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation clock if true')
    
# parameters=[{'robot_description': launch_ros.descriptions.ParameterValue( launch.substitutions.Command(['xacro ',os.path.join(turtlebot2_description_package,'robots/kobuki_conveyor.urdf.xacro')]), value_type=str)  }]
# ,'robot_description': Command(['xacro ', urdf_model])
    params = {'use_sim_time': use_sim_time, 'robot_description': robot_description_config.toxml()} 
    # params = [{'use_sim_time': use_sim_time,'robot_description': ParameterValue(Command(['xacro ',urdf_model]), value_type=str)}]

    
    rjpg=Node(condition=IfCondition(gui),
             package='joint_state_publisher_gui',
             executable='joint_state_publisher_gui',
             name='joint_state_publisher_gui')
    
    rjp=Node(condition=UnlessCondition(gui),
             package='joint_state_publisher',
             executable='joint_state_publisher',
             name='joint_state_publisher')
    
    rsp=Node(condition=IfCondition(use_robot_state_pub),
             package='robot_state_publisher',
             executable='robot_state_publisher',
             parameters=[params],
             arguments=[urdf_model],
             output='screen')
    
    rviz=Node(condition=IfCondition(use_rviz),
              package='rviz2',
              executable='rviz2',
              name='rviz2',
              output='screen',
              arguments=["-d", rviz_config_file]
              )

    ld.add_action(declare_urdf_path)
    ld.add_action(declare_use_robot_state_pub)
    ld.add_action(declare_use_joint_state_pub)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_use_sim_time)
    ld.add_action(delcare_rviz_config_file)

    ld.add_action(rsp)
    ld.add_action(rjpg)
    ld.add_action(rjp)
    ld.add_action(rviz)

    return ld