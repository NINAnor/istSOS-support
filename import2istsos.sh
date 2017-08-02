#!/bin/bash

# Usage info
show_help() {
cat << EOF

Import data from a csv file on an istSOS server.

Usage:
 bash import2istsos.sh csv_path=* observation_columns=* [timestamp_column=*]
                       [timestamp_format=*] url=* service=* offering=*
                       procedure=*

Flags:
  -h, -?, --help   Show this help message and exit
              -d   Use if you would like to convert all .csv files in your directory

Parameters:
             csv_path  Path to CSV file with observations (only working directory with files when using -d)
       file_extension  Extension of files with observations (not necessary when not using -d flag)
  observation_columns  Name of columns with observations (separated with ',')
     timestamp_column  Name of the column with timestamps
                       default: urn:ogc:def:parameter:x-istsos:1.0:time:iso8601
     timestamp_format  Format in which timestamps are provided
                       default: YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM
                  url  istSOS Server address IP or domain name
              service  The name of the service instance
             offering  A collection of sensor used to conveniently group them up
            procedure  Who provide the observations
EOF
}

set -e

timestamp_column='urn:ogc:def:parameter:x-istsos:1.0:time:iso8601'
timestamp_format='YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM'
directory=false
extension='csv'

OPTIND=1
for i in "$@"
do
    case "$i" in
        -h|-\?|--help)
            show_help
            exit
            ;;
        -d)
            directory=true
            ;;
        csv_path=*)
            csv_path="${i#*=}"
            ;;
        timestamp_column=*)
            timestamp_column="${i#*=}"
            ;;
        observation_columns=*)
            observation_columns="${i#*=}"
            ;;
        timestamp_format=*)
            timestamp_format="${i#*=}"
            ;;
        service=*)
            service="${i#*=}"
            ;;
        offering=*)
            offering="${i#*=}"
            ;;
        procedure=*)
            procedure="${i#*=}"
            ;;
        url=*)
            url="${i#*=}"
            ;;
        observations_directory=*)
            workspace="${i#*=}"
            ;;
        file_extension=*)
            extension="${i#*=}"
            ;;
        ?*)
            printf '\nERROR: Unknown option: %s\nEXECUTION STOPPED\n' "$i"
            exit
    esac
done

workspace=${csv_path%/*}

printf "creating .dat from your .csv"
if $directory;
then
    python convert2dat.py -path=$csv_path -timestamp_column=$timestamp_column\
     -observation_columns=$observation_columns -file_extension=$extension\
     -timestamp_format="$timestamp_format" -d
else
    python convert2dat.py -path=$csv_path -timestamp_column=$timestamp_column\
     -observation_columns=$observation_columns -file_extension=$extension\
     -timestamp_format="$timestamp_format"
fi
printf "\ndone\n"

printf "\nuploading your .dat file on the server"
cd /usr/share/istsos
python scripts/csv2istsos.py -m 1000 -p $procedure -o $offering -u $url\
 -s $service -w $workspace

