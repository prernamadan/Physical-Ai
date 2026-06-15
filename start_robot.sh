#!/bin/bash

# 1. Give the Pi 5 seconds to finish booting hardware
sleep 5

# 2. Source the ROS 2 Workspace

source /home/rahulyennu/ros2_WorkSpace/physical_ai_env/bin/activate
source /home/rahulyennu/ros2_WorkSpace/install/setup.bash

# 3. Launch the EYES (Sensor Node) in the background using the '&' symbol
ros2 run my_package1 real_sensor_node &

# 4. Launch the BRAIN & MUSCLE (AI Motor Node) in the foreground
ros2 run my_package1 ai_motor_node
