# /usr/bin/env

from satp_serial import MiotySerialSATP as SSATP
from satp_serial import int2hex4list
import time
import argparse
import platform

BAUDRATE = 115200

if platform.system() == "Windows":
    PORT_DEFAULT = "COM6"
else:
    PORT_DEFAULT = "/dev/ttyACM1"

class MiotySensor:
    def __init__(self, baudarte, port):
        self.satp = SSATP(baudarte, port)
        self.separator = "\n>   "

    def initialize(self, nwkkey):
        print(self.separator, end="")
        print("SATP_STACK_SELECT_STACK <- E_STACK_ID_MIOTY: ", end="")
        self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SELECT_STACK, [SSATP.E_STACK_ID_MIOTY])
        print(self.separator, end="")
        print(
            "SATP_STACK_SET <- E_STACK_PARAM_ID_MIOTY_NWKKEY <- {}: ".format(nwkkey),
            end="",
        )
        self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SET, [SSATP.E_STACK_PARAM_ID_MIOTY_NWKKEY] + self.hex_string2list(nwkkey))
        print(self.separator, end="")
        print("SATP_STACK_GET <- E_STACK_PARAM_ID_MIOTY_EUI64: ", end="")
        eui = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_GET, [SSATP.E_STACK_PARAM_ID_MIOTY_EUI64])
        if eui:
            print(
                "      ⨽ EUI64: {}".format(
                    "-".join(
                        int2hex4list(
                            eui,
                            without_0x=True,
                        )
                    )
                )
            )
        print(self.separator, end="")
        print("SATP_STACK_GET <- E_STACK_PARAM_ID_MIOTY_SHORT_ADDR: ", end="")
        short_addr = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_GET, [SSATP.E_STACK_PARAM_ID_MIOTY_SHORT_ADDR])
        if short_addr:
            print(
                "      ⨽ SHORT_ADDR: {}".format(
                    "".join(
                        int2hex4list(
                            short_addr,
                            without_0x=True,
                        )
                    )
                )
            )

    def send_data(self, data, timeout, period, save_data):
        if type(data) == bool:
            data = None
            print("READING FROM FILE: ", end="")
            try:
                with open("data", "r") as data_file:
                    data = data_file.readline()
                    if data[len(data) - 1] == "\n":
                        data = data[:-1]
                    if data:
                        print("OK")
                    else:
                        print("DATA NOT FOUND")
            except Exception as e:
                print(type(e).__name__)

        if data:
            print(self.separator, end="")
            print(
                "SATP_STACK_SEND_PARAMS <- E_STACK_SEND_PARAM_ID_MIOTY_RX_WINDOW <- 0x01: ",
                end="",
            )
            self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SEND_PARAMS, [SSATP.E_STACK_SEND_PARAM_ID_MIOTY_RX_WINDOW, 0x01])
            
            print(self.separator, end="")
            print(
                "SATP_STACK_NB_SEND <- {}: ".format(data),
                end="",
            )
            self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_NB_SEND, self.hex_string2list(data))
            
            if timeout>0:
                print(self.separator, end="")
                print(
                    "WAITING_FOR_INDICATION: ",
                    end="\r",
                )

            
                chek_times = int(timeout / period)
                indication = False
                for t in range(chek_times):
                    time.sleep(period)
                    if self.satp.check_serial():
                        readed_data = self.satp.read_data()
                        for dat in readed_data:
                            if dat[3] and dat[3][0] == SSATP.E_STACK_EVENT_RX_SUCCESS:
                                indication = True
                                break
                        if indication: break
                    else:
                        print(
                            f"\r>   WAITING FOR INDICATION: [{"▮" * (t + 1)}{"-" * (chek_times - 1 - t)}] {period*t}s  ",
                            end="",
                        )
                if indication:
                    print()
                    print(self.separator, end="")
                    print("SATP_STACK_RECEIVE: ", end="")
                    received_data = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_RECEIVE)
                    if received_data:
                        print(
                            "      ⨽ DATA: {}".format(
                                ", ".join(
                                    int2hex4list(received_data)
                                )
                            )
                        )
                        if save_data:
                            with open("data", "w") as data_file:
                                data_file.write("".join(int2hex4list(received_data, without_0x=True)))
                                print(
                                    "          ⨽ WRITING TO FILE: OK"
                                )
                else:
                    print(f"\r>   WAITING FOR INDICATION: TIMEOUT      " + " "*chek_times)

    def get_set_params(self, tx_power, mioty_mode, mioty_profile):
        if tx_power != None:
            if type(tx_power) == bool:
                print(self.separator, end="")
                print("SATP_STACK_GET <- E_STACK_PARAM_ID_MIOTY_TX_POWER: ", end="")
                u_tx_power_value = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_GET, [SSATP.E_STACK_PARAM_ID_MIOTY_TX_POWER])[0]
                if u_tx_power_value:
                    if u_tx_power_value>127:
                        s_tx_power_value = u_tx_power_value-256
                    else:
                        s_tx_power_value = u_tx_power_value
                    print(
                        "      ⨽ TX_POWER: {} ({})".format(
                            s_tx_power_value, hex(u_tx_power_value)
                        )
                    )
            else:
                print(self.separator, end="")
                print(
                    "SATP_STACK_SET <- E_STACK_PARAM_ID_MIOTY_TX_POWER <- {}: ".format(
                        hex(tx_power)
                    ),
                    end="",
                )
                self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SET, [SSATP.E_STACK_PARAM_ID_MIOTY_TX_POWER, tx_power])

        if mioty_mode != None:
            if type(mioty_mode) == bool:
                print(self.separator, end="")
                print("SATP_STACK_GET <- E_STACK_PARAM_ID_MIOTY_MODE: ", end="")
                mioty_mode_value = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_GET, [SSATP.E_STACK_PARAM_ID_MIOTY_MODE])
                if mioty_mode_value:
                    print(
                        "      ⨽ MIOTY_MODE: {} ({})".format(
                            mioty_mode_value[0], hex(mioty_mode_value[0])
                        )
                    )
            else:
                print(self.separator, end="")
                print(
                    "SATP_STACK_SET <- E_STACK_PARAM_ID_MIOTY_MODE <- {}: ".format(
                        hex(mioty_mode)
                    ),
                    end="",
                )
                self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SET, [SSATP.E_STACK_PARAM_ID_MIOTY_MODE, mioty_mode])

        if mioty_profile != None:
            if type(mioty_profile) == bool:
                print(self.separator, end="")
                print("SATP_STACK_GET <- E_STACK_PARAM_ID_MIOTY_PROFILE: ", end="")
                mioty_profile_value = self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_GET, [SSATP.E_STACK_PARAM_ID_MIOTY_PROFILE])
                if mioty_profile_value:
                    print(
                        "      ⨽ MIOTY_PROFILE: {} ({})".format(
                            mioty_profile_value[0], hex(mioty_profile_value[0])
                        )
                    )
            else:
                print(self.separator, end="")
                print(
                    "SATP_STACK_SET <- E_STACK_PARAM_ID_MIOTY_PROFILE <- {}: ".format(
                        hex(mioty_profile)
                    ),
                    end="",
                )
                self._send_with_confirmation(SSATP.API_SATP_STACK_CMD, SSATP.SATP_STACK_SET, [SSATP.E_STACK_PARAM_ID_MIOTY_PROFILE, mioty_profile])

    def _send_with_confirmation(self, api_id, comand_id, parameter = []):
        self.satp.send_data(api_id, comand_id, parameter)
        time.sleep(0.5)
        payload = self.satp.read_data()
        if payload[0][2] == 0:
            print("OK")
            return payload[0][3]
        else:
            print("ERROR")
            print("      ⨽ ERROR_CODE = {}".format(payload[0][3][0]))

    def hex_string2list(self, string):
        string = string.replace("-", "")

        return [int(string[x * 2 : x * 2 + 2], 16) for x in range(int(len(string) / 2))]


def NetworkKey(key):
    if len(key) == 32:
        return key
    else:
        raise argparse.ArgumentTypeError("Network key must be 32 characters long")


def SignedByte(vlaue):
    if vlaue[0:2] == "0x":
        byte = int(vlaue, 16)
        if byte < 0 or byte > 255:
            raise argparse.ArgumentTypeError("byte must be in range [0x00, 0xff]")
    elif vlaue[0:2] == "0b":
        byte = int(vlaue, 2)
        if byte < 0 or byte > 255:
            raise argparse.ArgumentTypeError(
                "byte must be in range [0b00000000, 0b11111111]"
            )
    else:
        byte = int(vlaue)
        if byte < -128 or byte > 127:
            raise argparse.ArgumentTypeError("byte must be in range [-128, +127]")
        if byte < 0:
            byte = (byte & 0xFF) | 0x80

    return byte


def MiotyProfile(value):
    modes = ["eu0", "eu1", "eu2", "us0"]

    str_value = str(value).lower()

    if str_value in modes:
        return modes.index(str_value)
    else:
        byte = SignedByte(value)
        if byte >= 0 and byte < 4:
            return byte
        else:
            raise argparse.ArgumentTypeError("profile index must be in range [0, 3]")


def MiotyMode(value):
    byte = SignedByte(value)
    if byte >= 0 and byte < 3:
        return byte
    else:
        raise argparse.ArgumentTypeError("mode index must be in range [0, 2]")

def ComPort(value):
    if value[:5] == "/dev/":
        return value
    value = value.upper()
    if value[:3] == "COM":
        if value[3:].isdigit():
            return value
    if value.isdigit():
        return "COM"+str(value)
    raise argparse.ArgumentTypeError("invalid port name")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port",
        type=ComPort,
        required=False
    )

    subparses = parser.add_subparsers(dest="function", required=True)

    parser_init = subparses.add_parser("init")
    parser_init.add_argument("networkKey", type=NetworkKey)
    parser_init.add_argument(
        "--txPower",
        nargs="?",
        type=SignedByte,
        required=False,
        const=True,
    )
    parser_init.add_argument(
        "--miotyMode",
        nargs="?",
        type=MiotyMode,
        required=False,
        const=True,
    )
    parser_init.add_argument(
        "--miotyProfile",
        nargs="?",
        type=MiotyProfile,
        required=False,
        const=True,
    )

    parser_send = subparses.add_parser("send")
    parser_send.add_argument("--data", nargs="?", type=str, required=True, const=True,)
    parser_send.add_argument("-t", "--timeout", type=float, required=False, default=30,)
    parser_send.add_argument("-p", "--period", type=float, required=False, default=0.5,)
    parser_send.add_argument("-ld", "--load_data",
        required=False,
        action="store_true",
    )
    parser_send.add_argument("-sd", "--save_data",
        required=False,
        action="store_true",
    )
    
    parser_params = subparses.add_parser("params")

    parser_params.add_argument(
        "--txPower",
        nargs="?",
        type=SignedByte,
        required=False,
        const=True,
    )
    parser_params.add_argument(
        "--miotyMode",
        nargs="?",
        type=MiotyMode,
        required=False,
        const=True,
    )
    parser_params.add_argument(
        "--miotyProfile",
        nargs="?",
        type=MiotyProfile,
        required=False,
        const=True,
    )

    console_args = parser.parse_args()

    if console_args.port:
        PORT = console_args.port
    else: PORT = PORT_DEFAULT

    #print(console_args)

    sensor = MiotySensor(BAUDRATE, PORT)

    if console_args.function == "init":
        sensor.initialize(console_args.networkKey)
        sensor.get_set_params(
            console_args.txPower,
            console_args.miotyMode,
            console_args.miotyProfile,
        )
    elif console_args.function == "send":
        sensor.send_data(console_args.data, console_args.timeout, console_args.period, console_args.save_data)
    elif console_args.function == "params":
        sensor.get_set_params(
            console_args.txPower,
            console_args.miotyMode,
            console_args.miotyProfile,
        )
