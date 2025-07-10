# Gunner Cook-Dumas
# 7/10/25

import os

from ament_index_python.packages import get_package_share_directory

from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():

    pkgPath = FindPackageShare(package='robot_arm_6axis').find('robot_arm_6axis')
    package_name='robot_arm_6axis'
    world=os.path.join(pkgPath, 'worlds/empty.sdf')
    robot_model=os.path.join(pkgPath, 'urdf/epsonvt6.urdf')

    # rsp = IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource([os.path.join(
    #                 get_package_share_directory(package_name),'launch','sim.launch.py'
    #             )]), launch_arguments={'use_sim_time': 'true'}.items()
    # )

    # Include the Gazebo launch file, provided by the ros_gz_sim package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
                    launch_arguments={'gz_args': ['-r -v 4', world], 'on_exit_shutdown': 'true'}.items()
             )

    # Run the spawner node from the ros_gz_sim package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-file', robot_model,
                                   '-entity', 'epsonvt6',
                                   '-z', '1'],
                        output='screen')



    # Launch them all!
    return LaunchDescription([
        gazebo,
        spawn_entity 
    ])