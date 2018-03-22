#!/usr/bin/env python
# -*- coding: utf-8 -*-
# THIS PROGRAM IS INTENDED TO TAKE RANGE MEASUREMENTS FROM THE LIDAR-LITE V3 SENSOR THROUGH
# AN UM232H MPSSE I2C-USB INTERFACE DEVICE.
# THE USED LIBRARY COMES FROM ADAFRUIT: https://learn.adafruit.com/adafruit-ft232h-breakout/i2c

import rospy
import Adafruit_GPIO.FT232H as FT232H
from sensor_msgs.msg import Range
from std_msgs.msg import Float32
 
# Temporarily disable FTDI serial drivers.
FT232H.use_FT232H()
 
# Find the first FT232H device.
ft232h = FT232H.FT232H()
print(ft232h)
# Create an I2C device at address 0x62.
global i2c
i2c = FT232H.I2CDevice(ft232h, 0x62)
i2c.write8(0x00, 0x00)

# High range configuration
#i2c.write8(0x02, 0xff)
#i2c.write8(0x04, 0x08)
#i2c.write8(0x1c, 0x00)

#global bias_corr
#bias_corr = 100


def measurement_callback(event):
	global i2c
	#global bias_corr

	### BIAS CORRECTION: This is ommited in this code because
	### it was not working properly with our lidar.
	#if(bias_corr == 100):
	#	# Use reciever bias correction
	#	i2c.write8(0x00, 0x04)
	#	bias_corr = 0
	#elif(bias_corr == 1):
	#	# Do not use receiver bias correction
	#	i2c.write8(0x00,0x03)

	# Advertise the measurement process to the slave
	i2c.write8(0x00, 0x04)
	# Wait until device is ready (LSB = 0)
	response = i2c.readU8(0x01)
	while(response & 0 != 0):
		response = i2c.readU8(0x01)
		pass

	# Measure the altitude
	responseH = i2c.readU8(0x0f)
	responseL = i2c.readU8(0x10)
	altitude = (responseL+256.0*responseH)/100.0 # In meters

	msg = Float32()
	#print altitude
	msg.data = altitude
	#msg.header = data.header
	altitude_pub.publish(msg)
	#bias_corr += 1

def main():
	rospy.spin()

if __name__ == '__main__':
	rospy.init_node('altitude_measurement')
	altitude_topic = rospy.get_param('altitude_topic', '/use_robot/lidarlite_range')
	fs = 100.0;
	callback_period = rospy.Duration(1/fs)
	altitude_pub = rospy.Publisher(altitude_topic, Float32, queue_size=1)
	rospy.Timer(callback_period,measurement_callback)
	try:
		main()
	except rospy.ROSInterruptException:
		pass


### TODO: Implement different configurations. This arduino code can be taken as an example
# void LIDARLite::configure(int configuration, char lidarliteAddress)
# {
#   switch (configuration)
#   {
#     case 0: // Default mode, balanced performance
#       write(0x02,0x80,lidarliteAddress); // Default
#       write(0x04,0x08,lidarliteAddress); // Default
#       write(0x1c,0x00,lidarliteAddress); // Default
#     break;

#     case 1: // Short range, high speed
#       write(0x02,0x1d,lidarliteAddress);
#       write(0x04,0x08,lidarliteAddress); // Default
#       write(0x1c,0x00,lidarliteAddress); // Default
#     break;

#     case 2: // Default range, higher speed short range
#       write(0x02,0x80,lidarliteAddress); // Default
#       write(0x04,0x00,lidarliteAddress);
#       write(0x1c,0x00,lidarliteAddress); // Default
#     break;

#     case 3: // Maximum range
#       write(0x02,0xff,lidarliteAddress);
#       write(0x04,0x08,lidarliteAddress); // Default
#       write(0x1c,0x00,lidarliteAddress); // Default
#     break;

#     case 4: // High sensitivity detection, high erroneous measurements
#       write(0x02,0x80,lidarliteAddress); // Default
#       write(0x04,0x08,lidarliteAddress); // Default
#       write(0x1c,0x80,lidarliteAddress);
#     break;

#     case 5: // Low sensitivity detection, low erroneous measurements
#       write(0x02,0x80,lidarliteAddress); // Default
#       write(0x04,0x08,lidarliteAddress); // Default
#       write(0x1c,0xb0,lidarliteAddress);
#     break;
#   }
# } /* LIDARLite::configure */
