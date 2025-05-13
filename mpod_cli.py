import cmd
import time
import my_netsnmp
from measurement import measure_once, get_csvheader

class mpodCli(cmd.Cmd):
    prompt = '\033[1;36m(mpod cli)\033[0m >> '
    intro = "\033[0;30;107m Welcome to the MPOD command line interface.\033[0m \033[90m(Dennis Spicker, 2025)\033[0m"

    def emptyline(self):
        pass

    def do_quit(self, line):
        return True
    
    def do_init(self, line):
        my_netsnmp.set_mpod_basic_config()
        print("MPOD initialised")
    
    def do_voltage(self, line: float = None):
        """Get / set nominal output voltage of all HV channels

        Args:
            line (float, optional): If given, sets all channels to this voltage. Defaults to None.
        """
        if line:
            volts = [float(line)] * my_netsnmp.get_number_of_channels()
            my_netsnmp.set_voltages(volts)

        voltsget = my_netsnmp.get_voltages()
        for i, v in enumerate(voltsget):
            print(f"Ch {i+1:02d}: {v:6.1f} V")

    def do_win_voltage(self, line: float = None):
        if line:
            my_netsnmp.set_win_voltage(float(line))

        voltsget = my_netsnmp.get_win_voltage()
        print(f"Window: {voltsget[0]:6.1f} V")

    def do_current_limit(self, line: float = None):
        """Get / set nominal output current limit of all HV channels

        Args:
            line (float, optional): Current in micro Ampere.
            If given, sets all channels to this current. Defaults to None.
        """
        if line:
            currents = [float(line)] * my_netsnmp.get_number_of_channels()
            my_netsnmp.set_currents(currents)

        currentsget = my_netsnmp.get_currents()
        for i, v in enumerate(currentsget):
            print(f"Ch {i+1:02d}: {v:4.2f} uA")

    def do_win_current_limit(self, line: float = None):
        if line:
            my_netsnmp.set_win_current(float(line))
        currget= my_netsnmp.get_win_current()
        print(f"Window: {currget[0]:4.2f} uA")

    def do_switch(self, line: str = None):
        """Switch on or off channels. All channels at once or single channel individually.

        Args:
            Zero, one or two arguments. 
            - 0: show current state
            - 1: "on" or "off", switch all channels on or off
            - 2: e.g. "on 2", switches on channel 2
        """
        values = {"on": 1, "off": 0}
        if line:
            input = line.split()
            if len(input) > 1:
                state = my_netsnmp.get_output_switch()
                state = [ values[x] for x in state ]
                state[int(input[1])-1] = values[input[0]]
            else:
                state = [values[input[0]]]*my_netsnmp.get_number_of_channels()
            my_netsnmp.set_output_switch(state)
        switchget = my_netsnmp.get_output_switch()
        for i, v in enumerate(switchget):
            print(f"Ch {i+1:02d}: {v:<6}")

    def do_win_switch(self, line: str = None):
        #state = my_netsnmp.get_win_output_switch()[0]
        #voltage = my_netsnmp.get_win_voltage()[0]
        #current = my_netsnmp.get_win_current()[0]
        #if state == "off" and line == "on":
        #    my_netsnmp.set_win_voltage(10.0)
        #    my_netsnmp.set_win_current(50.0)
        #    my_netsnmp.set_win_output_switch(1)
        #    time.sleep(5)
        #    my_netsnmp.set_win_current(current)
        #    my_netsnmp.set_win_voltage(voltage)
        #elif line == "off":
        #    my_netsnmp.set_win_output_switch(0)
        #state = my_netsnmp.get_win_output_switch()[0]
        #print(f"Window: {state}")
        if line == "on":
            my_netsnmp.set_win_output_switch(1)
        elif line == "off":
            my_netsnmp.set_win_output_switch(0)



    def do_reset_outputs(self, line):
        value = [0]*my_netsnmp.get_number_of_channels()   # off
        my_netsnmp.set_output_switch(value)
        value = [2]*my_netsnmp.get_number_of_channels()   # resetEmergencyOff
        my_netsnmp.set_output_switch(value)
        value = [10]*my_netsnmp.get_number_of_channels()  # clearEvents
        my_netsnmp.set_output_switch(value)
        value = [0]*my_netsnmp.get_number_of_channels()   # off
        my_netsnmp.set_output_switch(value)
        my_netsnmp.set_win_output_switch(0)
        print("Outputs reset and all off.")

    def do_win_reset(self, line):
        my_netsnmp.set_win_output_switch(2)
        my_netsnmp.set_win_output_switch(10)
        my_netsnmp.set_win_output_switch(0)
        print("Window reset and off.")


    def do_measurement(self, line: str = None):
        """Measure Currents and Voltages of all eight channels once.

        Args:
            line (str): csv filename to write result to
        """
        result = measure_once(line)
        print(get_csvheader(), end='')
        for item in result:
            print(item, end='')


if __name__ == '__main__':
    mpodCli().cmdloop()