# MF Lidar live synthetic data [mf.ov.lidar_live_synth]

Adds an Action Graph Node ("Generic/Beam to Ouster UDP") to send Isaac beam data via the Ouster(tm) UDP procotol.
This will allow any third party software implementing supporting Ouster(tm) lidars to be connected to simulated sensors instead of physical sensors.

It is developped for kit 104.2 and currently working only in Isaac Sim. 
This extensions only provide pre-built binaries for x86_64, for Linux version you may want to compile from the [source code](https://github.com/MomentFactory/Omniverse-Lidar-Live-Synthetic-Data) 

All the data inputs from the node should be plugged in from a "Isaac Read Lidar Beams Node".

The Lidar must have 16, 32, 64 or 128 rows to be supported by the procotol. 

Lidar FOVs and resolutions are not transmitted in the protocol and therefore should match those of an actual Ouster(tm) model (22.5, 45 or 90 degrees FOV) for an accurate reconstruction by the receiving software. 

JSON config files that describe the angles of the beams for an external application are included in the 'data' folder (ie OusterJsonConfigOmniverse-OS0-16.json). These files can be used in Cirrus as the Ouster(tm) Json Config file to properly recronstruct the data with the correct beam angles. OS0 are 90 degrees FOV, OS1 are 45 and OS2 are 22.5.