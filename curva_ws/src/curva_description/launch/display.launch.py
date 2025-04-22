import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
import launch
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ros_gz_bridge.actions import RosGzBridge
from ros_gz_sim.actions import GzServer


def generate_launch_description():
    pkg_share = FindPackageShare(package='curva_description').find('curva_description')
    default_model_path = os.path.join(pkg_share, 'sdf', 'curva_description.sdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    bridge_config_path = os.path.join(pkg_share, 'config', 'bridge_config.yaml')
    world_path = os.path.join(pkg_share, 'world', 'my_world.sdf')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    gz_spawn_model_launch_source = os.path.join(ros_gz_sim_share, "launch", "gz_spawn_model.launch.py")

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    gz_server = GzServer(
    world_sdf_file=world_path,
    container_name='ros_gz_container',
    create_own_container='True',
    use_composition='True',
    )
    ros_gz_bridge = RosGzBridge(
    bridge_name='ros_gz_bridge',
    config_file=bridge_config_path,
    container_name='ros_gz_container',
    create_own_container='False',
    use_composition='True',
    )
    spawn_entity = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
    launch_arguments={
        'world': 'my_world',
        'topic': '/robot_description',
        'entity_name': 'curva',
    }.items(),
    )   
    robot_localization_node = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_node',
    output='screen',
    parameters=[os.path.join(pkg_share, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    return LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='True',
                                            description='Flag to enable use_sim_time'),
        DeclareLaunchArgument(name='use_sim_time', default_value='True', description='Flag to enable use_sim_time'),
        DeclareLaunchArgument(name='model', default_value=default_model_path, description='Absolute path to robot model file'),
        DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path, description='Absolute path to rviz config file'),
        ExecuteProcess(cmd=['gz', 'sim', '-g'], output='screen'),
        robot_state_publisher_node,
        spawn_entity,
        robot_localization_node,
        rviz_node,
        gz_server,
        ros_gz_bridge,
    ])