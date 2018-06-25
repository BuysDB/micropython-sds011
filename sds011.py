"""
Reading format. See http://cl.ly/ekot

0 Header   '\xaa'
1 Command  '\xc0'
2 DATA1    PM2.5 Low byte
3 DATA2    PM2.5 High byte
4 DATA3    PM10 Low byte
5 DATA4    PM10 High byte
6 DATA5    ID byte 1
7 DATA6    ID byte 2
8 Checksum Low byte of sum of DATA bytes
9 Tail     '\xab'

"""

import ustruct as struct
import sys
import utime as time

_SDS011_CMDS = {'SET': b'\x01',
        'GET': b'\x00',
        'QUERY': b'\x04',
        'REPORTING_MODE': b'\x02',
        'DUTYCYCLE': b'\x08',
        'SLEEPWAKE': b'\x06'}

class SDS011:
    def __init__(self, uart):
        self._uart = uart
        self._pm25 = 0.0
        self._pm10 = 0.0
        self._packet_status = ''
        self._packet = ()

        self.set_reporting_mode_query()

    @property
    def pm25(self):
        return self._pm25

    @property
    def pm10(self):
        return self._pm10

    @property
    def packet_status(self):
        return self._packet_status

    @property
    def packet(self):
        return self._packet

    def make_command(self, cmd, mode, param):
        header = b'\xaa\xb4'
        padding = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'
        checksum = chr(( ord(cmd) + ord(mode) + ord(param) + 255 + 255) % 256)
        checksum = bytes(checksum, 'utf8')
        tail = b'\xab'

        return header + cmd + mode + param + padding + checksum + tail

    #Sends wake command to sds011
    def wake(self):
        cmd = self.make_command(_SDS011_CMDS['SLEEPWAKE'],
                _SDS011_CMDS['SET'], chr(1))
        self._uart.write(cmd)

    #Sends sleep command to sds011
    def sleep(self):
        cmd = self.make_command(_SDS011_CMDS['SLEEPWAKE'],
                _SDS011_CMDS['SET'], chr(0))
        self._uart.write(cmd)

    def set_reporting_mode_query(self):
        cmd = self.make_command(_SDS011_CMDS['REPORTING_MODE'],
                _SDS011_CMDS['SET'], chr(1))
        self._uart.write(cmd)

    #Query new measurement data
    def query(self):
        cmd = self.make_command(_SDS011_CMDS['QUERY'], chr(0), chr(0))
        self._uart.write(cmd)

    def process_measurement(self, packet):
        try:
            *data, checksum, tail = struct.unpack('<HHBBBs', packet)
            self._pm25 = data[0]/10.0
            self._pm10 = data[1]/10.0
            checksum_OK = (checksum == (sum(data) % 256))
            tail_OK = tail == b'\xab'
            self._packet_status = 'OK' if (checksum_OK and tail_OK) else 'NOK'
        except Exception as e:
            print('Problem decoding packet:', e)
            sys.print_exception(e)

    def read(self):
        #Query measurement
        self.query()

        #Read measurement
        #Drops up to 512 bits before giving up finding a measurement pkt...
        for i in range(512):
            try:
                header = self._uart.read(1)
                if header == b'\xaa':
                    command = self._uart.read(1)

                    if command == b'\xc0':
                        packet = self._uart.read(8)
                        if packet != None:
                            self.process_measurement(packet)
                            return 'OK'
            except Exception as e:
                print('Problem attempting to read:', e)
                sys.print_exception(e)

        #If we gave up finding a measurement pkt
        return 'NOK'
