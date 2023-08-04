"""
This is the implementation of the OGN node defined in OgnBeamToOusterUDPNode.ogn
"""

from pxr import Gf
from typing import List

import math
import numpy as np
import omni.graph.core as og
import socket
import time
import struct

class OgnBeamToOusterUDPNodeInternalState:
    def __init__(self):
        self.frameId = 0

    def update_frameId(self):
        self.frameId += 1

class OgnBeamToOusterUDPNode:
    """
         Receives point cloud data from Isaac Lidar and send it via the Ouster UDP protocol.
    """
    COLUMNS_PER_PACKET = 16
    TWO_PI = np.pi * 2.0
    DEG_TO_RAD = TWO_PI / 360.0
    OUSTER_NUM_ROT_ANGLES = 90112
    OUSTER_NUM_ROT_ANGLES_OVER_TWO_PI = OUSTER_NUM_ROT_ANGLES / TWO_PI

    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnBeamToOusterUDPNodeInternalState()
    
    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""

        numRows = db.inputs.numRows
        linearDepthData = db.inputs.linearDepthData
        numCols = db.inputs.numCols
        azimuthStart = db.inputs.azimuthRange[0] + OgnBeamToOusterUDPNode.TWO_PI
        horizontalStepInRads = -1.0 * db.inputs.horizontalResolution * OgnBeamToOusterUDPNode.DEG_TO_RAD
        frame_id = db.internal_state.frameId % 65536

        try:
            measurement_id = 0

            if (numRows != 16 and
                  numRows != 32 and
                  numRows != 64 and
                  numRows != 128):

                db.log_error("Row count must be either 16, 32, 64 or 128, not " + str(numRows))
                return False

            # # Packet structure :
            # # OusterAzimuthBlock [16]
            # #     unsigned long long timeStamp
            # #     unsigned short measurementId
            # #     unsigned short frameId
            # #     unsigned int encoderCount
            # #     OusterChannelDataBlock [N] = 16,32,64 OR 128
            # #         unsigned int rangemm
            # #         unsigned short reflectivity
            # #         unsigned short signal_photons
            # #         unsigned short noise_photons
            # #         unsigned short unused
            # #     unsigned int azimuthDataBlockStatus

            packet_point_dtype = np.dtype([('distance', 'u4'),
                                           ('reflectivity', 'u2'),
                                           ('signal_photons', 'u2'),
                                           ('noise_photons', 'u2'),
                                           ('unused', 'u2')])
            
            packet_column_dtype = np.dtype([('timestamp', 'u8'),
                                            ('measurement_id', 'u2'),
                                            ('frame_id', 'u2'),
                                            ('encoder_count', 'u4'),
                                            ('points', packet_point_dtype, (numRows)),
                                            ('block_status', 'u4')])

            chunks = []  # We will likely have multiple packets to send. Each packet contains at most 16 columns
            chunk = np.zeros(OgnBeamToOusterUDPNode.COLUMNS_PER_PACKET, packet_column_dtype)
            current_chunk_column = 0
            
            linearDepthDataInMillimeters = np.zeros(shape=(len(linearDepthData)), dtype=int)
            for index in range(len(linearDepthData)):
                linearDepthDataInMillimeters[index] = int(linearDepthData[index] * 1000)

            # We need to send data in ascending angle (encoder_count) order
            # Data is in right-to-left order, we need to iterate left-to-right
            # We also need to start at the middle (center) of the data which is encoderCount 0
            colEndIndex = (numCols - 1) // 2
            colStartIndex = colEndIndex + numCols

            for temp_col_index in range(colStartIndex, colEndIndex, -1):

                col_index = temp_col_index % numCols

                # This assumes consistent input data across azimuthRange, horizontalResolution, numCols, numRows and linearDepthData size
                # We are lenient on the checks, it should just fail if something doesnt work out and throw an error
                current_encoderCount = int((azimuthStart + horizontalStepInRads * temp_col_index)
                                            * OgnBeamToOusterUDPNode.OUSTER_NUM_ROT_ANGLES_OVER_TWO_PI)

                # If previous chunk is complete, start new one
                if current_chunk_column == OgnBeamToOusterUDPNode.COLUMNS_PER_PACKET:
                    chunks.append(chunk)
                    chunk = np.zeros(OgnBeamToOusterUDPNode.COLUMNS_PER_PACKET, packet_column_dtype)
                    current_chunk_column = 0
                
                chunk[current_chunk_column]['timestamp'] = time.time_ns()
                chunk[current_chunk_column]['measurement_id'] = measurement_id
                chunk[current_chunk_column]['frame_id'] = frame_id
                chunk[current_chunk_column]['encoder_count'] = current_encoderCount

                measurement_id = (measurement_id + 1) % 65536
                col_index_start = col_index * numRows

                for row_index in range(numRows):

                    chunk[current_chunk_column]['points'][row_index]['distance'] = linearDepthDataInMillimeters[col_index_start + row_index]
                    chunk[current_chunk_column]['points'][row_index]['signal_photons'] = 0xFFFF #0xFFFF means valid

                chunk[current_chunk_column]['block_status'] = 0xFFFFFFFF #0xFFFFFFFF means valid

                current_chunk_column += 1

            if current_chunk_column != 0:
                for extra_column_index in range(current_chunk_column, OgnBeamToOusterUDPNode.COLUMNS_PER_PACKET):
                    chunk[extra_column_index]['timestamp'] = time.time_ns()
                    chunk[extra_column_index]['measurement_id'] = measurement_id
                    chunk[extra_column_index]['frame_id'] = frame_id
                    chunk[extra_column_index]['encoder_count'] = OgnBeamToOusterUDPNode.OUSTER_NUM_ROT_ANGLES
                
                chunks.append(chunk)

            if db.inputs.broadcast:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
                for chunk in chunks:
                    sock.sendto(chunk, (db.inputs.ip_address, db.inputs.port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                for chunk in chunks:
                    sock.sendto(chunk, (db.inputs.ip_address, db.inputs.port))
            
        except Exception as error:
            # If anything causes your compute to fail report the error and return False
            db.log_error(str(error))
            return False
        
        db.internal_state.update_frameId()

        # Always enable the output execution
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        # Even if inputs were edge cases like empty arrays, correct outputs mean success

        return True
