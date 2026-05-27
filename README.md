

<div align="center">

# Autonomous Outdoor Rover

<i> Jeremy Huhta, Gayani Disawage, Edijs Strolis </i>

<h3><i>Autonomous GPS-guided rover platform for outdoor navigation & robotics experimentation</i></h3>

<p>
A student-built <strong>autonomous robotics platform</strong> focused on outdoor navigation, waypoint traversal, and real-world robotics experimentation using embedded systems, computer vision, and autonomous navigation concepts.
</p>


</div>

### <ins>Videos and Images</ins>

<div align="center">
  
<br> 
<br> 

<img width="995" height="542" alt="image" src="https://github.com/user-attachments/assets/87400936-c571-4014-8ba8-585dcfc21170" />

<br> 
<br> 

<img width="528" height="706" alt="image" src="https://github.com/user-attachments/assets/1572a70d-3629-4ac4-86d2-0caf2193791a" />

<br> 
<br> 

### Videos & Documentation

[Demonstration 1 ](https://drive.google.com/file/d/13XhkIBho0NHk22KdxnauqyNc27zsrg2S/view?usp=sharing)

[Demonstration 2](https://drive.google.com/file/d/1eCOzFyEx8hW3prvHlIMfsB_pQN1z7qxf/view?usp=sharing)
 
[PX4 SITL Simulation Documentation](https://docs.google.com/document/d/1z3-eDyU8_LM__Pzj1X5ttv-u5MphG-FmZoaNTeOQ9Qo/edit?usp=sharing)



</div>

<br>

---

### <ins>The Problem</ins>

Building autonomous outdoor robots is difficult because real-world environments are unpredictable. GPS drift, uneven terrain, obstacle avoidance, unreliable wireless communication, and embedded hardware limitations all create challenges for reliable autonomous navigation.

This project explores how an autonomous rover can:
- Navigate outdoors using GPS waypoints
- Process real-world sensor data
- Operate using embedded hardware
- Serve as a flexible robotics experimentation platform

The goal was to create a practical robotics system capable of autonomous movement while remaining affordable and modular for future development.

<br>

---

### <ins>Features</ins>

- **Autonomous waypoint navigation** — rover follows predefined GPS coordinates outdoors
- **Embedded robotics platform** — integrates sensors, motors, and onboard compute hardware
- **Real-world outdoor testing** — designed for rough terrain and open-environment experimentation
- **Modular architecture** — components can be expanded or swapped easily
- **Sensor integration** — supports GPS and additional robotics peripherals
- **Remote monitoring & control** — manual intervention and testing support
- **Navigation experimentation** — ideal platform for robotics, autonomy, and pathfinding research
- **Scalable software structure** — designed to support future computer vision and AI integration

<br>

---

### <ins>Architecture</ins>

<div align="center">

GPS + Sensors  
→ Embedded Controller  
→ Navigation Logic  
→ Motor Control System  
→ Outdoor Rover Platform  

</div>

- **GPS modules** provide waypoint positioning and outdoor localization
- **Embedded controllers** handle navigation and hardware communication
- **Motor drivers** translate navigation decisions into rover movement
- **Sensor systems** provide environmental awareness and telemetry
- **Modular software design** allows rapid experimentation and future upgrades

<br>

---

### <ins>Navigation System</ins>

The rover uses waypoint-based autonomous navigation for outdoor movement.

The navigation workflow includes:

- Reading GPS coordinates
- Calculating direction and heading
- Moving toward target waypoints
- Continuously correcting trajectory
- Handling real-world movement inaccuracies

The platform was designed as both:
- a robotics learning project
- a foundation for more advanced autonomy systems

<br>

---

### <ins>Hardware</ins>

The rover platform integrates multiple hardware systems for autonomous operation.

Potential components include:
- GPS modules
- Embedded microcontrollers
- Motor drivers
- Battery systems
- Wireless communication modules
- Chassis & drivetrain hardware
- Sensor peripherals

The modular design allows future expansion with:
- LiDAR
- Computer vision
- SLAM
- Obstacle avoidance
- AI inference systems

<br>

---

### <ins>Software Stack</ins>

| Component | Technology |
|---|---|
| Language | Python / Embedded C++ |
| Robotics | Autonomous Navigation |
| Localization | GPS |
| Hardware Control | Embedded Systems |
| Platform | Outdoor Rover |
| Development Style | Modular Robotics Architecture |

<br>

---

### <ins>Use Cases</ins>

This rover platform can be extended for:

- Autonomous robotics research
- GPS waypoint experimentation
- Outdoor robotics competitions
- Agricultural robotics
- Autonomous delivery concepts
- Sensor fusion experimentation
- SLAM & mapping research
- Computer vision integration

<br>

---

### <ins>Future Improvements</ins>

- LiDAR integration
- Real-time obstacle avoidance
- ROS / ROS2 integration
- SLAM implementation
- Computer vision navigation
- Autonomous path planning
- Remote telemetry dashboard
- AI-based terrain analysis
- Improved battery management
- Multi-sensor fusion

<br>

---

### <ins>Lessons Learned</ins>

This project provided hands-on experience with:
- autonomous robotics
- outdoor navigation systems
- embedded hardware integration
- real-world sensor limitations
- robotics software architecture
- debugging autonomous systems in uncontrolled environments

---

<div align="center">

<i>Built as a hands-on autonomous robotics and outdoor navigation project.</i>

</div>

