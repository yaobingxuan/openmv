# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Image Transfer - As The Remote Device
#
# This script is meant to talk to the "image_transfer_jpg_streaming_as_the_controller_device.py" on your computer.
#
# This script shows off how to transfer the frame buffer to your computer as a jpeg image.

import omv
import rpc
import sensor

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Turn off the frame buffer connection to the IDE from the OpenMV Cam side.
#
# This needs to be done when manually compressing jpeg images at higher quality
# so that the OpenMV Cam does not try to stream them to the IDE using a fall back
# mechanism if the JPEG image is too large to fit in the IDE JPEG frame buffer on the OpenMV Cam.

omv.disable_fb(True)

# The RPC library above is installed on your OpenMV Cam and provides multiple classes for
# allowing your OpenMV Cam to be controlled over USB or LAN/WLAN.

################################################################
# Choose the interface you wish to control your OpenMV Cam over.
################################################################

# Uncomment the below line to setup your OpenMV Cam for control over a USB VCP.
#
interface = rpc.rpc_usb_vcp_slave()

# Uncomment the below line to setup your OpenMV Cam for control over the lan.
#
# import network
# network_if = network.LAN()
# network_if.active(True)
# network_if.ifconfig('dhcp')
#
# interface = rpc.rpc_network_slave(network_if)

# Uncomment the below line to setup your OpenMV Cam for control over the wlan.
#
# import network
# network_if = network.WLAN(network.STA_IF)
# network_if.active(True)
# network_if.connect('your-ssid', 'your-password')
#
# interface = rpc.rpc_network_slave(network_if)

################################################################
# Call Backs
################################################################


# This is called repeatedly by interface.stream_writer().
def stream_generator_cb():
    img = sensor.snapshot()
    img.to_jpeg(quality=90)
    return img.bytearray()


# Transmits a stream of bytes()'s generated by stream_generator_cb to the master device.
def jpeg_image_stream_cb():
    interface.stream_writer(stream_generator_cb)


# When called sets the pixformat and framesize, and then schedules
# frame streaming to start after the RPC call finishes.
#
# data is a pixformat string and framesize string.
def jpeg_image_stream(data):
    pixformat, framesize = bytes(data).decode().split(",")
    sensor.set_pixformat(eval(pixformat))
    sensor.set_framesize(eval(framesize))
    interface.schedule_callback(jpeg_image_stream_cb)
    return bytes()


# Register call backs.

interface.register_callback(jpeg_image_stream)

# Once all call backs have been registered we can start
# processing remote events. interface.loop() does not return.

interface.loop()
