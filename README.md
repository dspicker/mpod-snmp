# MPOD Control

Controlling the Wiener MPOD via snmp to perform High-Voltage tests in the lab during construction of CBM-TRD chambers.

## Setup

1. SNMP Setup

    ```bash
    sudo apt-get install snmp libsnmp-dev
    sudo apt-get install snmp-mibs-downloader
    sudo download mibs
    sudo cp WIENER-CRATE-MIB.txt usr/share/snmp/mibs
    ```

2. Python version  
    Make sure, the correct python version is available on your system. See Pipfile for the exact version.
    It is recommended to use pyenv for this. If necessary, do e.g. `pyenv install 3.12`. Then activate it with `pyenv shell 3.12`

3. Install pipenv  
    `pip install pipenv`

4. Install mpod snmp control  

    ```bash
    git clone git@github.com:dspicker/mpod-snmp.git
    cd mpod-snmp
    pipenv shell
    pipenv install
    ```

## How to use

If you haven't just finished installing, first activate the pipenv with `pipenv shell`

There are two main functionalities:

1. Live view of the measurement readings.
    Start with `python live_view.py`
2. Command line interface that allows to change settings or switch channels.
    Start with `python mpod_cli.py`

## snmp

``` bash
dspicker@pcikf156:~/mpod_control$ snmpwalk -Cp -v 2c -m +WIENER-CRATE-MIB -c public 141.2.243.129
SNMPv2-MIB::sysDescr.0 = STRING: WIENER MPOD (2688023, MPOD 2.1.6109.0, MPODslave 1.09, MPOD-BL 2.2439.0, UEP6000 2.22)
SNMPv2-MIB::sysObjectID.0 = OID: WIENER-CRATE-MIB::sysMainSwitch.0
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (57897246) 6 days, 16:49:32.46
SNMPv2-MIB::sysContact.0 = STRING: 
SNMPv2-MIB::sysName.0 = STRING: 
SNMPv2-MIB::sysLocation.0 = STRING: 
SNMPv2-MIB::sysServices.0 = INTEGER: 79
Variables found: 7
```

`snmpbulkget -Cr8 -Ov -OU -OQ -v 2c -m +WIENER-CRATE-MIB -c public 141.2.243.129 outputVoltage.500`
