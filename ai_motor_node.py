import sys
# THE GOLDEN HACK: Force ROS 2 to use your virtual environment's NumPy 2.x
sys.path.insert(0, '/home/rahulyennu/ros2_WorkSpace/physical_ai_env/lib/python3.12/site-packages')

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import RPi.GPIO as GPIO
import numpy as np
from stable_baselines3 import PPO

class AIMotorNode(Node):
    def __init__(self):
        super().__init__('ai_motor_node')
        
        # 1. Listen for sensor data
        self.subscription = self.create_subscription(
            Float32MultiArray, 'sensor_data', self.listener_callback, 10)

        # 2. Load the Brain
        model_path = "/home/rahulyennu/Downloads/model.zip"
        self.get_logger().info(f"Waking up AI from {model_path}...")
        try:
            self.model = PPO.load(model_path)
            self.get_logger().info("✅ AI Loaded Successfully!")
        except Exception as e:
            self.get_logger().error(f"❌ Failed to load model: {e}")
            sys.exit(1)

        # 3. Setup Hardware (Motors)
        self.IN1, self.IN2, self.IN3, self.IN4 = 17, 27, 22, 23
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup([self.IN1, self.IN2, self.IN3, self.IN4], GPIO.OUT)
        
        # Start PWM at 0%
        self.left_fwd = GPIO.PWM(self.IN1, 100); self.left_fwd.start(0)
        self.left_bwd = GPIO.PWM(self.IN2, 100); self.left_bwd.start(0)
        self.right_fwd = GPIO.PWM(self.IN3, 100); self.right_fwd.start(0)
        self.right_bwd = GPIO.PWM(self.IN4, 100); self.right_bwd.start(0)

    def drive(self, left_speed, right_speed):
        # Left Motor Logic
        if left_speed >= 0:
            self.left_fwd.ChangeDutyCycle(left_speed)
            self.left_bwd.ChangeDutyCycle(0)
        else:
            self.left_fwd.ChangeDutyCycle(0)
            self.left_bwd.ChangeDutyCycle(abs(left_speed))
            
        # Right Motor Logic
        if right_speed >= 0:
            self.right_fwd.ChangeDutyCycle(right_speed)
            self.right_bwd.ChangeDutyCycle(0)
        else:
            self.right_fwd.ChangeDutyCycle(0)
            self.right_bwd.ChangeDutyCycle(abs(right_speed))

    def listener_callback(self, msg):
        sensor_data = msg.data
        
        # Ask the AI
        obs = np.array(sensor_data, dtype=np.float32)
        
        action_val, _ = self.model.predict(obs, deterministic=True)
        action = int(action_val)
        if np.min(obs)<=0.01:
         action=-1
        print(np.min(obs))
        # Your specific discrete action map
        left, right = 0, 0
        if action == -1: left, right = -100, -100
        elif action == 0: left, right = 100, 100
        elif action == 1: left, right = 0, 100
        elif action == 2: left, right = 100, 0
        elif action == 3: left, right = 0, 100
        elif action == 4: left, right = 100, 0	
        # Execute
        self.drive(left, right)
        self.get_logger().info(f"Sensors: {[round(d, 2) for d in sensor_data]} | Act: {action} -> L: {left}% R: {right}%")

def main(args=None):
    rclpy.init(args=args)
    node = AIMotorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down motors...")
    finally:
        node.drive(0, 0) # Hard stop
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()

left_one=100
right_one=40
if __name__ == '__main__':
    left_one = float(input("Enter the Left speed for action 1"))
    right_ont = float(input("Enter the right speed for action 1"))
    main()
