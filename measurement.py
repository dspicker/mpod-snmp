import os
import time
import threading
import my_netsnmp





def get_values(print_idx = 0):
    output = list()
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    voltages = my_netsnmp.get_measuredVoltages()
    currents = my_netsnmp.get_measuredCurrents()
    for volt, nanoamp, channel in zip(voltages, currents, range(15)):
        result = f"{print_idx: 5d}, {time_str}, {channel: 7d}, {volt: 8.2f}, {nanoamp: 10.2f}\n"
        output.append(result)
        #print(result, end='')
    #print(" ")
    return output


def get_csvheader():
    header = f"Index, {"Time".ljust(19)}, Channel,  Voltage, Current nA\n"
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


def run_measurement(csv_filename = "/home/dspicker/mpod_control/measurement.csv"):
    check_csvfile(csv_filename)

    print(f"Starting measurement. \nUsing file {csv_filename}")
    index = 0
    thisthread = threading.current_thread()
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
        while getattr(thisthread, "keep_going", True):
            valstrings = get_values(index)
            csv_file.writelines(valstrings)
            time.sleep(2)
            index += 1
    print("Measurement finished.")


def measure_once(csv_filename = "/home/dspicker/mpod_control/measurement.csv") -> list[str]:
    """Get Voltages and Currents from all eight channels of the MPOD

    Args:
        csv_filename (str, optional): File to save the result to. Defaults to "/home/dspicker/mpod_control/measurement.csv".

    Returns:
        list[str]: csv formatted measurement values as they are written to the file.
    """
    check_csvfile(csv_filename)
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
        valstrings = get_values()
        csv_file.writelines(valstrings)
    return valstrings


if __name__ == "__main__":
    #print(f"Index, {"Time".ljust(19)}, Channel, Voltage, Current nA\n")
    #get_values()
    measurement = threading.Thread(target=run_measurement)
    try:
        measurement.start()
        seconds = 5.0 * 60
        loops = 10
        time.sleep(2)
        for i in range( loops ):
            print(f"{((i/loops) * 100):2.0f} % done")
            time.sleep(seconds/loops)
        measurement.keep_going = False
    except KeyboardInterrupt:
        measurement.keep_going = False
        print("  interrupted  ")

