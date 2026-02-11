// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#ifndef CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_HPP_
#define CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__capstone_vision__msg__PickTargetWorld __attribute__((deprecated))
#else
# define DEPRECATED__capstone_vision__msg__PickTargetWorld __declspec(deprecated)
#endif

namespace capstone_vision
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct PickTargetWorld_
{
  using Type = PickTargetWorld_<ContainerAllocator>;

  explicit PickTargetWorld_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x_mm = 0.0f;
      this->y_mm = 0.0f;
      this->label = "";
      this->locked = false;
      this->conf = 0.0f;
    }
  }

  explicit PickTargetWorld_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : label(_alloc),
    stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x_mm = 0.0f;
      this->y_mm = 0.0f;
      this->label = "";
      this->locked = false;
      this->conf = 0.0f;
    }
  }

  // field types and members
  using _x_mm_type =
    float;
  _x_mm_type x_mm;
  using _y_mm_type =
    float;
  _y_mm_type y_mm;
  using _label_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _label_type label;
  using _locked_type =
    bool;
  _locked_type locked;
  using _conf_type =
    float;
  _conf_type conf;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;

  // setters for named parameter idiom
  Type & set__x_mm(
    const float & _arg)
  {
    this->x_mm = _arg;
    return *this;
  }
  Type & set__y_mm(
    const float & _arg)
  {
    this->y_mm = _arg;
    return *this;
  }
  Type & set__label(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->label = _arg;
    return *this;
  }
  Type & set__locked(
    const bool & _arg)
  {
    this->locked = _arg;
    return *this;
  }
  Type & set__conf(
    const float & _arg)
  {
    this->conf = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    capstone_vision::msg::PickTargetWorld_<ContainerAllocator> *;
  using ConstRawPtr =
    const capstone_vision::msg::PickTargetWorld_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      capstone_vision::msg::PickTargetWorld_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      capstone_vision::msg::PickTargetWorld_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__capstone_vision__msg__PickTargetWorld
    std::shared_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__capstone_vision__msg__PickTargetWorld
    std::shared_ptr<capstone_vision::msg::PickTargetWorld_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PickTargetWorld_ & other) const
  {
    if (this->x_mm != other.x_mm) {
      return false;
    }
    if (this->y_mm != other.y_mm) {
      return false;
    }
    if (this->label != other.label) {
      return false;
    }
    if (this->locked != other.locked) {
      return false;
    }
    if (this->conf != other.conf) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    return true;
  }
  bool operator!=(const PickTargetWorld_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PickTargetWorld_

// alias to use template instance with default allocator
using PickTargetWorld =
  capstone_vision::msg::PickTargetWorld_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace capstone_vision

#endif  // CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__STRUCT_HPP_
