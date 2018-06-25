Introduction
============

A MicroPython driver for the SDS011 particle sensor (PM10 and PM25). This sensor
uses serial communication.

Installation
=============

On a LoPy, just put ``sds011.py`` in the ``lib/`` directory.

Usage Notes
=============

First, import the library:

.. code-block:: python

    import sds011

Next, initialize a UART object (here P21 in TX and P22 is RX):

.. code-block:: python

	uart = UART(1, baudrate=9600, pins=('P21','P22'))


Since we have the UART bus object, we can now use it to instantiate the SDS011 object:

.. code-block:: python

	dust_sensor = sds011.SDS011(uart)

Reading from the Sensor
------------------------

To read from the sensor:

.. code-block:: python

    dust_sensor.read()
	print('PM25: ', dust_sensor.pm25)
	print('PM10: ', dust_sensor.pm10)
