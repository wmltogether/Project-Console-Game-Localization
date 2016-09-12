import os
import struct
import codecs
from arc_tool import *

arc = ARC("script.mpk")
arc.unpack_arc("script.mpk_unpacked")

arc = ARC("system.mpk")
arc.unpack_arc("system.mpk_unpacked")
