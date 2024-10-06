import numpy as np
from typing import List

import rclpy
from rclpy import node

from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose, Pose2D

from sketch_follower.model.kinematics import Kinematics


class ROSInterface:
    def __init__(self):
        rclpy.init()
        interface_node = node.Node("controller")

        interface_node.declare_parameter("control_mode", "")
        control_mode = interface_node.get_parameter("control_mode").value

        interface_node.get_logger().info(
            "Python controller waiting for Gazebo to start..."
        )
        # dummy_client = interface_node.create_client(
        #     SetPhysicsProperties, "/gazebo/set_physics_properties"
        # )
        interface_node.get_logger().info("Python controller starting...")

        self.kin = Kinematics()

        self.q = np.zeros(4)
        self.dq = np.zeros(4)
        self.q_reset = [0, -0.5, 2, -1.5]

        self.desired_position = None

        interface_node.create_subscription(
            JointState, "/sketch_follower/joint_states", self.joint_states_cb, 10
        )

        interface_node.create_subscription(
            Pose2D, "/sketch_follower/cursor_position", self.cursor_cb, 10
        )

        self.cursor_feedback = interface_node.create_publisher(
            Pose2D, "/sketch_follower/eef_position", 10
        )

        self.joint_publishers: List[rclpy.publisher.Publisher] = []
        self.r = interface_node.create_rate(10)

        for i in range(4):
            self.joint_publishers.append(
                interface_node.create_publisher(
                    Float64,
                    f"/sketch_follower/joint_{i}_{control_mode}_controller/command",
                    10,
                )
            )

    def joint_states_cb(self, data: JointState):
        self.q[1] = data.position[0]
        self.q[2] = data.position[1]
        self.q[0] = data.position[2]
        self.q[3] = data.position[3]

        self.q = self.q % (2 * np.pi)
        self.q = np.where(self.q > np.pi, self.q - 2 * np.pi, self.q)

        p = self.kin.p(self.q)[0:3, 3]
        self.cursor_feedback.publish(Pose2D(x=p[0], y=p[1]))

        if len(data.velocity) != 0:
            self.dq[1] = data.velocity[0]
            self.dq[2] = data.velocity[1]
            self.dq[0] = data.velocity[2]
            self.dq[3] = data.velocity[3]

    def cursor_cb(self, data: Pose2D):
        if self.desired_position is None:
            self.desired_position = np.array([data.x, data.y])
        else:
            self.desired_position[0] = data.x
            self.desired_position[1] = data.y