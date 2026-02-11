// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice
#include "capstone_vision/msg/detail/pick_target_world__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `label`
#include "rosidl_runtime_c/string_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
capstone_vision__msg__PickTargetWorld__init(capstone_vision__msg__PickTargetWorld * msg)
{
  if (!msg) {
    return false;
  }
  // x_mm
  // y_mm
  // label
  if (!rosidl_runtime_c__String__init(&msg->label)) {
    capstone_vision__msg__PickTargetWorld__fini(msg);
    return false;
  }
  // locked
  // conf
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    capstone_vision__msg__PickTargetWorld__fini(msg);
    return false;
  }
  return true;
}

void
capstone_vision__msg__PickTargetWorld__fini(capstone_vision__msg__PickTargetWorld * msg)
{
  if (!msg) {
    return;
  }
  // x_mm
  // y_mm
  // label
  rosidl_runtime_c__String__fini(&msg->label);
  // locked
  // conf
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
}

bool
capstone_vision__msg__PickTargetWorld__are_equal(const capstone_vision__msg__PickTargetWorld * lhs, const capstone_vision__msg__PickTargetWorld * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x_mm
  if (lhs->x_mm != rhs->x_mm) {
    return false;
  }
  // y_mm
  if (lhs->y_mm != rhs->y_mm) {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->label), &(rhs->label)))
  {
    return false;
  }
  // locked
  if (lhs->locked != rhs->locked) {
    return false;
  }
  // conf
  if (lhs->conf != rhs->conf) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  return true;
}

bool
capstone_vision__msg__PickTargetWorld__copy(
  const capstone_vision__msg__PickTargetWorld * input,
  capstone_vision__msg__PickTargetWorld * output)
{
  if (!input || !output) {
    return false;
  }
  // x_mm
  output->x_mm = input->x_mm;
  // y_mm
  output->y_mm = input->y_mm;
  // label
  if (!rosidl_runtime_c__String__copy(
      &(input->label), &(output->label)))
  {
    return false;
  }
  // locked
  output->locked = input->locked;
  // conf
  output->conf = input->conf;
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  return true;
}

capstone_vision__msg__PickTargetWorld *
capstone_vision__msg__PickTargetWorld__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  capstone_vision__msg__PickTargetWorld * msg = (capstone_vision__msg__PickTargetWorld *)allocator.allocate(sizeof(capstone_vision__msg__PickTargetWorld), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(capstone_vision__msg__PickTargetWorld));
  bool success = capstone_vision__msg__PickTargetWorld__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
capstone_vision__msg__PickTargetWorld__destroy(capstone_vision__msg__PickTargetWorld * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    capstone_vision__msg__PickTargetWorld__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
capstone_vision__msg__PickTargetWorld__Sequence__init(capstone_vision__msg__PickTargetWorld__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  capstone_vision__msg__PickTargetWorld * data = NULL;

  if (size) {
    data = (capstone_vision__msg__PickTargetWorld *)allocator.zero_allocate(size, sizeof(capstone_vision__msg__PickTargetWorld), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = capstone_vision__msg__PickTargetWorld__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        capstone_vision__msg__PickTargetWorld__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
capstone_vision__msg__PickTargetWorld__Sequence__fini(capstone_vision__msg__PickTargetWorld__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      capstone_vision__msg__PickTargetWorld__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

capstone_vision__msg__PickTargetWorld__Sequence *
capstone_vision__msg__PickTargetWorld__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  capstone_vision__msg__PickTargetWorld__Sequence * array = (capstone_vision__msg__PickTargetWorld__Sequence *)allocator.allocate(sizeof(capstone_vision__msg__PickTargetWorld__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = capstone_vision__msg__PickTargetWorld__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
capstone_vision__msg__PickTargetWorld__Sequence__destroy(capstone_vision__msg__PickTargetWorld__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    capstone_vision__msg__PickTargetWorld__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
capstone_vision__msg__PickTargetWorld__Sequence__are_equal(const capstone_vision__msg__PickTargetWorld__Sequence * lhs, const capstone_vision__msg__PickTargetWorld__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!capstone_vision__msg__PickTargetWorld__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
capstone_vision__msg__PickTargetWorld__Sequence__copy(
  const capstone_vision__msg__PickTargetWorld__Sequence * input,
  capstone_vision__msg__PickTargetWorld__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(capstone_vision__msg__PickTargetWorld);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    capstone_vision__msg__PickTargetWorld * data =
      (capstone_vision__msg__PickTargetWorld *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!capstone_vision__msg__PickTargetWorld__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          capstone_vision__msg__PickTargetWorld__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!capstone_vision__msg__PickTargetWorld__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
