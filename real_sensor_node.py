import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import RPi.GPIO as GPIO
import time

class RealSensorNode(Node):
    def __init__(self):
        super().__init__('real_sensor_node')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'sensor_data', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

        # Hardware Setup
        self.sensors = [(5, 6), (13, 19), (26, 16), (20, 21), (12, 25)]
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for trig, echo in self.sensors:
            GPIO.setup(trig, GPIO.OUT)
            GPIO.setup(echo, GPIO.IN)
            GPIO.output(trig, False)
            
        self.get_logger().info("✅ REAL Sensors Online! Warming up...")
        time.sleep(2) # Give sensors time to settle

    def get_distance(self, trig, echo):
        # 10 microsecond pulse
        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        start, stop = time.time(), time.time()
        timeout = start + 0.04 # 40ms timeout

        while GPIO.input(echo) == 0 and time.time() < timeout:
            start = time.time()
        while GPIO.input(echo) == 1 and time.time() < timeout:
            stop = time.time()

        dist = ((stop - start) * 34300) / 2 /100        
        # Fail-safe: If timeout or too far, return 10.0 meters
        return 1.0 if (dist <= 0.02 or dist > 1.0) else dist

    def timer_callback(self):
        msg = Float32MultiArray()
        distances = []
        for trig, echo in self.sensors:
            distances.append(self.get_distance(trig, echo))
            time.sleep(0.01) # 10ms gap so soundwaves don't collide
            
        msg.data = distances
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = RealSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
