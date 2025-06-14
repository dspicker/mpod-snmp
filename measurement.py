import os
import time
import threading
import my_netsnmp





def get_values(print_idx = 0):
    """Retrieve one set of measurement values from the mpod

    Args:
        print_idx (int, optional): Index to be printed to the csv file.
        Can help to distinguish measurements. Defaults to 0.

    Returns:
        list(str): Measurement output as lines in csv format.
    """
    output = list()
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    voltages = my_netsnmp.get_measured_voltages()
    currents = my_netsnmp.get_measured_currents()
    for volt, nanoamp, channel in zip(voltages, currents, range(15)):
        result = f"{print_idx: 5d} ,{time_str}, {channel: 7d}, {volt: 8.2f}, {nanoamp: 10.2f}\n"
        output.append(result)
        #print(result, end='')
    
    volt = my_netsnmp.get_win_meas_volt()[0]
    nanoamp = my_netsnmp.get_win_meas_curr()[0]
    win_result = f"{print_idx: 5d} ,{time_str},      99, {volt: 8.2f}, {nanoamp: 10.2f}\n"
    output.append(win_result)
    
    return output


def get_csvheader():
    """Returns a string with the csv file header"""
    header = f"Index ,{"Time".ljust(19)}, Channel,  Voltage, Current nA\n"
    return str(header)


def check_csvfile(csv_filename: str):
    """Prepare the given file to write the next measurement

    Creates a file, if it does not exist. Appends to an existing file.

    Args:
        csv_filename (str): Path to csv file
    """
    if not os.path.isfile(csv_filename) :
        file = open(csv_filename, "w", newline='', encoding='utf-8')
        file.write(get_csvheader())
        file.close()
    else:
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
            csv_file.write("\n")


def _measure_continuous(stop: threading.Event, interval: float):
    """Subthread for continuous measurement.

    To be called by run_cont_measurement()

    Args:
        stop (threading.Event): Controls the thread.
        interval (float): Time between Datapoints in seconds.
    """
    csv_filename = "cont_" + time.strftime("%Y_%m_%d_%H_%M", time.localtime()) + ".csv"
    csv_fullpath = os.getcwd() + "/" + csv_filename
    state = my_netsnmp.get_output_switch()
    if not 'on' in state:
        print("No channel is on. Switch on at least one channel.")
        return
    check_csvfile(csv_fullpath)

    print(f"Starting measurement. \nOutput file: {csv_fullpath}")
    index = 0
    while not stop.is_set():
        valstrings = get_values(index)
        with open(csv_fullpath, 'a', newline='', encoding='utf-8') as csv_file:
            csv_file.writelines(valstrings)
        index += 1
        stop.wait(interval)
    print("Measurement finished.")
    return


def run_cont_measurement(duration: float = 3.0, interval: float = 2.0):
    """Measure every n seconds for the given duration

    Args:
        duration (float, optional): Duration in minutes. Defaults to 3.0.
        interval (float, optional): Time between measurements in seconds. Defaults to 2.0.
    """
    stop_event = threading.Event()
    measurement = threading.Thread(target=_measure_continuous, args=(stop_event,interval))
    time_start = time.time()
    time_stop = time_start + 60.0 * duration
    print(f"Start time: {time.strftime("%a, %H:%M:%S", time.localtime(time_start))}")
    print(f"Measuring every {interval} seconds until {time.strftime("%a, %H:%M:%S", time.localtime(time_stop))}")
    try:
        measurement.start()
        while measurement.is_alive() and time.time() < time_stop:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
        print("  interrupted  ")
    finally:
        stop_event.set()
        measurement.join(3.0)
        print("Exit.")


def run_long_measurement():
    hours = 24.0
    interval = 15.0

    minutes = hours * 60.0

    run_cont_measurement(minutes, interval)

    my_netsnmp.set_output_switch( [0]*8 )
    my_netsnmp.set_win_output_switch(0)
    print("Long measurement finished. HV switched off.")


def measure_once(csv_filename: str = "") -> list[str]:
    """Get Voltages and Currents from all eight channels of the MPOD

    Args:
        csv_filename (str, optional): File to save the result to. 
            Defaults to "pwd/single_YY_mm_dd_HH_MM.csv".

    Returns:
        list[str]: csv formatted measurement values as they are written to the file.
    """
    if not csv_filename:
        csv_filename = "single_" + time.strftime("%Y_%m_%d_%H_%M", time.localtime()) + ".csv"
    csv_fullpath = os.getcwd() + "/" + csv_filename
    check_csvfile(csv_fullpath)
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
        valstrings = get_values()
        csv_file.writelines(valstrings)
    return valstrings


def _measure_u_i(stop: threading.Event):
    csv_filename = "m_" + time.strftime("%Y_%m_%d_%H_%M", time.localtime()) + ".csv"
    csv_fullpath = os.getcwd() + "/" + csv_filename
    wait_sec = 60.0

    state = my_netsnmp.get_output_switch() + my_netsnmp.get_win_output_switch()
    if 'on' not in state:
        print("No channel is on. Switch on at least one channel.")
        return
    check_csvfile(csv_fullpath)

    meas_voltages = [1600.0, 1650.0, 1700.0, 1750.0, 1800.0, 1850.0, 1900.0, 1950.0, 1975.0,\
                     2000.0, 2025.0]
    #meas_voltages = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, \
    #                 1100.0, 1200.0, 1300.0, 1400.0, 1500.0, 1550.0, 1600.0, 1650.0, 1700.0]

    print(f"Starting measurement  {time.strftime("%H:%M", time.localtime())} h")
    print(f"Output file: {csv_fullpath}")
    print("Using these voltages: ")
    print(meas_voltages)
    print(f"Estimated duration {(len(meas_voltages) * wait_sec)/60.0} minutes.")

    for idx, voltage in enumerate(meas_voltages):
        set_volt = [ voltage if ch == "on" else 0.0 for ch in state ]
        my_netsnmp.set_voltages(set_volt)
        print(f"Set voltage to {voltage} V. Waiting for {wait_sec} s.")
        stop.wait(wait_sec)
        if stop.is_set():
            print("break")
            break
        with open(csv_fullpath, 'a', newline='', encoding='utf-8') as csv_file:
            valstrings = get_values(idx)
            csv_file.writelines(valstrings)
            print(get_csvheader(), end='')
            for item in valstrings:
                print(item, end='')

    print("Measurement finished.")
    return


def run_u_i_measurement():
    stop_event = threading.Event()
    measurement = threading.Thread(target=_measure_u_i, args=(stop_event,))

    try:
        measurement.start()
        while measurement.is_alive():
            time.sleep(1.0) # keep the main thread idling
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
        print("  interrupted  ")
    finally:
        measurement.join(1.0)
        my_netsnmp.set_output_switch( [0]*8 )
        my_netsnmp.set_voltages( [100.0]*8 )
        print("Exit.")


if __name__ == "__main__":
    #print(f"Index, {"Time".ljust(19)}, Channel, Voltage, Current nA\n")
    #get_values()
    #run_cont_measurement(150.0)
    #run_u_i_measurement()
    run_long_measurement()
