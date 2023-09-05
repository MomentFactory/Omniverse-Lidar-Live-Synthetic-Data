"""Support for simplified access to data on nodes of type mf.ov.lidar_live_synth.BeamToOusterUDPNode

Receives beam data from Isaac Lidar and send it via the Ouster UDP protocol
"""

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn
import numpy
class OgnBeamToOusterUDPNodeDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type mf.ov.lidar_live_synth.BeamToOusterUDPNode

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.azimuthRange
            inputs.broadcast
            inputs.execIn
            inputs.horizontalResolution
            inputs.ip_address
            inputs.linearDepthData
            inputs.numCols
            inputs.numRows
            inputs.port
        Outputs:
            outputs.execOut
    """
    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}
    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:azimuthRange', 'float2', 0, 'Azimuth Range', 'The azimuth range [min, max]', {ogn.MetadataKeys.DEFAULT: '[-3.14159, 3.14159]'}, True, [-3.14159, 3.14159], False, ''),
        ('inputs:broadcast', 'bool', 0, 'Broadcast', 'Whether the IP address is a broadcast address or not', {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:execIn', 'execution', 0, 'Exec In', 'Execution', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:horizontalResolution', 'float', 0, 'Horizontal Resolution', 'Degrees in between rays for horizontal axis', {ogn.MetadataKeys.DEFAULT: '2'}, True, 2, False, ''),
        ('inputs:ip_address', 'string', 0, 'IP Address', 'The message destination IP address', {ogn.MetadataKeys.DEFAULT: '"127.0.0.1"'}, True, '127.0.0.1', False, ''),
        ('inputs:linearDepthData', 'float[]', 0, 'Linear Depth Data', 'Buffer array containing linear depth data', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:numCols', 'int', 0, 'Num Cols', 'Number of columns in buffers', {ogn.MetadataKeys.DEFAULT: '1'}, True, 1, False, ''),
        ('inputs:numRows', 'int', 0, 'Num Rows', 'Number of rows in buffers', {ogn.MetadataKeys.DEFAULT: '1'}, True, 1, False, ''),
        ('inputs:port', 'int', 0, 'Port', 'The port to which to send the data to', {ogn.MetadataKeys.DEFAULT: '8037'}, True, 8037, False, ''),
        ('outputs:execOut', 'execution', 0, 'Exec Out', 'Output execution triggers when the data has been sent', {}, True, None, False, ''),
    ])
    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.Database.ROLE_EXECUTION
        role_data.outputs.execOut = og.Database.ROLE_EXECUTION
        return role_data
    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"azimuthRange", "broadcast", "execIn", "horizontalResolution", "ip_address", "numCols", "numRows", "port", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.azimuthRange, self._attributes.broadcast, self._attributes.execIn, self._attributes.horizontalResolution, self._attributes.ip_address, self._attributes.numCols, self._attributes.numRows, self._attributes.port]
            self._batchedReadValues = [[-3.14159, 3.14159], False, 0, 2, "127.0.0.1", 1, 1, 8037]

        @property
        def linearDepthData(self):
            data_view = og.AttributeValueHelper(self._attributes.linearDepthData)
            return data_view.get()

        @linearDepthData.setter
        def linearDepthData(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.linearDepthData)
            data_view = og.AttributeValueHelper(self._attributes.linearDepthData)
            data_view.set(value)
            self.linearDepthData_size = data_view.get_array_size()

        @property
        def azimuthRange(self):
            return self._batchedReadValues[0]

        @azimuthRange.setter
        def azimuthRange(self, value):
            self._batchedReadValues[0] = value

        @property
        def broadcast(self):
            return self._batchedReadValues[1]

        @broadcast.setter
        def broadcast(self, value):
            self._batchedReadValues[1] = value

        @property
        def execIn(self):
            return self._batchedReadValues[2]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[2] = value

        @property
        def horizontalResolution(self):
            return self._batchedReadValues[3]

        @horizontalResolution.setter
        def horizontalResolution(self, value):
            self._batchedReadValues[3] = value

        @property
        def ip_address(self):
            return self._batchedReadValues[4]

        @ip_address.setter
        def ip_address(self, value):
            self._batchedReadValues[4] = value

        @property
        def numCols(self):
            return self._batchedReadValues[5]

        @numCols.setter
        def numCols(self, value):
            self._batchedReadValues[5] = value

        @property
        def numRows(self):
            return self._batchedReadValues[6]

        @numRows.setter
        def numRows(self, value):
            self._batchedReadValues[6] = value

        @property
        def port(self):
            return self._batchedReadValues[7]

        @port.setter
        def port(self, value):
            self._batchedReadValues[7] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _prefetch(self):
            readAttributes = self._batchedReadAttributes
            newValues = _og._prefetch_input_attributes_data(readAttributes)
            if len(readAttributes) == len(newValues):
                self._batchedReadValues = newValues
    class ValuesForOutputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"execOut", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def execOut(self):
            value = self._batchedWriteValues.get(self._attributes.execOut)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.execOut)
                return data_view.get()

        @execOut.setter
        def execOut(self, value):
            self._batchedWriteValues[self._attributes.execOut] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _commit(self):
            _og._commit_output_attributes_data(self._batchedWriteValues)
            self._batchedWriteValues = { }
    class ValuesForState(og.DynamicAttributeAccess):
        """Helper class that creates natural hierarchical access to state attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
    def __init__(self, node):
        super().__init__(node)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.inputs = OgnBeamToOusterUDPNodeDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnBeamToOusterUDPNodeDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnBeamToOusterUDPNodeDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)
