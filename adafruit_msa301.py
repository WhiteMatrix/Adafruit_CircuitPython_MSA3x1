# The MIT License (MIT)
#
# Copyright (c) 2019 Bryan Siepert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`MSA301`
================================================================================

CircuitPython library for the MSA301 Accelerometer


* Author(s): Bryan Siepert

Implementation Notes
--------------------

**Hardware:**

* Adafruit MSA301 Breakout https://www.adafruit.com/product/4344

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MSA301.git"

import struct
from micropython import const
from adafruit_register.i2c_struct import ROUnaryStruct
from adafruit_register.i2c_bit import RWBit
from adafruit_register.i2c_bits import RWBits, ROBits
import adafruit_bus_device.i2c_device as i2cdevice
_MSA301_I2CADDR_DEFAULT = const(0x26)

_MSA301_REG_PARTID = const(0x01)
_MSA301_REG_OUT_X_L = const(0x02)
_MSA301_REG_OUT_X_H = const(0x03)
_MSA301_REG_OUT_Y_L = const(0x04)
_MSA301_REG_OUT_Y_H = const(0x05)
_MSA301_REG_OUT_Z_L = const(0x06)
_MSA301_REG_OUT_Z_H = const(0x07)
_MSA301_REG_MOTIONINT = const(0x09)
_MSA301_REG_DATAINT = const(0x0A)
_MSA301_REG_CLICKSTATUS = const(0x0B)
_MSA301_REG_RESRANGE = const(0x0F)
_MSA301_REG_ODR = const(0x10)
_MSA301_REG_POWERMODE = const(0x11)
_MSA301_REG_INTSET0 = const(0x16)
_MSA301_REG_INTSET1 = const(0x17)
_MSA301_REG_INTMAP0 = const(0x19)
_MSA301_REG_INTMAP1 = const(0x1A)
_MSA301_REG_TAPDUR = const(0x2A)
_MSA301_REG_TAPTH = const(0x2B)


_STANDARD_GRAVITY = 9.806
class Mode: # pylint: disable=too-few-public-methods
    """An enum-like class representing the different modes that the MSA301 can
    use. The values can be referenced like ``Mode.NORMAL`` or ``Mode.SUSPEND``
    Possible values are

    - ``Mode.NORMAL``
    - ``Mode.LOW_POWER``
    - ``Mode.SUSPEND``
    """
    # pylint: disable=invalid-name
    NORMAL = 0b00
    LOWPOWER = 0b01
    SUSPEND = 0b010

class DataRate: # pylint: disable=too-few-public-methods
    """An enum-like class representing the different data rates that the MSA301 can
    use. The values can be referenced like ``DataRate.RATE_1_HZ`` or ``DataRate.RATE_1000_HZ``
    Possible values are

    - ``DataRate.RATE_1_HZ``
    - ``DataRate.RATE_1_95_HZ``
    - ``DataRate.RATE_3_9_HZ``
    - ``DataRate.RATE_7_81_HZ``
    - ``DataRate.RATE_15_63_HZ``
    - ``DataRate.RATE_31_25_HZ``
    - ``DataRate.RATE_62_5_HZ``
    - ``DataRate.RATE_125_HZ``
    - ``DataRate.RATE_250_HZ``
    - ``DataRate.RATE_500_HZ``
    - ``DataRate.RATE_1000_HZ``
    """
    RATE_1_HZ = 0b0000     # 1 Hz
    RATE_1_95_HZ = 0b0001  # 1.95 Hz
    RATE_3_9_HZ = 0b0010   # 3.9 Hz
    RATE_7_81_HZ = 0b0011  # 7.81 Hz
    RATE_15_63_HZ = 0b0100 # 15.63 Hz
    RATE_31_25_HZ = 0b0101 # 31.25 Hz
    RATE_62_5_HZ = 0b0110  # 62.5 Hz
    RATE_125_HZ = 0b0111   # 125 Hz
    RATE_250_HZ = 0b1000   # 250 Hz
    RATE_500_HZ = 0b1001   # 500 Hz
    RATE_1000_HZ = 0b1010  # 1000 Hz

class BandWidth: # pylint: disable=too-few-public-methods
    """An enum-like class representing the different bandwidths that the MSA301 can
    use. The values can be referenced like ``BandWidth.WIDTH_1_HZ`` or ``BandWidth.RATE_500_HZ``
    Possible values are

    - ``BandWidth.RATE_1_HZ``
    - ``BandWidth.RATE_1_95_HZ``
    - ``BandWidth.RATE_3_9_HZ``
    - ``BandWidth.RATE_7_81_HZ``
    - ``BandWidth.RATE_15_63_HZ``
    - ``BandWidth.RATE_31_25_HZ``
    - ``BandWidth.RATE_62_5_HZ``
    - ``BandWidth.RATE_125_HZ``
    - ``BandWidth.RATE_250_HZ``
    - ``BandWidth.RATE_500_HZ``
    - ``BandWidth.RATE_1000_HZ``
    """
    WIDTH_1_95_HZ = 0b0000  # 1.95 Hz
    WIDTH_3_9_HZ = 0b0011   # 3.9 Hz
    WIDTH_7_81_HZ = 0b0100  # 7.81 Hz
    WIDTH_15_63_HZ = 0b0101 # 15.63 Hz
    WIDTH_31_25_HZ = 0b0110 # 31.25 Hz
    WIDTH_62_5_HZ = 0b0111  # 62.5 Hz
    WIDTH_125_HZ = 0b1000   # 125 Hz
    WIDTH_250_HZ = 0b1001   # 250 Hz
    WIDTH_500_HZ = 0b1010   # 500 Hz

class Range: # pylint: disable=too-few-public-methods
    """An enum-like class representing the different acceleration measurement ranges that the
    MSA301 can use. The values can be referenced like ``Range.RANGE_2_G`` or ``Range.RANGE_16_G``
    Possible values are

    - ``Range.RANGE_2_G``
    - ``Range.RANGE_4_G``
    - ``Range.RANGE_8_G``
    - ``Range.RANGE_16_G``
    """
    RANGE_2_G = 0b00  # +/- 2g (default value)
    RANGE_4_G = 0b01  # +/- 4g
    RANGE_8_G = 0b10  # +/- 8g
    RANGE_16_G = 0b11 # +/- 16g

class Resolution: # pylint: disable=too-few-public-methods
    """An enum-like class representing the different measurement ranges that the MSA301 can
    use. The values can be referenced like ``Range.RANGE_2_G`` or ``Range.RANGE_16_G``
    Possible values are

    - ``Resolution.RESOLUTION_14_BIT``
    - ``Resolution.RESOLUTION_12_BIT``
    - ``Resolution.RESOLUTION_10_BIT``
    - ``Resolution.RESOLUTION_8_BIT``
    """
    RESOLUTION_14_BIT = 0b00
    RESOLUTION_12_BIT = 0b01
    RESOLUTION_10_BIT = 0b10
    RESOLUTION_8_BIT = 0b11

class MSA301:
    """Driver for the MSA301 Accelerometer.

        :param ~busio.I2C i2c_bus: The I2C bus the MSA is connected to.
    """
    _part_id = ROUnaryStruct(_MSA301_REG_PARTID, "<B")

    def __init__(self, i2c_bus):
        self.i2c_device = i2cdevice.I2CDevice(i2c_bus, _MSA301_I2CADDR_DEFAULT)

        if self._part_id != 0x13:
            raise AttributeError("Cannot find a MSA301")


        self._disable_x = self._disable_y = self._disable_z = False
        self.power_mode = Mode.NORMAL
        self.data_rate = DataRate.RATE_500_HZ
        self.bandwidth = BandWidth.WIDTH_250_HZ
        self.range = Range.RANGE_4_G
        self.resolution = Resolution.RESOLUTION_14_BIT



    _disable_x = RWBit(_MSA301_REG_ODR, 7)
    _disable_y = RWBit(_MSA301_REG_ODR, 6)
    _disable_z = RWBit(_MSA301_REG_ODR, 5)

    _xyz_raw = ROBits(48, _MSA301_REG_OUT_X_L, 0, 6)

    power_mode = RWBits(2, _MSA301_REG_POWERMODE, 6)

    bandwidth = RWBits(4, _MSA301_REG_POWERMODE, 1)

    data_rate = RWBits(4, _MSA301_REG_ODR, 0)

    range = RWBits(2, _MSA301_REG_RESRANGE, 0)

    resolution = RWBits(2, _MSA301_REG_RESRANGE, 2)

    @property
    def acceleration(self):
        """The x, y, z acceleration values returned in a 3-tuple and are in m / s ^ 2."""
        # read the 6 bytes of acceleration data
        # zh, zl, yh, yl, xh, xl
        raw_data = self._xyz_raw
        acc_bytes = bytearray()
        # shift out bytes, reversing the order
        for shift in range(6):
            bottom_byte = (raw_data >>(8*shift) & 0xFF)
            acc_bytes.append(bottom_byte)

        # unpack three LE, signed shorts
        x, y, z = struct.unpack_from("<hhh", acc_bytes)

        current_range = self.range
        scale = 1.0
        if current_range == 3:
            scale = 512.0
        if current_range == 2:
            scale = 1024.0
        if current_range == 1:
            scale = 2048.0
        if current_range == 0:
            scale = 4096.0

        # shift down to the actual 14 bits and scale based on the range
        x_acc = ((x>>2) / scale) * _STANDARD_GRAVITY
        y_acc = ((y>>2) / scale) * _STANDARD_GRAVITY
        z_acc = ((z>>2) / scale) * _STANDARD_GRAVITY

        return (x_acc, y_acc, z_acc)
