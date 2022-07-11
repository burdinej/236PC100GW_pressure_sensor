#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, sys
import datetime as dt
import DMM_34401a as dmm
import argparse

DEFAULT_DEV = '/dev/tty.usbserial-FTUB1YBZ'

class ArgumentError(Exception):
    def __init__(self,message):
        self.msg = "Error with argument: %s" % str(message)
    def __str__(self):
        return self.msg

class ID_Error(Exception):
    def __init__(self,message):
        self.msg = "Communication Error: %s" % str(message)
    def __str__(self):
        return self.msg


def main():
    # Setup arg parse #
    par = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)   
    par.add_argument("devfile", metavar="DEVFILE", type=str, default=DEFAULT_DEV, help=f"The devfile path to locate usb device for serial. default={DEFAULT_DEV}")
    par.add_argument("--rate", "-r", metavar="RATE", type=float, default = 600.0, help="Set the rate data is collected at in seconds (i.e. log data point once every X seconds). Default is 600.0s (10 minutes).") 
    par.add_argument("--log_file", "-f", metavar='FILE', type=str, default = 'data.txt', help="Path for the file you want to use or create to log data. Default='data.txt'")
    args = par.parse_args()

    # Do arg parse error checking #
    if (args.rate < 5):
        raise ArgumentError('Data collection rate must be no faster than once every 10 seconds. Enter a rate >= 10s.')
        sys.exit()

    # initialize DMM (HP 34401A) #
    dmm_dev  = dmm.DMM_init(args.devfile)
    time.sleep(1)
    ID_check = dmm.DMM_ID_CHECK(dmm_dev)
    time.sleep(1)

    if "34401A" in ID_check:
        print("DMM confirmed it is 34401A")
    else:
        raise ID_Error('DMM could not confirm it is a HP 34401A. Please diagnose!')
        sys.exit()
    print("DMM is ready!")
    
    
    # Start logging data #  
    with open(args.log_file, 'a') as file: 
        file.write('# Datetime\t\t\t\tV_Outputs Diff [V]\tPressure [psi-gauge]\n')
        try: 
            while True: 
                v_diff = 1000 * read(dmm_dev)
                print(v_diff) 
                pres = conv_v_2_press(v_diff)
                print(pres)
                t = time.strftime("%Y-%m-%d-%H:%M:%S")
                os.system('clear')
                sys.stdout.write('\033[1;1h') # reset cursor
                print(f'logging to {args.log_file}. press ctrl+c to stop\n')
                print('Datetime\t\tV_Outputs Diff [V]\tPressure [psi-gauge]')
                print(f"{t}\t{v_diff:.6f}\t\t{pres:.6f}\n")  
                file.write(f"{t}\t\t{v_diff:.6f}\t\t\t{pres:.6f}\n")
                time.sleep(args.rate)  
        except KeyboardInterrupt:
            print('\nkeyboardinterrupt. \n\nlogging stopped. please wait while DMM connection closes...')
        except Exception as e:
            print(e)
            sys.exit()
        finally:
            close(dmm_dev)

def read(dmm_dev):
    v_diff = float((dmm.DMM_read_raw(dmm_dev)).decode())
    return v_diff

def conv_v_2_press(volt):
    # This conversion was experimentally determined, and converts to psi gauge
    pressure = (-1.064 * volt) - 0.1878
    return pressure

def close(dmm_dev):
    dmm.DMM_close(dmm_dev)


if __name__ == "__main__":
    main()



