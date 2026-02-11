// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#ifndef CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__TRAITS_HPP_
#define CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "capstone_vision/msg/detail/pick_target_world__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace capstone_vision
{

namespace msg
{

inline void to_flow_style_yaml(
  const PickTargetWorld & msg,
  std::ostream & out)
{
  out << "{";
  // member: x_mm
  {
    out << "x_mm: ";
    rosidl_generator_traits::value_to_yaml(msg.x_mm, out);
    out << ", ";
  }

  // member: y_mm
  {
    out << "y_mm: ";
    rosidl_generator_traits::value_to_yaml(msg.y_mm, out);
    out << ", ";
  }

  // member: label
  {
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << ", ";
  }

  // member: locked
  {
    out << "locked: ";
    rosidl_generator_traits::value_to_yaml(msg.locked, out);
    out << ", ";
  }

  // member: conf
  {
    out << "conf: ";
    rosidl_generator_traits::value_to_yaml(msg.conf, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PickTargetWorld & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x_mm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x_mm: ";
    rosidl_generator_traits::value_to_yaml(msg.x_mm, out);
    out << "\n";
  }

  // member: y_mm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y_mm: ";
    rosidl_generator_traits::value_to_yaml(msg.y_mm, out);
    out << "\n";
  }

  // member: label
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << "\n";
  }

  // member: locked
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "locked: ";
    rosidl_generator_traits::value_to_yaml(msg.locked, out);
    out << "\n";
  }

  // member: conf
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "conf: ";
    rosidl_generator_traits::value_to_yaml(msg.conf, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PickTargetWorld & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace capstone_vision

namespace rosidl_generator_traits
{

[[deprecated("use capstone_vision::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const capstone_vision::msg::PickTargetWorld & msg,
  std::ostream & out, size_t indentation = 0)
{
  capstone_vision::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use capstone_vision::msg::to_yaml() instead")]]
inline std::string to_yaml(const capstone_vision::msg::PickTargetWorld & msg)
{
  return capstone_vision::msg::to_yaml(msg);
}

template<>
inline const char * data_type<capstone_vision::msg::PickTargetWorld>()
{
  return "capstone_vision::msg::PickTargetWorld";
}

template<>
inline const char * name<capstone_vision::msg::PickTargetWorld>()
{
  return "capstone_vision/msg/PickTargetWorld";
}

template<>
struct has_fixed_size<capstone_vision::msg::PickTargetWorld>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<capstone_vision::msg::PickTargetWorld>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<capstone_vision::msg::PickTargetWorld>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__TRAITS_HPP_
