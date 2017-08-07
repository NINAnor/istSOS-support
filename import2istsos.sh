#!/bin/bash

# Usage info
show_help() {
cat << EOF

Import data from a csv file on an istSOS server.

Usage:
 bash import2istsos.sh file_path=* [file_extension=*] observation_columns=*
                       [timestamp_column=*] [timestamp_offset=*]
                       [timestamp_format=*] url=* service=* offering=*
                       procedure=*

Flags:
  -h, -?, --help   Show this help message and exit
              -d   Use if you would like to convert all .csv files in your
                   directory
              -t   Use template for observation_columns names (INDEX.SWD)

Parameters:
            file_path  Path to a file with observations
                       (only working directory with files when using -d)
       file_extension  Extension of files with observations
                       (required when using -d flag)
  observation_columns  Name of columns with observations (separated with ',')
                       (not required when using SWD file extension and -t flag)
     timestamp_column  Name of the column with timestamps
                       default: urn:ogc:def:parameter:x-istsos:1.0:time:iso8601
     timestamp_offset  Offset of timestamp in format +HH:MM
     timestamp_format  Format in which timestamps are provided
                       default: YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM
                  url  istSOS Server address IP or domain name
              service  The name of the service instance
             offering  A collection of sensor used to conveniently
                       group them up
            procedure  Who provides the observations
EOF
}

set -e

timestamp_column='urn:ogc:def:parameter:x-istsos:1.0:time:iso8601'
timestamp_format='YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM'
timestamp_offset='+01:00'
extension='swd'
directory=false
template=false

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
        -t)
            template=true
            ;;
        file_path=*)
            file_path="${i#*=}"
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
        timestamp_offset=*)
            timestamp_offset="${i#*=}"
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

workspace=${file_path%/*}

printf "creating .dat from your file\n"
if $directory;
then
    if $template;
    then
        python convert2dat.py -path=$file_path\
         -timestamp_column=$timestamp_column\
         -observation_columns=$observation_columns -file_extension=$extension\
         -timestamp_format="$timestamp_format"\
         -timestamp_offset=$timestamp_offset -procedure=$procedure -d\
          -t | grep "Your file extension is not supported" && exit 1
    else
        python convert2dat.py -path=$file_path\
         -timestamp_column=$timestamp_column\
         -observation_columns=$observation_columns -file_extension=$extension\
         -timestamp_format="$timestamp_format"\
         -timestamp_offset=$timestamp_offset -procedure=$procedure\
         -d | grep "Your file extension is not supported" && exit 1
    fi
else
    if $template;
    then
        python convert2dat.py -path=$file_path
         -timestamp_column=$timestamp_column\
         -observation_columns=$observation_columns -file_extension=$extension\
         -timestamp_format="$timestamp_format"\
         -timestamp_offset=$timestamp_offset -t
    else
        python convert2dat.py -path=$file_path
         -timestamp_column=$timestamp_column\
         -observation_columns=$observation_columns -file_extension=$extension\
         -timestamp_format="$timestamp_format"\
         -timestamp_offset=$timestamp_offset
    fi
fi
printf "\ndone\n"

printf "\nuploading your .dat file on the server"
cd /usr/share/istsos
python scripts/csv2istsos.py -m 1000 -p $procedure -o $offering -u $url\
 -s $service -w $workspace

