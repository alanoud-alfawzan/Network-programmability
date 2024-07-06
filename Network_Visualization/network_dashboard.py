# Import needed libraries
import urllib3
import requests
import pandas as pd
from nornir import InitNornir
from datetime import datetime
import taipy.gui.builder as tgb
from taipy.gui import Gui, notify

# We need to disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize connection in nornir
nr = InitNornir(config_file="config.yml")


# _______________Define Functions_______________
def get_restconf_data(task):
    """
    This function will use RESTCONF API to grap all information
    of all interfaces in iosxe, then parsing nornir output and return the information
    """
    # Our RESTCONF API call, of Cisco platforms
    url = f"https://{task.host.hostname}:443/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
    # Header
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }
    # API response
    response = requests.get(
        url,
        headers=headers,
        auth=(task.host.username, task.host.password),
        verify=False,
    )
    # Check API status code
    if response.status_code == 200:
        # Restracture the output to json formate
        interfaces = response.json()
        # Get the current date and time
        timestamp = datetime.now().strftime("%A, %B %d, %Y %H:%M")
        # Start parsing the response
        interface_data = interfaces.get(
            "Cisco-IOS-XE-interfaces-oper:interfaces", {}
        ).get("interface", [])
        out = []
        for interface in interface_data:
            if interface["admin-status"] == "if-state-up":
                interface_status = "up"
            elif interface["admin-status"] == "if-state-down":
                interface_status = "down"
            else:
                interface_status = "N/A"
            out.append(
                {
                    "Hostname": task.host.name,
                    "Interface": interface.get("name", "N/A"),
                    "IP": interface.get("ipv4", "N/A"),
                    "Description": interface.get("description", "N/A"),
                    "Input": interface.get("v4-protocol-stats", {}).get(
                        "in-pkts", "N/A"
                    ),
                    "Output": interface.get("v4-protocol-stats", {}).get(
                        "out-pkts", "N/A"
                    ),
                    "MTU": interface.get("mtu", "N/A"),
                    "Status": interface_status,
                    "CRC": interface.get("statistics", {}).get("in-crc-errors", "N/A"),
                    "Mode": interface.get("ether-state", {}).get(
                        "negotiated-duplex-mode", "N/A"
                    ),
                    "Date_Time": timestamp,
                }
            )
        return out
    else:
        return []


def get_data():
    """
    This function will run nornir task, and access norrnir parsing nornir output
    and return the data
    """
    result = nr.run(task=get_restconf_data)
    data = []
    for host, task_result in result.items():
        data.extend(task_result.result)
    return data


def start_filter(state):
    """
    In this function we will build a filter for dashboard GUI
    based on user choise, and return error message if no selection
    """
    if len(state.duplex) == 0 or len(state.hostname) == 0 or len(state.status) == 0:
        notify(state, "Error", "Please check the filter")
        return
    state.data_filter, state.input_interface, state.output_interface = interface_filter(
        state.duplex, state.hostname, state.status
    )


def interface_filter(duplex, hostname, status):
    """
    This function will take three args:
        duplex (text), hostname (text), status (text)
    And take sum of packets bandwidth and sort values in descending order,
    then return the data
    """
    data_filtered = data[
        data["Mode"].isin(duplex)
        & data["Hostname"].isin(hostname)
        & data["Status"].isin(status)
    ]
    input_interface = (
        data_filtered[["Interface", "Input"]]
        .groupby("Interface")
        .sum()
        .sort_values(by="Input", ascending=False)
        .reset_index()
    )
    output_interface = (
        data_filtered[["Interface", "Output"]]
        .groupby("Interface")
        .sum()
        .sort_values(by="Output", ascending=False)
        .reset_index()
    )
    return data_filtered, input_interface, output_interface

print("<<<< Start to gather information 🤯>>>>")

# Convert data in list to pandas formate
nornir_data = get_data()

data = pd.DataFrame(nornir_data)

# Convert datatype of two pandas columns
data["Input"] = pd.to_numeric(data["Input"], errors="coerce").fillna(0).astype(int)
data["Output"] = pd.to_numeric(data["Output"], errors="coerce").fillna(0).astype(int)
print(data["Date_Time"].unique()[0])
# Get unique values of each filter
duplex = list(data["Mode"].unique())
hostname = list(data["Hostname"].unique())
status = list(data["Status"].unique())

# Start build the dashboard
print("<<<< Start build the dashbord 💻>>>>")

with tgb.Page() as page:
    tgb.toggle(theme=True)
    tgb.text("🤩 My Network Dashboard", class_name="h1 text-center pb2")
    # _______________KPIs Section_______________
    with tgb.layout("1 1 1", class_name="p1"):
        with tgb.part(class_name="card"):
            tgb.text("## Date & Time:", mode="md")
            tgb.text("{data['Date_Time'].unique()[0]}", class_name="h6 text-center")
        with tgb.part(class_name="card"):
            tgb.text("## Total Interfaces:", mode="md")
            tgb.text("{len(data_filter['Interface'])}", class_name="h6 text-center ")
        with tgb.part(class_name="card"):
            tgb.text("## Total Devices:", mode="md")
            tgb.text(
                "{len(data_filter['Hostname'].unique())}", class_name="h6 text-center"
            )
    # _______________Selector Section_______________
    with tgb.layout("1 1 1", class_name="p1"):
        tgb.selector(
            value="{duplex}",
            lov=duplex,
            dropdown=True,
            multiple=True,
            label="Mode",
            class_name="fullwidth",
            on_change=start_filter,
        )
        tgb.selector(
            value="{hostname}",
            lov=hostname,
            dropdown=True,
            multiple=True,
            label="Hostname",
            class_name="fullwidth",
            on_change=start_filter,
        )
        tgb.selector(
            value="{status}",
            lov=status,
            dropdown=True,
            multiple=True,
            label="Status",
            class_name="fullwidth",
            on_change=start_filter,
        )
    # _______________Barchart Section_______________
    with tgb.layout("1 1", class_name="p1"):
        tgb.chart(
            "{input_interface}",
            x="Interface",
            y="Input",
            type="bar",
            title="Total of Input Packets",
        )
        tgb.chart(
            "{output_interface}",
            x="Interface",
            y="Output",
            type="bar",
            title="Total of Output Packets",
        )
    # _______________Table Section_______________
    with tgb.layout("1", class_name="p1"):
        tgb.table(
            "{data_filter}",
            columns=[
                "Hostname",
                "Interface",
                "IP",
                "Description",
                "Input",
                "Output",
                "Status",
            ],
            allow_all_rows=True,
        )

if __name__ == "__main__":
    data_filter, input_interface, output_interface = interface_filter(
        duplex, hostname, status
    )
    print("<<<< Your dashbord is ready 😎👌>>>>")
    Gui(page, ).run(
        title="Network dashboard",
        use_reloader=True,
        debug=True,
        watermark="",
    )
