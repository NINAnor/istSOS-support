#!/usr/bin/env python
"""
/***************************************************************************
 istsosdat

 A library with functions needed to create istSOS compatible .dat file
                              -------------------
        begin                : 2017-08-02
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


def get_dat_filepath(originalPath):
    """
    get the path to .dat file and give it today's timestamp suffix if not given
    :param originalPath: path to the original file
    :return: path to .dat file with timestamp as suffix
    """
    try:
        int(originalPath[-6:])
        try:
            int(originalPath[-14:])
            datPath = '{}.dat'.format(originalPath)
        except:
            if int(originalPath[-2:]) in [1, 3, 5, 7, 8, 10, 12]:
                datPath = '{}31235959000.dat'.format(originalPath)
            elif int(originalPath[-2:]) in [4, 6, 9, 11]:
                datPath = '{}30235959000.dat'.format(originalPath)
            elif int(originalPath[-6:-2]) % 4 != 0:
                datPath = '{}28235959000.dat'.format(originalPath)
            else:
                datPath = '{}29235959000.dat'.format(originalPath)

    except ValueError:
        import time
        timestampSuffix = time.strftime('%Y%m%d%H%M%S')
        datPath = '{}_{}000.dat'.format(originalPath, timestampSuffix)

    return datPath


def get_header(headerLine, timestampColumn, observationColumns):
    """
    creates istSOS compatible header for .dat file
    :param headerLine: first line of your file
    :param timestampColumn: name of column with timestamps
    :param observationColumns: names of columns with observation data
    :return header: istSOS acceptable header with user's desired columns
    :return indexes: dictionary in format {observation name: column index}
    """
    indexes = dict()
    header = str()
    index = 0

    if '\t' in headerLine:
        headerLine = headerLine.split('\t')
    elif ';' in headerLine:
        headerLine = headerLine.split(';')
    elif ',' in headerLine:
        headerLine = headerLine.split(',')

    for column in headerLine:
        if column.split('(')[0].strip() == timestampColumn:
            indexes.update(
                {'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601': index})
            header += 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,'
        elif column.split('(')[0].strip() in observationColumns.split(','):
            indexes.update({column.split('(')[0].strip(): index})
            header += '{},'.format(column.split('(')[0].strip())
        index += 1

    header = header[:-1]

    if not header.endswith('\n'):
        header += '\n'

    return header, indexes


def get_standardized_timestamp(originalTimestamp, timestampFormat):
    """
    transform given timestamp into YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM format
    :param originalTimestamp: timeStamp in original output format
    :param timestampFormat: schema of original timestamp format
    :return standardizedTimestamp: timestamp in istSOS compatible format
    """
    # TODO: Support more formats
    # TODO: Support Date and time in different columns
    # TODO: Support user's own time offset
    if timestampFormat == 'YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM':
        standardizedTimestamp = timestampFormat
    elif timestampFormat == 'YYYY-MM-DD HH:MM':
        standardizedTimestamp = '{}T{}:00.000000+01:00'.format(
            originalTimestamp[:10],
            originalTimestamp[11:])
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
    else:
        print("Your timestamp format isn't supported")

    return standardizedTimestamp


def get_observations(line, timestampFormat, columnsIndexes):
    """
    extract only desired observed properties from given line of file
    :param line: Line with all observations from the original file
    :param timestampFormat: Format in which are timestamps saved
    :param columnsIndexes: dict in format {observation name: column index}
    :return outLine: Line with desired observations separated with ','
    """
    index = 0
    columns = list()

    if '\t' in line:
        line = line.split('\t')
    elif ';' in line:
        line = line.split(';')
    elif ',' in line:
        line = line.split(',')

    for column in line:
        if index == columnsIndexes[
          'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']:
            columns.append(get_standardized_timestamp(column, timestampFormat))
        elif index in columnsIndexes.values():
            columns.append('.'.join(column.split(',')))
        index += 1

    outLine = ','.join(columns)
    if not outLine.endswith('\n'):
        outLine += '\n'

    return outLine


def get_metadata(indexFile):
    """
    Load observation columns names from template file in param format
    :param indexFile: Path to file with template of observation columns names
    :return observationColumns: Observation columns names from template file
    """
    print('Using file {} as a template for names of observation '
          'columns'.format(indexFile))
    observationColumns = list()

    i = open(indexFile, 'r')

    for line in i.readlines():
        observationColumn = line.split('\t')[1].split('(')[0]
        observationColumns.append(observationColumn.strip())

    observationColumns = ','.join(observationColumns)

    i.close()

    return observationColumns
