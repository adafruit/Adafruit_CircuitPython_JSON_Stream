# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_json_stream`
================================================================================


.. todo:: Describe what the library does.


* Author(s): Scott Shawcroft

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports
import array
import json

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_JSON_Stream.git"

class IterToStream:
  def __init__(self, data_iter):
    self.data_iter = data_iter
    self.i = 0
    self.chunk = b""

  def read(self):
    if self.i >= len(self.chunk):
      try:
        self.chunk = next(self.data_iter)
      except StopIteration:
        raise EOFError
      self.i = 0
    c = self.chunk[self.i]
    self.i += 1
    return c

  def fast_forward(self, closer):
    closer = ord(closer)
    close_stack = [closer]
    count = 0
    while close_stack:
      c = self.read()
      count += 1
      if c == close_stack[-1]:
        close_stack.pop()
      elif c == ord("\""):
        close_stack.append(ord("\""))
      elif close_stack[-1] == ord("\""):
        # in a string so ignore [] and {}
        pass
      elif c in (ord("}"), ord("]")):
        # Mismatched list or object means we're done and already past the last comma.
        return True
      elif c == ord("{"):
        close_stack.append(ord("}"))
      elif c == ord("["):
        close_stack.append(ord("]"))
    return False

  def next_value(self, endswith):
    buf = array.array("B")
    endswith = ord(endswith)
    in_string = False
    while True:
      try:
        c = self.read()
      except EOFError:
        c = endswith
      if c == endswith or (not in_string and c in (ord("]"), ord("}"))):
        if len(buf) == 0:
          return None
        value_string = bytes(buf).decode("utf-8")
        # print(repr(value_string))
        return json.loads(value_string)
      elif c == ord("{"):
        return TransientObject(self)
      elif c == ord("["):
        return TransientList(self)
      else:
        if not in_string:
          in_string = c == ord("\"")
        else:
          in_string = c != ord("\"")
        buf.append(c)

class Transient:
  pass

class TransientList(Transient):
  def __init__(self, stream):
    self.data = stream
    self.done = False
    self.active_child = None

  def finish(self):
    if not self.done:
      if self.active_child:
        self.active_child.finish()
        self.active_child = None
      self.data.fast_forward("]")
    self.done = True

  def __iter__(self):
    return self

  def __next__(self):
    if self.active_child:
      self.active_child.finish()
      self.done = self.data.fast_forward(",")
      self.active_child = None
    if self.done:
      raise StopIteration()
    next_value = self.data.next_value(",")
    if next_value is None:
      self.done = True
      raise StopIteration()
    if isinstance(next_value, Transient):
      self.active_child = next_value
    return next_value

class TransientObject(Transient):
  def __init__(self, stream):
    self.data = stream
    self.done = False
    self.buf = array.array("B")

    self.active_child = None

  def finish(self):
    if not self.done:
      if self.active_child:
        self.active_child.finish()
        self.active_child = None
      self.data.fast_forward("}")
    self.done = True

  def __getitem__(self, key):
    if self.active_child:
      self.active_child.finish()
      self.done = self.data.fast_forward(",")
      self.active_child = None
    if self.done:
      raise KeyError()
    # print("get", key)
    found = False
    while True:
      current_key = self.data.next_value(":")
      if current_key is None:
        # print("object done", self)
        self.done = True
        break
      if current_key == key:
        next_value = self.data.next_value(",")
        if isinstance(next_value, Transient):
          self.active_child = next_value
        return next_value
      else:
        self.data.fast_forward(",")
    raise KeyError()


def load(data_iter):
  stream = IterToStream(data_iter)
  c = stream.read()
  if c == ord("{"):
    return TransientObject(stream)
  elif c == ord("["):
    return TransientList(stream)
  else:
    # TODO: single value?
    return None
