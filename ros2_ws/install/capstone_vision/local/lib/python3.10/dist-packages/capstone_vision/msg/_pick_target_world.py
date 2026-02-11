# generated from rosidl_generator_py/resource/_idl.py.em
# with input from capstone_vision:msg/PickTargetWorld.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_PickTargetWorld(type):
    """Metaclass of message 'PickTargetWorld'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('capstone_vision')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'capstone_vision.msg.PickTargetWorld')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__pick_target_world
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__pick_target_world
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__pick_target_world
            cls._TYPE_SUPPORT = module.type_support_msg__msg__pick_target_world
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__pick_target_world

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class PickTargetWorld(metaclass=Metaclass_PickTargetWorld):
    """Message class 'PickTargetWorld'."""

    __slots__ = [
        '_x_mm',
        '_y_mm',
        '_label',
        '_locked',
        '_conf',
        '_stamp',
    ]

    _fields_and_field_types = {
        'x_mm': 'float',
        'y_mm': 'float',
        'label': 'string',
        'locked': 'boolean',
        'conf': 'float',
        'stamp': 'builtin_interfaces/Time',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.x_mm = kwargs.get('x_mm', float())
        self.y_mm = kwargs.get('y_mm', float())
        self.label = kwargs.get('label', str())
        self.locked = kwargs.get('locked', bool())
        self.conf = kwargs.get('conf', float())
        from builtin_interfaces.msg import Time
        self.stamp = kwargs.get('stamp', Time())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.x_mm != other.x_mm:
            return False
        if self.y_mm != other.y_mm:
            return False
        if self.label != other.label:
            return False
        if self.locked != other.locked:
            return False
        if self.conf != other.conf:
            return False
        if self.stamp != other.stamp:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def x_mm(self):
        """Message field 'x_mm'."""
        return self._x_mm

    @x_mm.setter
    def x_mm(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'x_mm' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'x_mm' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._x_mm = value

    @builtins.property
    def y_mm(self):
        """Message field 'y_mm'."""
        return self._y_mm

    @y_mm.setter
    def y_mm(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'y_mm' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'y_mm' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._y_mm = value

    @builtins.property
    def label(self):
        """Message field 'label'."""
        return self._label

    @label.setter
    def label(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'label' field must be of type 'str'"
        self._label = value

    @builtins.property
    def locked(self):
        """Message field 'locked'."""
        return self._locked

    @locked.setter
    def locked(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'locked' field must be of type 'bool'"
        self._locked = value

    @builtins.property
    def conf(self):
        """Message field 'conf'."""
        return self._conf

    @conf.setter
    def conf(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'conf' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'conf' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._conf = value

    @builtins.property
    def stamp(self):
        """Message field 'stamp'."""
        return self._stamp

    @stamp.setter
    def stamp(self, value):
        if __debug__:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'stamp' field must be a sub message of type 'Time'"
        self._stamp = value
