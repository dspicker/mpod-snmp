import matplotlib.dates
import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
#import datetime

matplotlib.use('tkagg')

#csv_filename = "/home/dspicker/mpod_control/chamber3_hv.csv"
#csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
#csv_data = csv_data.rename(columns=lambda x: x.strip())

def calc_mean_currents():
    csv_filename = "/home/dspicker/mpod_control/chamber3_hv.csv"
    csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    csv_data = csv_data.rename(columns=lambda x: x.strip())
    mean_currents = list()
    for i in range(8):
        current = csv_data.loc[ (csv_data["Channel"] == i) , ["Current nA"] ].mean()
        #current = csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Voltage"] > 1590.0), ["Current nA"] ].mean()
        mean_currents.append(current.iat[0])

    for chan in mean_currents:
        print(f"{chan:8.2f}")


def plot_u_i():
    csv_filename = "/home/dspicker/mpod_control/chamber3_hv.csv"
    csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    csv_data = csv_data.rename(columns=lambda x: x.strip())
    data_ch = list()
    for i in range(8):
        data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Current nA"] > 1.0) ] )
        plt.plot(data_ch[i]["Voltage"], data_ch[i]["Current nA"], 'o:', label=str(f"Ch {i}"))

    plt.title('HV Test')
    plt.xlabel('Voltage / V')
    plt.ylabel('Current / nA')
    plt.grid(True)
    plt.yscale("log") 
    plt.legend()
    #plt.xlim((1000.0, 2010.0))
    plt.show()

def plot_t_i():
    csv_filename = "/home/dspicker/mpod_control/chamber3_time.csv"
    csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    #csv_data = csv_data.rename(columns=lambda x: x.strip())
    starttime = csv_data["Time"].iat[0]
    #print(starttime)
    csv_data["Timedelta"] = csv_data["Time"] - starttime
    csv_data["Timedelta"] = csv_data["Timedelta"].dt.total_seconds()
    #print(csv_data["Timedelta"])

    fig, ax = plt.subplots()

    data_ch = list()
    for i in range(8):
        data_ch.append(csv_data.loc[ (csv_data["Channel"] == i) & (csv_data["Current nA"] > 1.0) ] )
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

if __name__ == "__main__":
    #plot_t_i()
    plot_u_i()
    
    #csv_filename = "/home/dspicker/mpod_control/chamber3_hv.csv"
    #csv_data = pd.read_csv(csv_filename, header=0, parse_dates=[1], date_format="%Y-%m-%d %H:%M:%S")
    #csv_data = csv_data.rename(columns=lambda x: x.strip())
    #print(csv_data["Time"])