// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice

#ifndef CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__BUILDER_HPP_
#define CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "capstone_vision/msg/detail/pick_target_world__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace capstone_vision
{

namespace msg
{

namespace builder
{

class Init_PickTargetWorld_stamp
{
public:
  explicit Init_PickTargetWorld_stamp(::capstone_vision::msg::PickTargetWorld & msg)
  : msg_(msg)
  {}
  ::capstone_vision::msg::PickTargetWorld stamp(::capstone_vision::msg::PickTargetWorld::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

class Init_PickTargetWorld_conf
{
public:
  explicit Init_PickTargetWorld_conf(::capstone_vision::msg::PickTargetWorld & msg)
  : msg_(msg)
  {}
  Init_PickTargetWorld_stamp conf(::capstone_vision::msg::PickTargetWorld::_conf_type arg)
  {
    msg_.conf = std::move(arg);
    return Init_PickTargetWorld_stamp(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

class Init_PickTargetWorld_locked
{
public:
  explicit Init_PickTargetWorld_locked(::capstone_vision::msg::PickTargetWorld & msg)
  : msg_(msg)
  {}
  Init_PickTargetWorld_conf locked(::capstone_vision::msg::PickTargetWorld::_locked_type arg)
  {
    msg_.locked = std::move(arg);
    return Init_PickTargetWorld_conf(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

class Init_PickTargetWorld_label
{
public:
  explicit Init_PickTargetWorld_label(::capstone_vision::msg::PickTargetWorld & msg)
  : msg_(msg)
  {}
  Init_PickTargetWorld_locked label(::capstone_vision::msg::PickTargetWorld::_label_type arg)
  {
    msg_.label = std::move(arg);
    return Init_PickTargetWorld_locked(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

class Init_PickTargetWorld_y_mm
{
public:
  explicit Init_PickTargetWorld_y_mm(::capstone_vision::msg::PickTargetWorld & msg)
  : msg_(msg)
  {}
  Init_PickTargetWorld_label y_mm(::capstone_vision::msg::PickTargetWorld::_y_mm_type arg)
  {
    msg_.y_mm = std::move(arg);
    return Init_PickTargetWorld_label(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

class Init_PickTargetWorld_x_mm
{
public:
  Init_PickTargetWorld_x_mm()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PickTargetWorld_y_mm x_mm(::capstone_vision::msg::PickTargetWorld::_x_mm_type arg)
  {
    msg_.x_mm = std::move(arg);
    return Init_PickTargetWorld_y_mm(msg_);
  }

private:
  ::capstone_vision::msg::PickTargetWorld msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::capstone_vision::msg::PickTargetWorld>()
{
  return capstone_vision::msg::builder::Init_PickTargetWorld_x_mm();
}

}  // namespace capstone_vision

#endif  // CAPSTONE_VISION__MSG__DETAIL__PICK_TARGET_WORLD__BUILDER_HPP_
