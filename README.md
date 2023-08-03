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

### Building the C++ extension
As the extension is written in C++ for performance reasons, developers need to build it before using it. Most of it works in the same way as the official Omniverse C++ examples (https://github.com/NVIDIA-Omniverse/kit-extension-template-cpp).

The first step is to run the build.bat file at the root of the repo. It will generate the actual extension files usable by Omniverse, as well as the Visual Studio files. It is recommended to work in Visual Studio (2019 and above) for C++, although VSCode should also work. The build.bat script generates the VS2019 .sln files in _compiler\vs2019\kit-extension-template-cpp.sln . It should work as-is. Do not upgrade the compiler and Windows SDK versions if asked to do so, and install the correct Windows SDK for the VS Installer if it is missing on your machine.

Unlike the samples, we do not recommend running the project by launching it via Visual Studio, since the extension is made specifically for Isaac Sim, and Visual Studio doesnt launch it within an Isaac Sim environment. It is recommended to run Isaac and attach the VS debugger to it by going to Debug -> Attach to Process and selecting the kit.exe coresponding to Isaac. One thing to note is that the symbols for the extension will only be loaded IF the extension is enabled after attaching. If the extension is already enabled, disabling then enabling it will also work. Also, to update the extension in Isaac after doing some changes and building, it needs to be disabled and enabled again (The extension willl probably fail to build if it is in use as the dll cannot be overwritten anyways).

To add the extension to Isaac, simply add the built plugin folder (c:/git/omniverse/omniverse-lidar-synthetic-data/_build/windows-x86_64/release/exts or c:/git/omniverse/omniverse-lidar-synthetic-data/_build/windows-x86_64/debug/exts for a debug build) to the extension manager paths