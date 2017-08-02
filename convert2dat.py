#!/usr/bin/env python
"""
/***************************************************************************
 convert2dat

 Extract user's desired data from his file and save them in istSOS
 acceptable format in .dat file
                              -------------------
        begin                : 2017-07-30
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
from csv2dat import *


if __name__ == '__main__':
    timestampFormats = ['YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM', 'YYYYMMDD',
                        'DD.MM.YYYY', 'DD.MM.YY HH:MM:SS', 'YYYYMMDDHH',
                        'DD.MM.YY HH:MM:SS AM/PM']

    parser = argparse.ArgumentParser(
        description='Import data from a csv file on an istSOS server.')

    parser.add_argument(
        '-path',
        type=str,
        dest='path',
        required=True,
        help='Path to CSV file with observations '
             '(only working directory with files when using -d flag)')

    # TODO: .csv shouldn't be default extension!
    parser.add_argument(
        '-file_extension',
        dest='file_extension',
        default='.csv',
        help='Extension of file with observations '
             '(not necessary when not using -d flag)')

    parser.add_argument(
        '-observation_columns',
        type=str,
        dest='observation_columns',
        required=True,
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
        '-d',
        action='store_true',
        help='Use if you would like to convert all .csv files in your '
             'directory')

    args = parser.parse_args()

    print(args.__dict__)

    if 'csv' in args.__dict__['file_extension']:
        csv2dat(args.__dict__)
    else:
        print("Your file extension isn't supported")