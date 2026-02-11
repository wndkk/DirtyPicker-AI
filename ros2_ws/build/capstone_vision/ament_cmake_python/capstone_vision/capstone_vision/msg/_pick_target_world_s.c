// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from capstone_vision:msg/PickTargetWorld.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "capstone_vision/msg/detail/pick_target_world__struct.h"
#include "capstone_vision/msg/detail/pick_target_world__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool builtin_interfaces__msg__time__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * builtin_interfaces__msg__time__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool capstone_vision__msg__pick_target_world__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[55];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("capstone_vision.msg._pick_target_world.PickTargetWorld", full_classname_dest, 54) == 0);
  }
  capstone_vision__msg__PickTargetWorld * ros_message = _ros_message;
  {  // x_mm
    PyObject * field = PyObject_GetAttrString(_pymsg, "x_mm");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->x_mm = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // y_mm
    PyObject * field = PyObject_GetAttrString(_pymsg, "y_mm");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->y_mm = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // label
    PyObject * field = PyObject_GetAttrString(_pymsg, "label");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->label, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // locked
    PyObject * field = PyObject_GetAttrString(_pymsg, "locked");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->locked = (Py_True == field);
    Py_DECREF(field);
  }
  {  // conf
    PyObject * field = PyObject_GetAttrString(_pymsg, "conf");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->conf = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // stamp
    PyObject * field = PyObject_GetAttrString(_pymsg, "stamp");
    if (!field) {
      return false;
    }
    if (!builtin_interfaces__msg__time__convert_from_py(field, &ros_message->stamp)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * capstone_vision__msg__pick_target_world__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of PickTargetWorld */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("capstone_vision.msg._pick_target_world");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "PickTargetWorld");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  capstone_vision__msg__PickTargetWorld * ros_message = (capstone_vision__msg__PickTargetWorld *)raw_ros_message;
  {  // x_mm
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->x_mm);
    {
      int rc = PyObject_SetAttrString(_pymessage, "x_mm", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // y_mm
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->y_mm);
    {
      int rc = PyObject_SetAttrString(_pymessage, "y_mm", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // label
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->label.data,
      strlen(ros_message->label.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "label", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // locked
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->locked ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "locked", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // conf
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->conf);
    {
      int rc = PyObject_SetAttrString(_pymessage, "conf", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // stamp
    PyObject * field = NULL;
    field = builtin_interfaces__msg__time__convert_to_py(&ros_message->stamp);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "stamp", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
