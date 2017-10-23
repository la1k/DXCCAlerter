# DXCCAlerter
A simple python based DX-cluster parser. The cluster output is filtered with the help of ClubLog lookup.

To run the script a config file is required. This file is used to pass user-specific information to the script, and is passed as an argument. An example config-script is shown below.

```
[spotter]
clublog_api_key = YOUR_API_KEY
dxcc_matrix_filename = dxcc_matrix.dat
watched_callsigns = LA1K LA6XTA LA3WUA
callsign = YOUR_CALLSIGN
cluster_host = la3waa.ddns.net
cluster_port = 8000
clublog_email = YOUR@E.MAIL
clublog_password = YOUR_PASSWORD
```

After the config file is written the script can be run:

get_clublog_dxcc_matrix.sh fetches Club Logs DXCC matrix, this is a .json structure which contains information on which DXCCs you have worked on different bands. To obtain this information you must upload your logs to Club Log.
```
./get_clublog_dxcc_matrix.sh my_config.conf
```
The python script opens a telnet connection to the telnet specified in the config file. Once the script identifies a new DXCC opportunity it will print it to the command line. 
```
python cluster_spotter.py my_config.conf
```
