// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "capstone_vision/msg/detail/pick_target_world__rosidl_typesupport_introspection_c.h"
#include "capstone_vision/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "capstone_vision/msg/detail/pick_target_world__functions.h"
#include "capstone_vision/msg/detail/pick_target_world__struct.h"


// Include directives for member types
// Member `label`
#include "rosidl_runtime_c/string_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  capstone_vision__msg__PickTargetWorld__init(message_memory);
}

void capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_fini_function(void * message_memory)
{
  capstone_vision__msg__PickTargetWorld__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_member_array[6] = {
  {
    "x_mm",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, x_mm),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "y_mm",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, y_mm),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "label",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, label),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "locked",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, locked),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "conf",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, conf),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(capstone_vision__msg__PickTargetWorld, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_members = {
  "capstone_vision__msg",  // message namespace
  "PickTargetWorld",  // message name
  6,  // number of fields
  sizeof(capstone_vision__msg__PickTargetWorld),
  capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_member_array,  // message members
  capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_init_function,  // function to initialize message memory (memory has to be allocated)
  capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_type_support_handle = {
  0,
  &capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_capstone_vision
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, capstone_vision, msg, PickTargetWorld)() {
  capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_member_array[5].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_type_support_handle.typesupport_identifier) {
    capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &capstone_vision__msg__PickTargetWorld__rosidl_typesupport_introspection_c__PickTargetWorld_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
