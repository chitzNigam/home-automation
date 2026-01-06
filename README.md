# HOME AUTOMATION

## About the project

This is a project to create systems to automate home devices like lights, fans using existing electricity grid and leveraging the network to send signals without the need to install extra cabling. 

## Key Features

- Switch appliances in home with button/touch
- Cloud support for remote toggle
- Automation and schedule for toggle
- Mobile App for easy toggle
- Remote control for convenient toggle
- Integration with local sensors to automate switch

## Future 

- Switch-less toggle
- Agent integration
- Custom home power grid
- Integration of smart devices

## How this works?

- The primary component in this system will be the home router. This router will act as the data link between the components.
- The components will be mainly small microcontrollers with wifi capabilities. Eg. Node Mcu, 8266.

# Hardware

## Switches

- Solid state relays for reliability and durability.

## Wiring

- Will be directly integrated with home's grid. 
- Copper/ aluminium wiring for connections in PoC. Integration Circuit Board for MVP

## Controller

- Node Mcu, Arduino controller
- 8266 for wifi communication

# Communication

- Over the wireless network with 2.4 GHz connection
- Public Internet for cloud communication

## Protocols

- TCP for local communication
- MQTT Event based streaming for cloud communication

# Software

- Arduino IDE for chip programming
- MQTT Broker
- Python for CRUD 
- Postgres for data storage
- Oracle Cloud for cloud support
- Android for Mobile apps

# Adapter Components

![Project Diagram](props/circuit.png)

# Server Side Components

### High Level Design

##### MVP1
![Project Diagram](props/mvp1.png)

##### MVP2
![Project Diagram](props/mvp2.png)

# References components

- Esp32 >  https://www.amazon.com/ESP-WROOM-32-Development-Aideepen-Compatible-MicroPython/dp/B0BQJ8BTVB/ref=sr_1_6

- Solid state relays > https://roboticsdna.in/product/4-channel-3-24v-relay-module-solid-state-low-level-ssr-dc-control-dc-with-resistive-fuse