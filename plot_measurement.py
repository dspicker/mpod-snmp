import matplotlib.dates
import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
#import datetime

matplotlib.use('tkagg')

CSV_DIRNAME = "/home/dspicker/mpod_control/"


def get_data_from_csv(_csv_path: str):
    csv_data = pd.read_csv(_csv_path, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    csv_data = csv_data.rename(columns=lambda x: x.strip())
    return csv_data


def calc_mean_currents(_csv_path: str):
    csv_data = get_data_from_csv(_csv_path)
    mean_currents = list()
    for i in range(8):
        current = csv_data.loc[ (csv_data["Channel"] == i) , ["Current nA"] ].mean()
        #current = csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Voltage"] > 1590.0), ["Current nA"] ].mean()
        mean_currents.append(current.iat[0])

    for chan in mean_currents:
        print(f"{chan:8.2f}")


def plot_u_i(_csv_path: str):
    calibration = [304.46, -14.90, 161.14, 150.04, -15.25, 187.31, 44.90, 256.30]
    #calibration = [304.46,   0.0 , 161.14, 150.04,   0.0 , 187.31, 44.90, 256.30]

    csv_data = get_data_from_csv(_csv_path)
    csv_data["calib Current"] = csv_data.apply(lambda row: row["Current nA"] - calibration[int(row["Channel"])] , axis=1)
    
    data_ch = list()
    for i in range(8):
        #data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Current nA"] > 1.0) ] )
        data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) ] )
        #plt.plot(data_ch[i]["Voltage"], data_ch[i]["Current nA"], 'o:', label=str(f"Ch {i}"))
        plt.plot(data_ch[i]["Voltage"], data_ch[i]["calib Current"], 'o:', label=str(f"Ch {i}"))

    plt.title('HV Test')
    plt.xlabel('Voltage / V')
    plt.ylabel('Current / nA')
    plt.grid(True)
    #plt.yscale("log")
    plt.legend()
    #plt.xlim((1600.0, 2050.0))
    #plt.ylim((-10.0, 1800.0))
    plt.show()


def plot_t_i(_csv_path: str):
    csv_data = get_data_from_csv(_csv_path)
    starttime = csv_data["Time"].iat[0]
    #print(starttime)
    csv_data["Timedelta"] = csv_data["Time"] - starttime
    csv_data["Timedelta"] = csv_data["Timedelta"].dt.total_seconds()
    #print(csv_data["Timedelta"])

    fig, ax = plt.subplots()

    data_ch = list()
    for i in range(8):
        #data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Current nA"] > 1.0) ] )
        data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) ] )
        ax.plot(data_ch[i]["Timedelta"], data_ch[i]["Current nA"], '.', label=str(f"Ch {i}"))

    #ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%M:%S"))
    #locator = matplotlib.ticker.LinearLocator(10)
    #locator = matplotlib.dates.MinuteLocator()
    #ax.xaxis.set_major_locator(locator)
    ax.set_title('HV Test')
    ax.set_xlabel('Time / s')
    ax.set_ylabel('Current / nA')
    ax.legend()
    ax.grid(True)
    #fig.autofmt_xdate()
    plt.show()


def compare_channel(_ch_id: int = 0):
    file1 = CSV_DIRNAME + "glued_02_18.csv"
    file2 = CSV_DIRNAME + "chamber3_hv.csv"
    data_file1 = get_data_from_csv(file1)
    data_file2 = get_data_from_csv(file2)
    data_file1 = data_file1.loc[ (data_file1["Channel"] == _ch_id) & (data_file1["Current nA"] > 1.0) ]
    data_file2 = data_file2.loc[ (data_file2["Channel"] == _ch_id) & (data_file2["Current nA"] > 1.0) ]
    plt.plot(data_file1["Voltage"], data_file1["Current nA"], 'o:', label=str(f"Ch {_ch_id} with glue"))
    plt.plot(data_file2["Voltage"], data_file2["Current nA"], 'o:', label=str(f"Ch {_ch_id} no glue"))

    plt.title('HV Test')
    plt.xlabel('Voltage / V')
    plt.ylabel('Current / nA')
    plt.grid(True)
    plt.yscale("log")
    plt.legend()
    #plt.xlim((1600.0, 2050.0))
    #plt.ylim((-10.0, 1800.0))
    plt.show()


def compare_channels():
    file1 = CSV_DIRNAME + "glued_02_18.csv"
    file2 = CSV_DIRNAME + "chamber3_hv.csv"
    data_file1 = get_data_from_csv(file1)
    data_file2 = get_data_from_csv(file2)

    #differences = list()
    #for i in range(2):
    i = 1
    data1 = data_file1.loc[ (data_file1["Channel"] == i) & (data_file1["Current nA"] > 1.0) ][["Voltage","Current nA"]]
    data2 = data_file2.loc[ (data_file2["Channel"] == i) & (data_file2["Current nA"] > 1.0) ][["Voltage","Current nA"]]
    diff = data1["Current nA"] - data2["Current nA"]
    print(data1)
    print(data2)
    print(diff)



if __name__ == "__main__":
    #csv_filename = "chamber3_hv.csv"
    #csv_filename = "glued_02_18.csv"
    #csv_filename = "n2_02_26.csv"
    #csv_filename = "measurement.csv"
    csv_filename = "m_2025_02_26_15_53.csv"
    csv_path = CSV_DIRNAME + csv_filename

    #plot_t_i(csv_path)
    plot_u_i(csv_path)
    #compare_channel(0)
    #compare_channels()

    #csv_filename = "/home/dspicker/mpod_control/chamber3_hv.csv"
    #csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    #csv_data = csv_data.rename(columns=lambda x: x.strip())
    #print(csv_data["Time"])
