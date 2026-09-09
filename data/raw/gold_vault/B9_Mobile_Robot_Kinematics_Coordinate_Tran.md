# B9. Mobile Robot Kinematics: Coordinate Transformations

**Source:** ROS Control / Research Literature

Mobile robot kinematics describes the relationship between the wheel velocities and the robot's motion in the plane, under simplifying assumptions (e.g., no slipping). The first step is to define coordinate frames:

- **World Frame:** A fixed reference frame.
- **Robot Frame:** Attached to the robot's body, often at the center of the wheelbase.
- **Wheel Frames:** Attached to each wheel.

Transformation matrices convert points from one frame to another, using rotation and translation. For a differential-drive robot, the robot's linear and angular velocities are determined from the left and right wheel speeds:

```
v = (v_r + v_l) / 2
w = (v_r - v_l) / d
```

where `v_r` and `v_l` are the right and left wheel linear velocities, and `d` is the distance between the wheels.

These equations allow the robot's pose (x, y, theta) to be integrated over time. However, odometry accumulates drift, so sensor data (e.g., from IMU or cameras) is fused to improve localization accuracy.
