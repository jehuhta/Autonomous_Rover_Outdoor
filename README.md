# Autonomous RC Rover -- Object Detection, Lidar, GPS navigation

<i> Jeremy Huhta, Gayani Disawage, Edijs Strolis </i>

Lidar object avoidance and Object detection Ground Rover using MAVSDK and Autonomous navigation


<br> 

<img width="995" height="542" alt="image" src="https://github.com/user-attachments/assets/87400936-c571-4014-8ba8-585dcfc21170" />

<br> 

<img width="528" height="706" alt="image" src="https://github.com/user-attachments/assets/1572a70d-3629-4ac4-86d2-0caf2193791a" />

<br> 

* Pixhawk 6C
* RaspberryPi5
* Camera (captures frames during the mission)
* Object Detection (reports what it saw during the mission)
* Non-ROS lidar dodging using a custom library for the project (LightLidar)
* Crossfire protocol (transciever/transmitter)
* QGroundControl
* CSC DBaaS stores post-mission info, gps location, and object detection results.
* Streamlit Dashboard retrieving data from postgre db, visualizing mission results.

### Videos

https://drive.google.com/file/d/13XhkIBho0NHk22KdxnauqyNc27zsrg2S/view?usp=sharing

<br> 

https://drive.google.com/file/d/1eCOzFyEx8hW3prvHlIMfsB_pQN1z7qxf/view?usp=sharing

<br> 

<br> 

### PX4 SITL Simulation Guide in Gazebo

https://docs.google.com/document/d/1z3-eDyU8_LM__Pzj1X5ttv-u5MphG-FmZoaNTeOQ9Qo/edit?usp=sharing

