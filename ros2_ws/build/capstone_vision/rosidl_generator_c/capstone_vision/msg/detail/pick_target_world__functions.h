// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#ifndef CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__FUNCTIONS_H_
#define CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "capstone_vision/msg/rosidl_generator_c__visibility_control.h"

#include "capstone_vision/msg/detail/pick_target_world__struct.h"

/// Initialize msg/PickTargetWorld message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * capstone_vision__msg__PickTargetWorld
 * )) before or use
 * capstone_vision__msg__PickTargetWorld__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__init(capstone_vision__msg__PickTargetWorld * msg);

/// Finalize msg/PickTargetWorld message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
void
capstone_vision__msg__PickTargetWorld__fini(capstone_vision__msg__PickTargetWorld * msg);

/// Create msg/PickTargetWorld message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * capstone_vision__msg__PickTargetWorld__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
capstone_vision__msg__PickTargetWorld *
capstone_vision__msg__PickTargetWorld__create();

/// Destroy msg/PickTargetWorld message.
/**
 * It calls
 * capstone_vision__msg__PickTargetWorld__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
void
capstone_vision__msg__PickTargetWorld__destroy(capstone_vision__msg__PickTargetWorld * msg);

/// Check for msg/PickTargetWorld message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__are_equal(const capstone_vision__msg__PickTargetWorld * lhs, const capstone_vision__msg__PickTargetWorld * rhs);

/// Copy a msg/PickTargetWorld message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__copy(
  const capstone_vision__msg__PickTargetWorld * input,
  capstone_vision__msg__PickTargetWorld * output);

/// Initialize array of msg/PickTargetWorld messages.
/**
 * It allocates the memory for the number of elements and calls
 * capstone_vision__msg__PickTargetWorld__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__Sequence__init(capstone_vision__msg__PickTargetWorld__Sequence * array, size_t size);

/// Finalize array of msg/PickTargetWorld messages.
/**
 * It calls
 * capstone_vision__msg__PickTargetWorld__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
void
capstone_vision__msg__PickTargetWorld__Sequence__fini(capstone_vision__msg__PickTargetWorld__Sequence * array);

/// Create array of msg/PickTargetWorld messages.
/**
 * It allocates the memory for the array and calls
 * capstone_vision__msg__PickTargetWorld__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
capstone_vision__msg__PickTargetWorld__Sequence *
capstone_vision__msg__PickTargetWorld__Sequence__create(size_t size);

/// Destroy array of msg/PickTargetWorld messages.
/**
 * It calls
 * capstone_vision__msg__PickTargetWorld__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
void
capstone_vision__msg__PickTargetWorld__Sequence__destroy(capstone_vision__msg__PickTargetWorld__Sequence * array);

/// Check for msg/PickTargetWorld message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__Sequence__are_equal(const capstone_vision__msg__PickTargetWorld__Sequence * lhs, const capstone_vision__msg__PickTargetWorld__Sequence * rhs);

/// Copy an array of msg/PickTargetWorld messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_capstone_vision
bool
capstone_vision__msg__PickTargetWorld__Sequence__copy(
  const capstone_vision__msg__PickTargetWorld__Sequence * input,
  capstone_vision__msg__PickTargetWorld__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__FUNCTIONS_H_
