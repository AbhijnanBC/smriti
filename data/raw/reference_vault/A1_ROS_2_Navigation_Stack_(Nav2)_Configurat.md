# A1. ROS 2 Navigation Stack (Nav2) Configuration Guide

**Source:** Foxglove Blog / ROS 2 Documentation

The Nav2 stack is the official navigation solution for ROS 2. It is designed to be modular, configurable, and suitable for a wide range of mobile robotic platforms. The entire system is launched via the `navigation_launch.py` file provided in the `nav2_bringup` package. This launch file orchestrates the lifecycle of multiple nodes, each of which loads its configuration parameters from a central YAML file, typically named `nav2_params.yaml`.

All Nav2 nodes are implemented as LifecycleNodes, which means they follow a managed lifecycle: they start in an unconfigured state, transition to configuring, then to active, and finally to a shutdown state. A dedicated lifecycle manager node ensures that all dependent nodes are brought up in the correct order and that the system transitions gracefully.

The core components of Nav2 include:

- **Planner Server:** Responsible for computing a global path from the robot's current position to a goal point, using a global costmap that represents static obstacles and known map data.
- **Controller Server:** Follows the global plan by generating velocity commands for the robot. It uses a local costmap that incorporates real-time sensor data to avoid dynamic obstacles.
- **Behavior Server:** Executes recovery behaviors such as spinning, backing up, or waiting when the robot becomes stuck.
- **BT Navigator:** Orchestrates the overall navigation task using a BehaviorTree that can combine planning, control, and recovery actions in a flexible manner.

The separation of global and local costmaps allows the system to balance long-term route planning with short-term obstacle avoidance, making Nav2 a robust choice for both indoor and outdoor robotics applications.
