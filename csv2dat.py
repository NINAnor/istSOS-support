#!/usr/bin/env python
"""
/***************************************************************************
 csv2dat

 Extract user's desired data from a .csv file and save them in istSOS
 acceptable format in .dat file
                              -------------------
        begin                : 2017-07-24
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


def csv2dat(options):
    """
    extract user's desired data from .csv file and save them in istSOS
    acceptable format in .dat file
    :param options: parameters given with running this script
    """
    if options['d'] is False:
        i = open(options['path'], 'r')
        datPath = get_dat_filepath(options['path'][:-4])
        o = open(datPath, 'w')

        header, columnsIndexes = get_header(i.readline(),
                                            options['timestamp_column'],
                                            options['observation_columns'])
        o.write(header)

        for line in i.readlines():
            o.write(get_observations(line, options['timestamp_format'],
                                     columnsIndexes))

        i.close()
        o.close()
    else:
        import glob
        files = glob.glob("{}*.csv".format(options['path']))
        for file in files:
            i = open(file, 'r')
            datPath = get_dat_filepath(file[:-4])
            o = open(datPath, 'w')

            header, columnsIndexes = get_header(i.readline(),
                                                options['timestamp_column'],
                                                options['observation_columns'])
            o.write(header)

            for line in i.readlines():
                o.write(get_observations(line, options['timestamp_format'],
                                         columnsIndexes))

            i.close()
            o.close()


def get_dat_filepath(csvPath):
    """
    get the path to .dat file and give it today's timestamp suffix if not given
    :param csvPath: path to the .csv file
    :return: path to .dat file with timestamp as suffix
    """
    try:
        int(csvPath[-14:])
        datPath = '{}.dat'.format(csvPath)
    except ValueError:
        import time
        timestampSuffix = time.strftime('%Y%m%d%H%M%S.dat')
        datPath = '{}_{}'.format(csvPath, timestampSuffix)

    return datPath


def get_header(headerLine, timestampColumn, observationColumns):
    """
    creates istSOS acceptable header for .dat file
    :param headerLine: first line of .csv file
    :param timestampColumn: name of column with timestamps
    :param observationColumns: names of columns with observation data
    :return header: istSOS acceptable header with user's desired columns
    :return indexes: dictionary in format {observation name: column index}
    """
    if ';' in headerLine:
        headerLine = headerLine.split(';')
    else:
        headerLine = headerLine.split(',')

    indexes = dict()
    header = str()
    index = 0
    for column in headerLine:
        if column.strip() == timestampColumn:
            indexes.update(
                {'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601': index})
            header += 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,'
        elif column.strip() in observationColumns.split(','):
            indexes.update({column.strip(): index})
            header += '{},'.format(column.strip())
        index += 1

    header = header[:-1]

    if not header.endswith('\n'):
        header += '\n'

    return header, indexes


def get_observations(line, timestampFormat, columnsIndexes):
    """
    extract only desired observed properties from given line of .csv file
    :param line: Line with all observations from .csv file
    :param timestampFormat: Format in which are timestamps saved
    :param columnsIndexes: dict in format {observation name: column index}
    :return outLine: Line with desired observations separated with ','
    """
    index = 0
    columns = list()

    if ';' in line:
        line = line.split(';')
    else:
        line = line.split(',')

    for column in line:
        if index in columnsIndexes.values():
            if index == columnsIndexes[
              'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']:
                columns.append(get_standardized_timestamp(column,
                                                          timestampFormat))
            else:
                columns.append(column)
        index += 1

    outLine = ','.join(columns)
    if not outLine.endswith('\n'):
        outLine += '\n'

    return outLine


def get_standardized_timestamp(originalTimestamp, timestampFormat):
    """
    transform given timestamp into YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM format
    :param originalTimestamp: timeStamp in original output format
    :param timestampFormat: schema of original timestamp format
    :return standardizedTimestamp: timestamp in istSOS acceptable format
    """
    # TODO: Support more formats
    if timestampFormat == 'YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM':
        standardizedTimestamp = timestampFormat
    elif timestampFormat == 'YYYYMMDD':
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000+01:00'.format(
            originalTimestamp[:4],
            originalTimestamp[4:6],
            originalTimestamp[6:])
    elif timestampFormat == 'YYYYMMDDHH':
        standardizedTimestamp = '{}-{}-{}T{}:00:00.000000+01:00'.format(
            originalTimestamp[:4],
            originalTimestamp[4:6],
            originalTimestamp[6:8],
            originalTimestamp[8:])
    elif timestampFormat == 'DD.MM.YYYY':
        originalTimestamp = originalTimestamp.split('.')
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000+01:00'.format(
            originalTimestamp[2],
            originalTimestamp[1],
            originalTimestamp[0])
    elif timestampFormat == 'DD.MM.YY HH:MM:SS':
        import time
        thisYear = time.strftime('%Y')

        timestampParts = [originalTimestamp[:2], originalTimestamp[3:5],
                          originalTimestamp[6:8], originalTimestamp[9:11],
                          originalTimestamp[12:14], originalTimestamp[15:17]]

        if int(timestampParts[2]) <= int(thisYear[2:]):
            timestampParts[2] = '20{}'.format(timestampParts[2])
        else:
            timestampParts[2] = '19{}'.format(timestampParts[2])

        standardizedTimestamp = '{}-{}-{}T{}:{}:{}.000000+01:00'.format(
            timestampParts[2], timestampParts[1],
            timestampParts[0], timestampParts[3],
            timestampParts[4], timestampParts[5])
    elif timestampFormat == 'DD.MM.YY HH:MM:SS AM/PM':
        import time
        thisYear = time.strftime('%Y')

        timestampParts = [originalTimestamp[:2], originalTimestamp[3:5],
                          originalTimestamp[6:8], originalTimestamp[9:11],
                          originalTimestamp[12:14], originalTimestamp[15:17]]

        if originalTimestamp[-2:] == 'PM':
            timestampParts[3] = str(int(originalTimestamp[9:11]) + 12)
        if int(timestampParts[2]) <= int(thisYear[2:]):
            timestampParts[2] = '20{}'.format(timestampParts[2])
        else:
            timestampParts[2] = '19{}'.format(timestampParts[2])

        standardizedTimestamp = '{}-{}-{}T{}:{}:{}.000000+01:00'.format(
            timestampParts[2], timestampParts[1],
            timestampParts[0], timestampParts[3],
            timestampParts[4], timestampParts[5])

    return standardizedTimestamp


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
        help='Path to CSV file with observations'
             '(only working directory with files when using -d)')

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

    csv2dat(args.__dict__)
