"""
This module can be used to plot data that was acquired with measurement.py
"""
import sys
import os
import matplotlib.dates
import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib


matplotlib.use('tkagg')


def get_data_from_csv(_csv_path: str):
    csv_data = pd.read_csv(_csv_path, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    csv_data = csv_data.rename(columns=lambda x: x.strip())
    return csv_data


def get_environment_data(start_time: pd.Timestamp, end_time: pd.Timestamp):
    """Get temperature and humidity for given time interval.

    Args:
        start_time (pd.Timestamp): _description_
        end_time (pd.Timestamp): _description_

    Returns:
        pd.DataFrame: _description_

    First lines of csv file look like this:  
    ```
    Epoch,Time,Humidity %RH,Temperature C
    1720695546.0,2024-07-11 12:59,42.9,22.5
    ```
    """
    csv_fullpath = "/home/dspicker/environment_monitoring/env_data.csv"
    env_data = pd.read_csv(csv_fullpath, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M")
    env_data = env_data.rename(columns=lambda x: x.strip())
    env_data = env_data.loc[ (env_data["Time"] >= start_time) & (env_data["Time"] < end_time) ]
    env_data["Timedelta"] = env_data["Time"] - start_time
    env_data["Timedelta"] = env_data["Timedelta"].dt.total_seconds() / (60 * 60)

    return env_data


def get_pressure_data_dwd(start_time: pd.Timestamp, end_time: pd.Timestamp):
    csv_fullpath = "/home/dspicker/mpod_control/measure_with_window/produkt_p0_stunde_20231112_20250514_01420.txt"
    press_data = pd.read_csv(csv_fullpath, sep=";", header=0, parse_dates=[1], date_format="%Y%m%d%H")
    press_data = press_data.rename(columns=lambda x: x.strip())
    # MESS_DATUM ist in utc, daher konvertierung zu lokaler zeitzone und dann löschen der zeitzonen info.
    press_data["Time_Local"] = press_data["MESS_DATUM"].dt.tz_localize('utc').dt.tz_convert("Europe/Berlin").dt.tz_localize(None)
    press_data = press_data.loc[ (press_data["Time_Local"] >= start_time) & (press_data["Time_Local"] < end_time)]
    
    press_data["Timedelta"] = press_data["Time_Local"] - start_time
    press_data["Timedelta"] = press_data["Timedelta"].dt.total_seconds() / (60 * 60)

    return press_data


def get_pressure_data(start_time: pd.Timestamp, end_time: pd.Timestamp):
    """

    First two lines of input csv:
    ```
    Time,Temperature,Pressure
    2025-05-20 16:10:01,22.91,998.53
    ```
    """
    csv_fullpath = "/home/dspicker/mpod_control/measure_with_window/2025_05_20_luftdruck_sensordaten.csv"
    press_data = pd.read_csv(csv_fullpath, sep=",", header=0, parse_dates=[0], date_format="%Y-%m-%d %H:%M:%S")
    press_data = press_data.rename(columns=lambda x: x.strip())
    press_data = press_data.loc[ (press_data["Time"] >= start_time) & (press_data["Time"] < end_time)]
    
    press_data["Timedelta"] = press_data["Time"] - start_time
    press_data["Timedelta"] = press_data["Timedelta"].dt.total_seconds() / (60 * 60)

    return press_data


def get_start_end_time(dataframe: pd.DataFrame):
    starttime: pd.Timestamp = dataframe["Time"].iat[0]
    endtime: pd.Timestamp = dataframe["Time"].iat[-1]

    # timestamp() converts to posix timestamp as float
    return (starttime, endtime)


if __name__ == "__main__":

    csv_filename = sys.argv[1]
    if not csv_filename:
        sys.exit()
    csv_path = os.getcwd() + "/" + csv_filename

    measurement_data = get_data_from_csv(csv_filename)
    times = get_start_end_time(measurement_data)

    measurement_data["Timedelta"] = measurement_data["Time"] - times[0]
    measurement_data["Timedelta"] = measurement_data["Timedelta"].dt.total_seconds() / (60 * 60)

    environment_data = get_environment_data(times[0], times[1])
    pressure_data = get_pressure_data(times[0], times[1])


    fig, (ax_current, ax_hum, ax_temp, ax_press) = plt.subplots( \
        4,1, sharex=True, figsize=(12,8), \
        gridspec_kw={'height_ratios': [4,1,1,1], 'hspace': 0.05, 'left': 0.07, 'right':0.95, 'top':0.95} )

    for i in range(8):
        data_chan = measurement_data.loc[ measurement_data["Channel"] == i ]
        ax_current.plot(data_chan["Timedelta"], data_chan["Current nA"], '-', linewidth=0.7, label=str(f"Ch {i}"))

    data_win = measurement_data.loc[(measurement_data["Channel"] == 99)]
    ax_current.plot(data_win["Timedelta"], data_win["Current nA"].abs(), '-', linewidth=0.7, label=str("Window (neg.)"))

    ax_current.set_ylabel('Current / nA')
    ax_current.grid(True)
    ax_current.grid(visible=True, which="minor", axis="y", linestyle="-", alpha=0.4)
    ax_current.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    #ax_current.legend()

    ax_hum.plot(environment_data["Timedelta"], environment_data["Humidity %RH"], '-', label="% Rel. Hum.")
    ax_hum.grid(True)
    ax_hum.set_ylabel('% Rel. Hum.')

    #ax_temp.plot(environment_data["Timedelta"], environment_data["Temperature C"], '-r', label="Temp C")
    ax_temp.plot(pressure_data["Timedelta"], pressure_data["Temperature"], '-r', linewidth=0.6, label="Temp C")
    ax_temp.grid(True)
    ax_temp.set_ylabel('Temp / deg. C')

    ax_press.plot(pressure_data["Timedelta"], pressure_data["Pressure"], '-g', linewidth=0.6)
    ax_press.grid(True)
    ax_press.set_ylabel('Press. / hPa')
    ax_press.set_xlabel('Time / hours')

    ax_current.grid(visible=True, which="minor", axis="x", linestyle=":", alpha=0.4)
    ax_hum.grid(visible=True, which="minor", axis="x", linestyle=":", alpha=0.4)
    ax_temp.grid(visible=True, which="minor", axis="x", linestyle=":", alpha=0.4)
    ax_press.grid(visible=True, which="minor", axis="x", linestyle=":", alpha=0.4)
    ax_press.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax_press.set_xlim((0.0, 24.0))



    #ax_temp.xaxis.set_major_formatter(matplotlib.dates.AutoDateFormatter(matplotlib.dates.AutoDateLocator()))

    plt.show()

    