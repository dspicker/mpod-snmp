"""
This module provides functions to steer an iseg HV module inside a Wiener-MPOD.

Created by Dennis Spicker 2025
"""
import subprocess

SNMP_HOST = "141.2.243.129 "
""" The IP address of the MPOD """

SNMP_BULK_OPTIONS = "-Cr8 -Ov -OU -OQ "
"""
-Cr8: Bulk-read 8 repeating variables (currently 8 HV channels).  
-Ov:  Display the varbind value only, not the OID.  
-OU:  Do not print the UNITS suffix at the end of the value.  
-OQ:  Removes the type information when displaying varbind values.
"""

SNMP_PRECISION = "-Op +020.12 "
"""
-Op PRECISION
    Uses the PRECISION string to allow modification of the value output format.
    This is used with OPAQUE float/double at the moment, but might be usabe for 
    other types in the future. Allowed PRECISION strings are compatible to the
    flag/field with/precision part of the printf(3) function:

        `$ snmpget localhost outputVoltage.1`
        WIENER-CRATE-MIB:: outputVoltage.u0 = Opaque: Float: 0.000000 V

        `$ snmpget -Op +020.12 localhost outputVoltage.1`
        WIENER-CRATE-MIB:: outputVoltage.u0 = Opaque: Float: +000000.000000000000 V
"""

SNMP_OPTIONS = "-v 2c -m +WIENER-CRATE-MIB "
"""
-v 2c: Use snmp protocol version 2c  
-m:    Which MIB file to use. Make sure the file is in /usr/share/snmp/mibs/
"""

SNMP_COMM_READ = "-c public "
SNMP_COMM_WRITE = "-c guru "

HV_MODULE_OID = ".500"
HV_CHANNELS_OIDS = [".501", ".502", ".503", ".504", ".505", ".506", ".507", ".508"]

volt_on      = [100.0] * 8   # 100 V, channel on
volt_standby = [1000.0] * 8  # 1000 V, detector standby
volt_amp1    = [1600.0] * 8  # 1600 V, onset of amplification
volt_amp2    = [1750.0] * 8

DEBUG = False

#"snmpbulkget -Cr8 -Ov -OU -OQ -v 2c -m +WIENER-CRATE-MIB -c public 141.2.243.129 outputVoltage.500"


def snmp_command(command: list[str]):
    """Execute snmp command in the shell. Internal use only.

    Args:
        command (list[str]): The complete snmp bash command. 
        E.g. to get all preset output voltages:
        `$ snmpbulkget -Cr8 -Ov -OU -OQ -v 2c -m +WIENER-CRATE-MIB -c public 
        141.2.243.129 outputVoltage.500`

    Returns:
        subprocess.CompletedProcess: Result of the snmp query as subprocess object.
    """
    sp_result = None
    try:
        sp_result = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            check=True,
            timeout=10
            #text=True
            )
    except subprocess.CalledProcessError as exc:
        if not is_too_big_error(exc):
            print(f"Error!\n{exc}\n")
            print(exc.stderr.decode('utf-8'))
    except subprocess.TimeoutExpired as exc:
        print(f"Snmp command timed out after {exc.timeout} sec.")
    return sp_result


def is_too_big_error(exception: subprocess.CalledProcessError) -> bool:
    """Helper for snmp_command. Silences "tooBig" errors from snmp agent.

    Args:
        exception (subprocess.CalledProcessError): 

    Returns:
        bool: True if exception is a "tooBig" error
    """
    ret = False
    if exception.returncode == 2:
        if "Reason: (tooBig)" in exception.stderr.decode():
            ret = True
    return ret


def get_voltages():
    """Get preset voltages of all HV channels

    Returns:
        list[float]: The nominal output voltage of each channel
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_OPTIONS +\
               SNMP_COMM_READ + SNMP_HOST + "outputVoltage.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ float(x.decode()) for x in cmd_result.stdout.split()]
        if DEBUG:
            print(command)
            print(cmd_result.stdout.decode('utf-8'), end='')
    return result


def set_voltages(voltages: list[float]):
    """Set the voltage of each HV channel

    Args:
        voltages (list[float]): The nominal output voltage of each channel
    """
    for i, x in enumerate(voltages):
        if i >= len(HV_CHANNELS_OIDS):
            break
        chan = HV_CHANNELS_OIDS[i]
        voltage = str(x)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + "outputVoltage"\
                   + chan + " F " + voltage]
        cmd_result = snmp_command(command)
        if DEBUG:
            print(command)
            if cmd_result:
                print(cmd_result.stdout.decode('utf-8'), end='')


def get_currents():
    """Get current limit of all HV channels

    Returns:
        (list[float]): The current limit of each channel in micro ampere
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_OPTIONS + SNMP_COMM_READ + SNMP_HOST\
               + "outputCurrent.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ (float(x.decode()) * 1e6) for x in cmd_result.stdout.split()]
    return result


def set_currents(currents: list[float]):
    """Set the channel current limit of each HV channel

    Args:
        currents (list[float]): The current limit of each channel in micro ampere
    """
    for i, x in enumerate(currents):
        if i >= len(HV_CHANNELS_OIDS):
            break
        chan = HV_CHANNELS_OIDS[i]
        current = str(x * 1e-6)
        print(current)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + "outputCurrent"\
                   + chan + " F " + current]
        cmd_result = snmp_command(command)
        if DEBUG:
            print(command)
            if cmd_result:
                print(cmd_result.stdout.decode('utf-8'), end='')


def get_riserate_voltage():
    """Get the voltage rise rate of all HV channels

    Returns:
        list[float]: The slew rate of each output voltage if it increases, in V/s
                    (after switch on or if the Voltage has been changed)
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_OPTIONS + SNMP_COMM_READ + SNMP_HOST \
               + "outputVoltageRiseRate.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ float(x.decode()) for x in cmd_result.stdout.split()]
    return result


def get_output_switch():
    """Get the switch state of all HV channels

    Returns:
        list[str]: An enumerated value which shows the current state of the output channel
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_OPTIONS + SNMP_COMM_READ + SNMP_HOST \
               + "outputSwitch.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ x.decode() for x in cmd_result.stdout.split() ]
    if DEBUG:
        print(command)
        if cmd_result:
            #print(cmd_result.stdout.decode('utf-8'), end='')
            debug_result = \
                [ f"Ch {i}: {x.decode()}" for i, x in enumerate(cmd_result.stdout.split())]
            for chan in debug_result: 
                print(chan)
    return result


def set_output_switch(states: list[int]):
    """Switch HV channels on or off

    Args:
        states (list[int]): 0 to switch off, 1 to switch on. 
                            E.g.: `[1,1,1,1,0,0,0,0]` to switch on the first 4 channels.

    If the write value is resetEmergencyOff (2), then the channel will
    leave the state EmergencyOff. A write of clearEvents (10) is necessary
    before the voltage can ramp up again
    """
    for i, x in enumerate(states):
        if i >= len(HV_CHANNELS_OIDS): break
        chan = HV_CHANNELS_OIDS[i]
        state = str(x)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + "outputSwitch" \
                   + chan + " i " + state]
        cmd_result = snmp_command(command)
        if DEBUG:
            print(command)
            if cmd_result:
                print(cmd_result.stdout.decode('utf-8'), end='')


def get_measured_voltages():
    """Get measured terminal voltages of all HV channels

    Returns:
        list[float]: Measured voltage of each channel in Volt
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_PRECISION + SNMP_OPTIONS \
               + SNMP_COMM_READ + SNMP_HOST + "outputMeasurementTerminalVoltage.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ float(x.decode()) for x in cmd_result.stdout.split()]
    return result


def get_measured_currents():
    """Get measured currents of all HV channels

    Returns:
        list[float]: Measured current of each channel in nano Ampere
    """
    result = None
    command = ["snmpbulkget " + SNMP_BULK_OPTIONS + SNMP_PRECISION + SNMP_OPTIONS \
               + SNMP_COMM_READ + SNMP_HOST + "outputMeasurementCurrent.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        result = [ float(x.decode()) * 1e9 for x in cmd_result.stdout.split()]
    return result
    # # Calibration values acquired at 1800 V
    # calibration = [304.46, -14.90, 161.14, 150.04, -15.25, 187.31, 44.90, 256.30]
    # calib_result = list()
    # #calib_result = [x - y for x, y in zip(result, calibration)]
    # for res, calib in zip(result, calibration) :
    #     if res < (calib + 0.5) or res < 0.0 :
    #         calib_result.append(0.0)
    #     else :
    #         calib_result.append(res)
    # return calib_result


def get_status():
    """Get status of all HV channels

    Returns:
        list[str]: Status description of each channel
    """
    result = None
    command = ["snmpbulkget " + "-Cr8 " + SNMP_OPTIONS + SNMP_COMM_READ + SNMP_HOST \
               + "outputStatus.500"]
    cmd_result = snmp_command(command)
    if cmd_result:
        #print(cmd_result.stdout)
        # result = [ x.strip().split(' ')[-1] for x in \
        #           cmd_result.stdout.decode().strip('\n').split('\n') ]
        result = cmd_result.stdout.decode().strip('\n').split('\n')
    return result


def set_mpod_basic_config():
    """Send some basic configuration values to the MPOD
    """
    num_channels = len(HV_CHANNELS_OIDS)
    voltage_rise_rate = [40.0]*num_channels # 40 V/s
    voltage_fall_rate = [40.0]*num_channels
    supervision_max_current = [3000*1e-9]*num_channels  # 3000 nA
    trip_time_max_current = [100]*num_channels # 100 ms
    trip_action_max_current = [1]*num_channels # 1: switch off this channel by ramp down the voltage
    for i, chan in enumerate(HV_CHANNELS_OIDS):
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + \
                   "outputVoltageRiseRate" + chan + " F " + str(voltage_rise_rate[i])]
        snmp_command(command)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + \
                   "outputVoltageFallRate" + chan + " F " + str(voltage_fall_rate[i])]
        snmp_command(command)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + \
                   "outputSupervisionMaxCurrent" + chan + " F " + str(supervision_max_current[i])]
        snmp_command(command)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + \
                   "outputTripTimeMaxCurrent" + chan + " i " + str(trip_time_max_current[i])]
        snmp_command(command)
        command = ["snmpset " + SNMP_OPTIONS + SNMP_COMM_WRITE + SNMP_HOST + \
                   "outputTripActionMaxCurrent" + chan + " i " + str(trip_action_max_current[i])]
        snmp_command(command)


def show_info():
    """Generate info summary string
    """
    title = [ f"Ch{x:02d}  " for x in range(1,9)]
    switch = [ f"{x:<6}" for x in get_output_switch() ]
    volts = [ f"{x:6.1f}" for x in get_voltages() ]
    volt_rise = [ f"{x:6.1f}" for x in get_riserate_voltage() ]
    amps = [ f"{x:6.1f}" for x in get_currents() ]
    #meas_volts = [ f"{x:6.1f}" for x in get_measured_voltages() ]
    #meas_amps = [ f"{x:6.1f}" for x in get_measured_currents() ]
    out_string = f'''Value      {"  ".join(title)}
-------------------------------------------------------------------------
Switch     {"  ".join(switch)}
set Volts  {"  ".join(volts)}
riseRate V {"  ".join(volt_rise)}
set uAmps  {"  ".join(amps)}'''

    #meas V     {"  ".join(meas_volts)}
    #meas nA    {"  ".join(meas_amps)}
    return out_string

def show_amp_meas():
    """Generate info summary string
    """
    meas_amps = [ f"{x:6.1f}" for x in get_measured_currents() ]
    meas_volts = [ f"{x:6.1f}" for x in get_measured_voltages() ]
    out_string = f'''meas V     {"  ".join(meas_volts)}
meas nA    {"  ".join(meas_amps)}
'''
    return out_string

#set_voltages(volt_on)

#res = get_voltages()
#for volt in res: print(volt)
#
#set_output_switch([0]*8)
#switch = get_output_switch()
#for chan in switch: print(chan)
#set_currents([4.0]*8)
#
#res = get_status()
#for volt in res: print(volt)

if __name__ == "__main__":
    #set_output_switch([0]*8)
    #set_mpod_basic_config()
    #print(show_info())

    #for line in get_status():
    #    print(line)

    set_voltages(volt_on)
