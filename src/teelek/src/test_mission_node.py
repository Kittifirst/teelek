#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from std_msgs.msg import Bool

class MissionNode(Node):
    def __init__(self):
        super().__init__("mission_node")
        
        # Publisher สำหรับสั่งให้หุ่นเดินไปยังพิกัดเป้าหมาย (Relative)
        self.target_pub = self.create_publisher(Pose2D, "/teelek/move_to_xy", 10)
        
        # Publisher สำหรับเซ็ตตำแหน่งปัจจุบันของหุ่น (Absolute/Initial)
        self.robot_pose_pub = self.create_publisher(Pose2D, "/teelek/robot_pose", 10)
        
        self.create_subscription(Bool, "/teelek/move_done", self.done_callback, 10)
        
        # หน่วงเวลา 2 วินาทีเพื่อให้ Node อื่นๆ พร้อมใช้งาน
        self.timer = self.create_timer(2.0, self.send_full_mission)

    def send_full_mission(self):
        # --- ขั้นตอนที่ 1: เซ็ตตำแหน่งปัจจุบันของหุ่น (Robot Pose) ---
        # สมมติว่าตอนนี้หุ่นวางอยู่ที่จุด (0,0) และหันหน้าไปทางแกน +X (0 องศา)
        initial_pose = Pose2D()
        initial_pose.x = 0.0
        initial_pose.y = 0.0
        initial_pose.theta = math.radians(0.0)
        self.robot_pose_pub.publish(initial_pose)
        self.get_logger().info(f"Resetting Robot Pose to: X={initial_pose.x}, Y={initial_pose.y}, Theta=0°")

        # --- ขั้นตอนที่ 2: สั่งเป้าหมาย (Move Target) ---
        msg = Pose2D()
        msg.x = 0.6      # เดินไปข้างหน้า 50 cm
        msg.y = 0.6      # ไม่เบี่ยงซ้ายขวา
        msg.theta = math.radians(90.0) # เมื่อถึงจุดหมาย ให้หันหน้าไปทางซ้าย (+Y)

        self.target_pub.publish(msg)
        self.get_logger().info(
            f"Sent Mission: Move X{msg.x}, Y:{msg.y} and Align to {math.degrees(msg.theta)}°"
        )
        
        self.timer.cancel()

    def done_callback(self, msg):
        if msg.data:
            self.get_logger().info("Mission Success: Arrived and Aligned.")

def main():
    rclpy.init()
    node = MissionNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()