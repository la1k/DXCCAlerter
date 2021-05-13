"""
Parse DX cluster telnet spots and print to STDOUT on:

    * Match against pre-defined list of watched calls.
    * Match against missing DXCC entities in ClubLog.
"""

import sys
import telnetlib
import time
import re
from urllib.request import urlopen
import json
from configparser import ConfigParser

"""
Class for keeping track over the time since the last time
a specific country and band were spotted.
"""
class spot_timekeeper:
    def __init__(self):
        # Map over the times at which a specific (country code, band) were spotted
        self.spot_times = {}

        # Time threshold
        threshold_seconds = 60*60

    """
    Check whether the time since the last spot is large enough for reporting a
    new spot for this country and band. Updates the spot time if successful.

    Parameters
    ----------
    country_code:
        Country code
    band:
        Band

    Returns
    -------
    exceeds_threshold: boolean
        True if time difference exceeds the threshold, false otherwise
    """
    def exceeds_threshold(self, country_code, band):
        curr_time = time.time()
        if (curr_time - self.spot_times.get((country_code, band), 0) > self.threshold_seconds):
            self.spot_times[(country_code, band)] = curr_time
            return True
        return False;

"""
Map frequencies to ham bands between 160 and 6 m.

Parameters
----------
freq: float
    Frequency in kHz

Returns
-------
band: float
    Ham radio band (e.g. 80 for 80 meters)
"""
def frequency_to_band(freq):
    if 1810.0<frequency<2000.0:
        band = "160"
    elif 3500.0<frequency<3800.0:
        band = "80"
    elif 5260.0<frequency<5410.0:
        band = "60"
    elif 7000.0<frequency<7200.0:
        band = "40"
    elif 10100.0<frequency<10150.0:
        band = "30"
    elif 14000.0<frequency<14350:
        band = "20"
    elif 18068.0<frequency<18168.0:
        band = "17"
    elif 21000.0<frequency<21450.0:
        band = "15"
    elif 24740.0<frequency<24990.0:
        band = "12"
    elif 28000.0<frequency<29700.0:
        band = "10"
    elif 50000.0<frequency<52000.0:
        band = "6"
    else:
        band = None
    return band

"""
Map callsign to DXCC number, locator, .. using the ClubLog API.

Parameters
----------
callsign: str
    Callsign
api_key: str
    ClubLog API key
"""
def query_dxcc_info(callsign, api_key):
    return json.load(urlopen("https://secure.clublog.org/dxcc?call=%s&api=%s&full=1" % (callsign,api_key)))

"""
Check if the DXCC has already been run on the specified band.

Parameters
----------
dxcc: str
    DXCC number
band: str
    Band (e.g. 80 for 80 meters)
matrix_filename: str
    Filename for JSON structure containing DXCC information obtained from ClubLog
"""
def dxcc_in_matrix(dxcc, band, matrix_filename):
    try:
        with open(matrix_filename) as dxcc_json_data:
            dxcc_data = json.load(dxcc_json_data)
            dxcc_data[dxcc][band]
            return True
    except KeyError:
        return False

# Check number of cli arguments
if len(sys.argv) <= 1:
    print("Usage: " + sys.argv[0] + " [CONFIG FILE]")
    exit()

# Read config file
config = ConfigParser()
config.readfp(open(sys.argv[1], "r"))

# JSON DXCC matrix filename
SECTION = "spotter"
dxcc_matrix_filename = config.get(SECTION, "dxcc_matrix_filename")

# Clublog API key
api_key = config.get(SECTION, "clublog_api_key")

# Obtain list of callsigns we want to spot in addition to missing calls in the DXCC matrix
watched_callsigns = config.get(SECTION, "watched_callsigns").split()

# Spam filter: keep track over the last spot
# time of specific country and band
time_since_last_report = spot_timekeeper()

# Open connection to telnet
tn = telnetlib.Telnet(config.get(SECTION, "cluster_host"), config.get(SECTION, "cluster_port"))
tn.read_until(b":")
tn.write((config.get(SECTION, "callsign") + "\n").encode('ascii'))

# Define regular expressions for obtaining callsign, frequency etc from a spot
callsign_pattern = "([a-z|0-9|/]+)"
frequency_pattern = "([0-9|.]+)"
pattern = re.compile("^DX de "+callsign_pattern+":\s+"+frequency_pattern+"\s+"+callsign_pattern+"\s+(.*)\s+(\d{4}Z)", re.IGNORECASE)

# Parse DXCC cluster stream
while (1):
    # Obtain new spotted call
    telnet_output = tn.read_until(b"\n")
    print(telnet_output)
    match = pattern.match(telnet_output.decode('ascii'))

    # If there is a match, sort matches into variables
    if match:
        spotter = match.group(1)
        frequency = float(match.group(2))
        spotted = match.group(3)
        comment = match.group(4).strip()
        spot_time = match.group(5)
        band = frequency_to_band(frequency)

        # Get DXCC information from clublog API
        spotter_data = query_dxcc_info(spotter, api_key)
        spotted_data = query_dxcc_info(spotted, api_key)
        spotted_dxcc_route = str(spotted_data["DXCC"])

        #note: spotted_data also contains coordinates of the spotted callsign which can be used for further filtering.

        # Report the call if it has not been worked before
        if band and spotted_dxcc_route and time_since_last_report.exceeds_threshold(spotted_dxcc_route, band) and not dxcc_in_matrix(spotted_dxcc_route, band, dxcc_matrix_filename):
            print("New DXCC! {} ({}) at {} by {} ({} - {}) {}".format(spotted,spotted_data["Name"],frequency,spotter,spotter_data["Name"], comment, spot_time))

        # Compare callsign against watched list of callsigns for which we are reporting spots regardless of DXCC matrix
        if any(x in spotted for x in watched_callsigns):
            print("{} at {} by {} ({}) {}".format(spotted,frequency,spotter,comment,spot_time))

