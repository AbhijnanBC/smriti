# A2. Gazebo Harmonic Physics Simulation Environment

**Source:** Gazebo Official Documentation

Gazebo Harmonic is a powerful robot simulation environment that provides high-fidelity physics, realistic sensor rendering, and a rich set of plugins. It is the successor to the classic Gazebo and is built with modern C++ and ROS 2 integration in mind. The simulation engine supports multiple physics solvers, including ODE and Bullet, enabling accurate simulation of rigid bodies, joints, and contacts.

Key features of Gazebo Harmonic include:

- **Component Inspector:** A GUI plugin that displays detailed information about any selected model, including its links, joints, and sensors. It allows users to inspect and modify parameters in real time.
- **Entity Tree:** Provides a hierarchical view of all entities in the simulation world, making it easy to navigate complex environments.
- **Force/Torque Application:** Users can interactively apply forces and torques to objects by dragging them with the mouse, or by specifying exact values through a dedicated interface.
- **Physics Step Control:** A step-by-step simulation mode enables users to advance the simulation one physics iteration at a time, which is invaluable for debugging and deterministic testing.

Sphere and water-tight triangle meshes are fully supported for collision detection and physically plausible inertial calculations. Gazebo Harmonic also publishes standard ROS 2 messages, such as PointCloud2, to facilitate integration with perception and navigation stacks, making it a cornerstone of modern robotic development pipelines.
