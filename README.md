# Sketch Follower

A 4-DOF robot arm Gazebo simulation created to learn CAD modeling, inverse kinematics, and ROS Control.

The arm was designed using Fusion 360 then assembled through URDF and Xacro. The main Python scripts include:

- **cursor_publisher.py**: Tkinter GUI that records and publishes the cursor position when pressed and displays the current end effector position.
- **ros_interface.py**: Subscribes to the cursor publisher and the simulation joint states, and publishes the joint velocities to the simulation.
- **kinematics.py**: Describes the robot kinematics using numpy and solves the inverse kinematics problem.
- **controller.py**: Controls the Gazebo simulation by reading the desired pose, obtaining the desired joint velocities, then publishing them.

<br/>
<img src=./robot_description/3d_demo.gif width=100%>

## Demo (ROS 1)

For a demo, simply run docker compose inside the project:

```
docker compose up
```