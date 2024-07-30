# /usr/bin/env

import serial
import time


class MiotySerialSATP:
    def __init__(self, baudrate, port):
        self.serial = serial.Serial()

        self.serial.baudrate = baudrate
        self.serial.port = port

        self.serial.open()

    def send_data(self, api_id, command_id, parameter=[]):
        data = bytearray(
            self._pack_data(
                api_id,
                command_id,
                parameter,
            )
        )

        self.serial.write(data)

    def check_serial(self):
        return self.serial.inWaiting()

    def read_data(self):
        received_data = []
        messages = []

        while self.serial.inWaiting() > 0:
            data = self.serial.read(1)

            if data != "":
                received_data.append(data[0])

        # print(received_data)

        read_next = True
        shift = 0
        if received_data:
            while read_next:
                message = self._unpack_data(received_data[shift:])
                messages.append(message[1:])

                # print(message)

                if message and message[0]:
                    shift += message[0]
                    if shift >= len(received_data):
                        read_next = False
                else:
                    read_next = False

        return messages

    def _calc_crc(self, data) -> tuple:
        crc_pol = 0x3D65

        reg = 0

        if len(data) > 0:
            reg = data[0] << 8
            if len(data) > 1:
                reg += data[1]

        for next_byte in data[2:]:
            for b_i in range(8):
                reg_Hb = reg >> 15
                reg = (reg << 1) & 0xFFFF
                reg += (next_byte >> 7) & 1
                next_byte <<= 1
                if reg_Hb:
                    reg ^= crc_pol

        for b_i in range(16):
            reg_Hb = reg >> 15
            reg = (reg << 1) & 0xFFFF
            if reg_Hb:
                reg ^= crc_pol

        crc_H = int(reg / 256)
        crc_L = reg % 256

        return (~crc_H) & 0xFF, (~crc_L) & 0xFF

    def _pack_data(self, api_id, comand_id, parameter):
        length = 3 + len(parameter)

        l_H = int(length / 256)
        l_L = length % 256

        payload = [0x07, api_id, comand_id] + parameter

        crc_H, crc_L = self._calc_crc(payload)

        return [0xA5, l_H, l_L, (~l_H) & 0xFF, (~l_L) & 0xFF] + payload + [crc_H, crc_L]

    def _unpack_data(self, data):
        if data[0] == 165:
            if len(data) > 6:
                length = data[1] * 256 + data[2]
                if length == 256 * ((~data[3]) & 0xFF) + ((~data[4]) & 0xFF):
                    if len(data) >= 7 + length:
                        payload = data[5 : 5 + length]
                        message_len = 7 + length
                    else:
                        print("SIZE ERROR [2]")
                        return
                else:
                    print("ERROR: data is corrupted")
                    return
            else:
                print("SIZE ERROR [1]")
                return
        else:
            print("SYNC BYTE ERROR")
            return

        crc_H, crc_L = self._calc_crc(payload)

        if data[length + 5] == crc_H and data[length + 6] == crc_L:
            if len(payload) > 2:
                stack_id = payload[0]
                api_id = payload[1]
                command = payload[2]
                parameter = None
                if len(payload) > 3:
                    parameter = payload[3:]

                return message_len, stack_id, api_id, command, parameter
            else:
                print("SATP SIZE ERROR")
                return message_len, None, None, None
        else:
            print("CRC ERROR")
            return message_len, None, None, None


def int2hex4list(int_list, without_0x=False):
    hex_list = []

    for el in int_list:
        hex_form = hex(el)[2:]

        if len(hex_form) == 1:
            hex_form = "0" + hex_form

        if not without_0x:
            hex_form = "0x" + hex_form

        hex_list.append(hex_form)

    return hex_list


if __name__ == "__main__":
    satp = MiotySerialSATP(115200, "COM6")

    satp.send_data(
        0x00,
        0x03,
        [
            0x62,
        ],
    )

    time.sleep(1)

    unpacked_data = satp.read_data()
    print(unpacked_data)

    """ if unpacked_data:
        print(unpacked_data)
        if unpacked_data[3]:
            print(int2hex4list(unpacked_data[3])) """