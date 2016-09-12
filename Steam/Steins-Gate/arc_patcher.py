import os
import struct
import codecs
from arc_tool import *

arc = ARC("script.mpk")
arc.patch_arc("script.mpk",'patch//')

arc = ARC("system.mpk")
arc.patch_arc("system.mpk", 'patch//')
