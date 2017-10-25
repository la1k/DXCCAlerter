# DXCCAlerter

A simple Python-based DX-cluster parser. The cluster output is filtered with
the help of ClubLog lookup, and only new DXCC calls or watched callsigns are
output to the command line. The output here can be used for further processing
and output to e.g. an IRC channel, a desktop screen or similar.

Synopsis
--------

`./get_clublog_dxcc_matrix.sh [PATH TO CONFIG FILE]`

Download a matrix specifying which DXCCs have been run for a given band.  The
matrix is obtained as a JSON structure from ClubLog and saved to a filename
specified in the config file. Correct information here requires that logs are
uploaded to ClubLog.

`./cluster_spotter.py [PATH TO CONFIG FILE]`

Connect to the DXCC cluster specified in the config file and continuosly parse
for new callsigns. Callsigns are looked up against the ClubLog API and compared
against the DXCC matrix currently contained in the DXCC matrix file. New DXCC
oppourtunities are then printed to standard output, in addition to spots for
any watched calls.

Config file
-----------

A configuration file is required for the scripts. The file contains the login
information for the ClubLog API, host and port and callsign for the DX cluster,
and a filename for which to save the ClubLog DXCC JSON structure. In addition,
a list over callsigns can be specified so that spots for these callsigns always
will be output to standard output regardless of DXCC status.

An example configuration file is shown below:

```
[spotter]
dxcc_matrix_filename = dxcc_matrix.dat
watched_callsigns = LA1K LA6XTA LA3WUA
callsign = YOUR_CALLSIGN
clublog_api_key = YOUR_API_KEY
cluster_host = la3waa.ddns.net
cluster_port = 8000
clublog_email = YOUR@E.MAIL
clublog_password = YOUR_PASSWORD
```
