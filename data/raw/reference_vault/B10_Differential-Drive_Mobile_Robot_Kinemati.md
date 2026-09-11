# B10. Differential-Drive Mobile Robot Kinematics

**Source:** GMU / Robotics Tutorials

In a differential-drive robot, the two wheels are independently driven. The motion patterns are:

- **Straight Line:** Both wheels turn at the same speed (`v_r = v_l`).
- **Turn in an Arc:** One wheel turns faster than the other, causing the robot to follow a circular path.
- **Turn in Place:** The wheels rotate in opposite directions (`v_r = -v_l`), resulting in a zero-radius turn.

The robot's pose update in discrete time is given by:

```
dx = v * cos(theta + w * dt / 2) * dt
dy = v * sin(theta + w * dt / 2) * dt
dtheta = w * dt
```

These equations assume constant velocities during the time step. In practice, the robot's controller sends velocity commands, and the kinematics model is used in both simulation and real-world odometry to track the robot's position.
