#!/bin/bash

config_file="$1"

# Obtain config option from config file in style
#
# config_option = value
function get_config_option()
{
	config_option="$1"
	cat $config_file | sed -rn "s/$config_option\s*=\s*(.*)/\1/p"
}

API_key=$(get_config_option "clublog_api_key")
callsign=$(get_config_option "callsign")
email=$(get_config_option "clublog_email")
password=$(get_config_option "clublog_password")
output_filename=$(get_config_option "dxcc_matrix_filename")
curl -s "https://secure.clublog.org/json_dxccchart.php?call=$callsign\&api=$API_key\&email=$email\&password=$password\&mode=0" > $output_filename
