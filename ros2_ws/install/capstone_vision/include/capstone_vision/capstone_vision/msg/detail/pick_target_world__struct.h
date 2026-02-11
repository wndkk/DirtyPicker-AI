// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#ifndef CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_H_
#define CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'label'
#include "rosidl_runtime_c/string.h"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/PickTargetWorld in the package capstone_vision.
typedef struct capstone_vision__msg__PickTargetWorld
{
  float x_mm;
  float y_mm;
  rosidl_runtime_c__String label;
  bool locked;
  float conf;
  builtin_interfaces__msg__Time stamp;
} capstone_vision__msg__PickTargetWorld;

// Struct for a sequence of capstone_vision__msg__PickTargetWorld.
typedef struct capstone_vision__msg__PickTargetWorld__Sequence
{
  capstone_vision__msg__PickTargetWorld * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} capstone_vision__msg__PickTargetWorld__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_H_
