#!/bin/bash

#check cli arguments
if [ "$#" -ne 1 ]; then
	echo "Usage: $0 [config_file]"
	exit
fi

#check whether file exists
config_file="$1"
if [ ! -e $config_file ]; then
	echo "File $config_file does not exist"
	exit
fi

# Obtain config option from config file in style `config_option = value`
function get_config_option()
{
	config_option="$1"
	option_value=$(cat $config_file | sed -rn "s/$config_option\s*=\s*(.*)/\1/p")
	if [[ -z "$option_value" ]]; then
		(>&2 echo "Option $config_option does not exist in $config_file")
		exit
	fi
	echo $option_value
}

#get relevant config options from config file
API_key=$(get_config_option "clublog_api_key")
callsign=$(get_config_option "callsign")
email=$(get_config_option "clublog_email")
password=$(get_config_option "clublog_password")
output_filename=$(get_config_option "dxcc_matrix_filename")
curl -s "https://secure.clublog.org/json_dxccchart.php?call=$callsign&api=$API_key&email=$email&password=$password&mode=0" > $output_filename
