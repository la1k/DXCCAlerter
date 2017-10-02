# Script that parses DXCC-cluster telnet spots and compares them to clublogs DXCC matrix. If new DXCCs appear the user may be alerted.

import sys
import telnetlib
import time
import re
import urllib2
import json
from math import radians, cos, sin, asin, sqrt

# Class for keeping track over the time since the last time
# a specific country and band were spotted.
class spot_timekeeper:
    # Map over the times at which a specific (country code, band) were spotted
    spot_times = {};

    # Time threshold
    threshold_seconds = 60*60

    # Check whether the time since the last spot is large enough
    # for reporting a new spot for this country and band. Updates
    # the spot time if successful.
    #
    # \param country_code Country code
    # \param band Band
    # \return True if time difference exceeds the threshold, false otherwise
    def exceeds_threshold(self, country_code, band):
        curr_time = time.time()
        if (curr_time - self.spot_times.get((country_code, band), 0) > self.threshold_seconds):
            self.spot_times[(country_code, band)] = curr_time
            return True
        return False;

# Map frequencies to ham bands between 160 and 6 m.
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

# Map callsign to DXCC number, locator, ..
def query_dxcc_info(callsign, api_key):
    return json.load(urllib2.urlopen("https://secure.clublog.org/dxcc?call=%s&api=%s&full=1" % (callsign,api_key)))

# Check if DXCC on frequency is in matrix
def dxcc_in_matrix(dxcc, band, matrix_filename):
    try:
        with open(matrix_filename) as dxcc_json_data:
            dxcc_data = json.load(dxcc_json_data)
            dxcc_data[dxcc][band]
            return True
    except KeyError:
        return False

# Read config file
config = ConfigParser.ConfigParser()
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
tn.read_until("login: ")
tn.write(config.get(SECTION, "callsign") + "\n")

# Define regular expressions
callsign_pattern = "([a-z|0-9|/]+)"
frequency_pattern = "([0-9|.]+)"
pattern = re.compile("^DX de "+callsign_pattern+":\s+"+frequency_pattern+"\s+"+callsign_pattern+"\s+(.*)\s+(\d{4}Z)", re.IGNORECASE)

# Parse telnet
while (1):
    # Check new telnet info against regular expression
    telnet_output = tn.read_until("\n")
    match = pattern.match(telnet_output)

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

        #note: spotted_data also contains coordinates of the spotted callsign which can be used for filtering.

        # Compare DXCC number to DXCC matrix, if there is an error the band has not been worked before
        if band and spotted_dxcc_route and time_since_last_report.exceeds_threshold(spotted_dxcc_route, band) and not dxcc_in_matrix(spotted_dxcc_route, band, dxcc_matrix_filename):
            print "New DXCC! %s (%s) at %s by %s (%s - %s) %s" % (spotted,spotted_data["Name"],frequency,spotter,spotter_data["Name"], comment, spot_time)

        # Compare callsign against watched list of callsigns for which we are reporting spots regardless of DXCC matrix
        if any(x in spotted for x in watched_callsigns):
            print "%s at %s by %s (%s) %s" % (spotted,frequency,spotter,comment,spot_time)

