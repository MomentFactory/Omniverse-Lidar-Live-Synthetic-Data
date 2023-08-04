# MF Lidar live synthetic data [mf.ov.lidar_live_synth]

Adds an Action Graph Node ("Generic/Beam to Ouster UDP") to send Isaac beam data via the Ouster(tm) UDP procotol.
This will allow any third party software implementing supporting Ouster(tm) lidars to be connected to simulated sensors instead of physical sensors.

All the data inputs from the node should be plugged in from a "Isaac Read Lidar Beams Node".

## Supported Lidars

Currently, only Ouster™ sensors are supported. 

The Lidar must have 16, 32, 64 or 128 rows to be supported by the procotol. 

Lidar FOVs and resolutions are not transmitted in the protocol and therefore should match those of an actual Ouster(tm) model (22.5, 45 or 90 degrees FOV) for an accurate reconstruction by the receiving software. 

JSON config files that describe the angles of the beams for an external application are included in the 'data' folder (example : [OusterJsonConfigOmniverse-OS0-16.json](exts/mf.ov.lidar_live_synth/data/OusterJsonConfigOmniverse-OS0-16.json)). These files can be used in Cirrus as the Ouster(tm) Json Config file to properly recronstruct the data with the correct beam angles. OS0 are 90 degrees FOV, OS1 are 45 and OS2 are 22.5.

## How to use

Requires Isaac Sim as well as a third party software that can connect to Lidar sensors. 

You can use the [usd demo file](./isaac_lidar_sample_moving_cube.usd), or create your own following the instructions below.

### In Isaac Sim:
1. Activate the MF LIDAR LIVE SYNTHETIC DATA extension
2. Open or create a scene
    - Meshes requires a Rigidbody to intercept Lidar raycast
    - Right-click a mesh, then select `Add / Physics / Rigid Body`
3. Add a Lidar to the scene if not present
    - `Create / Isaac / Sensors / Lidar / Generic`
    - Unfold Raw USD Properties
    - Check `drawPoints` and/or `drawLines` if you want to see the point cloud
    - Check the `enabled` property
    - Use `horizontalFov`, `horizontalResolution`. `maxRange`, `minRange`, `verticalFov`, and `verticalResolution` to define the Lidar raycast zone
    - set `rotationRate` to `0` if you want continuous raycast
4. Create an action graph
    - Right-click the Stage, then select `Create / Visual Scripting / Action Graph`
    - Right-click the Action Graph then select "Open Graph"
    - Add a `Event / On Playback Tick` node
    - Add a `Isaac Range Sensor / Isaac Read Lidar Beam Node`
    - Connect the "Tick" output to the "Exec In" input
    - Add a `Generic / Beam to Ouster UDP` node
    - Connect the "Exec Out" output to the "Exec In" input
    - Connect the outputs of `Isaac Read Lidar Beam Node` to the matching `Beam to Ouster UDP` inputs
        - `Azimuth Range`
        - `Horizontal Resolution`
        - `Linear Depth Data`
        - `Num Cols`
        - `Num Rows`

6. Press the play icon (SPACE) to begin the simulation

### Beam to Ouster UDP
- `IP Address` (string): The IP address to send the data to
- `Port` (int): The port to send the data to (also used in Cirrus)
- `Broadcast` (bool): Check to property if the IP Address is a broadcast address
