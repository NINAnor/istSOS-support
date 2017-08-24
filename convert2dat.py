#!/usr/bin/env python
"""
/***************************************************************************
 convert2dat

 Extract user's desired data from his file and save them in istSOS
 acceptable format in .dat file
                              -------------------
        begin                : 2017-07-30 (funny, it's my birthday)
        author               : Ondrej Pesek
        email                : pesej.ondrek@gmail.com
        copyright            : (C) Norwegian Institute for Nature Research
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import argparse
from os import sep
from scripts.csv2dat import csv2dat
from scripts.swd2dat import swd2dat
from scripts.xls2dat import xls2dat


def main():
    if args.__dict__['d'] is True and args.__dict__['path'][-1] != sep:
        print("WARNING: Your path doesn't end with '{}'. It will parse all "
              "files beginning with '{}' and ending with '{}' in the path"
              "'{}{}'".format(sep,
                              args.__dict__['path'].split(sep)[-1],
                              args.__dict__['file_extension'],
                              args.__dict__['path'].rsplit(sep, 1)[0],
                              sep))

    if 'csv' in args.__dict__['file_extension'] or \
                    'CSV' in args.__dict__['file_extension']:
        csv2dat(args.__dict__['path'],
                args.__dict__['observation_columns'],
                args.__dict__['timestamp_column'],
                args.__dict__['timestamp_format'],
                args.__dict__['timestamp_offset'],
                args.__dict__['procedure'],
                args.__dict__['d'])
    elif 'swd' in args.__dict__['file_extension'] or \
                    'SWD' in args.__dict__['file_extension']:
        swd2dat(args.__dict__['path'],
                args.__dict__['observation_columns'],
                args.__dict__['timestamp_column'],
                args.__dict__['timestamp_format'],
                args.__dict__['timestamp_offset'],
                args.__dict__['procedure'],
                args.__dict__['d'],
                args.__dict__['t'])
    elif 'xls' in args.__dict__['file_extension'] or \
                    'XLS' in args.__dict__['file_extension']:
        xls2dat(args.__dict__['path'],
                args.__dict__['timestamp_column'],
                args.__dict__['timestamp_format'],
                args.__dict__['timestamp_offset'],
                args.__dict__['procedure'],
                args.__dict__['d'])
    else:
        print("END: Your file extension is not supported")


if __name__ == '__main__':
    timestampFormats = ['YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM', 'YYYYMMDD',
                        'DD.MM.YYYY', 'DD.MM.YY HH:MM:SS', 'YYYYMMDDHH',
                        'DD.MM.YY HH:MM:SS AM/PM', 'YYYY-MM-DD HH:MM',
                        'DATE+TIME']

    parser = argparse.ArgumentParser(
        description='Import data from a file (or files) on an istSOS server.')

    parser.add_argument(
        '-path',
        type=str,
        dest='path',
        required=True,
        help='Path to a file with observations '
             '(only working directory with files when using -d flag)')

    parser.add_argument(
        '-file_extension',
        dest='file_extension',
        default='.SWD',
        help='Extension of files with observations '
             '(not necessary when not using -d flag)')

    parser.add_argument(
        '-observation_columns',
        type=str,
        dest='observation_columns',
        help='Name of columns with observations (separated with ",")')

    parser.add_argument(
        '-timestamp_column',
        type=str,
        dest='timestamp_column',
        default='urn:ogc:def:parameter:x-istsos:1.0:time:iso8601',
        help='Name of the column with timestamps')

    parser.add_argument(
        '-timestamp_format',
        type=str,
        default='YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM',
        choices=timestampFormats,
        help='Format in which timestamps are provided')

    parser.add_argument(
        '-timestamp_offset',
        type=str,
        default='+01:00',
        help='Offset of timestamp in format +HH:MM')

    parser.add_argument(
        '-procedure',
        type=str,
        help='Who provides the observations')

    parser.add_argument(
        '-d',
        action='store_true',
        help='Use if you would like to convert all files with defined'
             'extension in the directory')

    parser.add_argument(
        '-t',
        action='store_true',
        help='Use template for observation_columns names (INDEX.SWD)')

    args = parser.parse_args()

    main()
