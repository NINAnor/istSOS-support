#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from os import sep


def get_dat_filepath(originalPath, procedure=None):
    """
    get the path to .dat file and give it today's timestamp suffix if not given
    :param originalPath: path to the original file
    :param procedure: who provides the observations
    :return datPath: path to .dat file with timestamp as suffix
    """

    try:
        int(originalPath[-6:])
        try:
            int(originalPath[-14:])
            if procedure:
                prefix = '{}{}{}'.format(originalPath.rsplit(sep, 1)[0],
                                         sep,
                                         procedure)
            else:
                prefix = originalPath[:-17]
            datPath = '{}{}.dat'.format(prefix, originalPath[-17:])
        except:
            if procedure:
                prefix = '{}{}{}_{}'.format(originalPath.rsplit(sep, 1)[0],
                                            sep,
                                            procedure,
                                            originalPath[-6:])
            else:
                prefix = originalPath
            if int(originalPath[-2:]) in [1, 3, 5, 7, 8, 10, 12]:
                datPath = '{}31235959000.dat'.format(prefix)
            elif int(originalPath[-2:]) in [4, 6, 9, 11]:
                datPath = '{}30235959000.dat'.format(prefix)
            elif int(originalPath[-6:-2]) % 4 != 0:
                datPath = '{}28235959000.dat'.format(prefix)
            else:
                datPath = '{}29235959000.dat'.format(prefix)

    except ValueError:
        import time
        timestampSuffix = time.strftime('%Y%m%d%H%M%S')

        if procedure:
            prefix = '{}{}{}'.format(originalPath.rsplit(sep, 1)[0],
                                     sep,
                                     standardize_norwegian(procedure))
        else:
            prefix = originalPath

        datPath = '{}{}000.dat'.format(prefix, timestampSuffix)

    if datPath[-22] != '_':
        datPath = '{}_{}'.format(datPath[:-21], datPath[-21:])

    return datPath


def get_header(headerLine, timestampColumn, observationColumns,
               timeColumn=None):
    """
    creates istSOS compatible header for .dat file
    :param headerLine: First line of your file
    :param timestampColumn: Name of column with timestamps (or dates)
    :param observationColumns: Names of columns with observation data
    :param timeColumn: Name of column with times if date and time in separates
    :return header: istSOS acceptable header with user's desired columns
    :return indexes: dictionary in format {observation name: column index}
    :return timeColumnIndex: index of column with times if they are separated
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
        if column == standardize_norwegian(timestampColumn, shorten=True):
            indexes.update(
                {'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601': index})
            header += 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,'
        elif column.split('(')[0].strip() in observationColumns.split(','):
            indexes.update({column.split('(')[0].strip(): index})
            header += '{},'.format(column.split('(')[0].strip())
        elif timeColumn and column.split('(')[0].strip() == timeColumn:
            timeColumnIndex = index

        index += 1

    header = header[:-1]

    if not header.endswith('\n'):
        header += '\n'

    if not timeColumn:
        return header, indexes
    else:
        return header, indexes, timeColumnIndex


def get_standardized_timestamp(originalTimestamp, timestampFormat, offset):
    """
    transform given timestamp into YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM format
    :param originalTimestamp: timeStamp in original output format
    :param timestampFormat: schema of original timestamp format
    :param offset: offset of timestamp
    :return standardizedTimestamp: timestamp in istSOS compatible format
    """

    # TODO: Support more formats
    if timestampFormat == 'YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM':
        standardizedTimestamp = timestampFormat
    elif timestampFormat == 'YYYY-MM-DD HH:MM':
        standardizedTimestamp = '{}T{}:00.000000{}'.format(
            originalTimestamp[:10],
            originalTimestamp[11:],
            offset)
    elif timestampFormat == 'YYYYMMDD':
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000{}'.format(
            originalTimestamp[:4],
            originalTimestamp[4:6],
            originalTimestamp[6:],
            offset)
    elif timestampFormat == 'DATE+TIME':
        standardizedTimestamp = '{}-{}-{}T{}:{}:{}.000000{}'.format(
            originalTimestamp[10:14],
            originalTimestamp[7:9],
            originalTimestamp[4:6],
            originalTimestamp[18:20],
            originalTimestamp[21:23],
            originalTimestamp[24:26],
            offset)
    elif timestampFormat == 'YYYYMMDDHH':
        standardizedTimestamp = '{}-{}-{}T{}:00:00.000000{}'.format(
            originalTimestamp[:4],
            originalTimestamp[4:6],
            originalTimestamp[6:8],
            originalTimestamp[8:],
            offset)
    elif timestampFormat == 'DD.MM.YYYY':
        originalTimestamp = originalTimestamp.split('.')
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000{}'.format(
            originalTimestamp[2],
            originalTimestamp[1],
            originalTimestamp[0],
            offset)
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

        standardizedTimestamp = '{}-{}-{}T{}:{}:{}.000000{}'.format(
            timestampParts[2], timestampParts[1],
            timestampParts[0], timestampParts[3],
            timestampParts[4], timestampParts[5], offset)
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

        standardizedTimestamp = '{}-{}-{}T{}:{}:{}.000000{}'.format(
            timestampParts[2], timestampParts[1],
            timestampParts[0], timestampParts[3],
            timestampParts[4], timestampParts[5], offset)
    else:
        print("Your timestamp format isn't supported")

    return standardizedTimestamp


def get_observations(line, timestampFormat, offset, columnsIndexes):
    """
    extract only desired observed properties from given line of file
    :param line: Line with all observations from the original file
    :param timestampFormat: Format in which are timestamps saved
    :param offset: offset of timestamp
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

    try:
        for column in line:
            if index == columnsIndexes[
              'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']:
                columns.append(get_standardized_timestamp(column,
                                                          timestampFormat,
                                                          offset))
            elif index in columnsIndexes.values():
                columns.append('.'.join(column.split(',')))
            index += 1
    except KeyError as e:
        print('\nKEY ERROR ({}): Column not found\nTry to check index files '
              'or observation_columns inputs\n'.format(e.__str__()))
        raise e

    outLine = ','.join(columns)
    if not outLine.endswith('\n'):
        outLine += '\n'

    return outLine


def get_metadata(indexFile, returnUnits=False):
    """
    Load observation columns names from template file in param format
    :param indexFile: Path to file with template of observation columns names
    :param returnUnits: boolean to decide whether return also units
    :return observationColumns: Observation columns names from template file
    """

    print('Using file {} as a template for names of observation '
          'columns'.format(indexFile))
    observationColumns = list()

    if indexFile[-3:] == 'SWD':
        i = open(indexFile, 'r')

        for line in i.readlines():
            if returnUnits is False:
                observationColumn = line.split('\t')[1].split('(')[0]
            else:
                observationColumn = line.split('\t')[1]
                if '*' in observationColumn:
                    observationColumn = '°'.join(observationColumn.split('*'))
            observationColumns.append(observationColumn.strip())

        i.close()
    elif indexFile[-3:] == 'xls':
        import xlrd

        xlWorkbook = xlrd.open_workbook(indexFile)
        xlSheet = xlWorkbook.sheet_by_index(0)

        for column in xlSheet.row(3):
            if column.ctype:
                value = column.value
                if value == 'Temperature' or value == 'Dew Point':
                    observationColumns.append('{} (°C)'.format(value))
                elif value == 'Humidity':
                    observationColumns.append('{} (%)'.format(value))

    observationColumns = ','.join(observationColumns)

    return observationColumns

def get_procedure_id(procedureName, geometryIndex):
    """
    Find name of sensor used on the server for given name used in archive
    :param procedureName: Name of the procedure used in archive
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    :return: Name of procedure for server usage
    """

    procedureName = standardize_norwegian(procedureName)

    with open(geometryIndex, 'r') as geometry:
        for line in geometry.readlines():
            lineFeatures = line.split(',')
            if procedureName in lineFeatures or \
                            '{}-temp'.format(procedureName) in lineFeatures:
                return lineFeatures[0]

def standardize_norwegian(word, shorten=False):
    """
    Convert word containing norwegian characters to istSOS acceptable standard
    :param shorten: return input string with missing norwegian characters
    """

    if shorten is False:
        if 'ø' in word:
            word = 'o'.join(word.split('ø'))
        if 'Ø' in word:
            word = 'o'.join(word.split('Ø'))
        if 'æ' in word:
            word = 'ae'.join(word.split('æ'))
        if 'å' in word:
            word = 'a'.join(word.split('å'))
        if 'Ы' in word:
            word = 'o'.join(word.split('Ы'))
        if 'Э' in word:
            word = 'O'.join(word.split('Э'))
        if 'Ж' in word:
            word = 'a'.join(word.split('Ж'))
        if 'П' in word:
            word = 'A'.join(word.split('П'))
        if 'Å' in word:
            word = 'A'.join(word.split('Å'))
    else:
        if 'ø' in word:
            word = ''.join(word.split('ø'))
        if 'Ø' in word:
            word = ''.join(word.split('Ø'))
        if 'æ' in word:
            word = ''.join(word.split('æ'))
        if 'å' in word:
            word = ''.join(word.split('å'))
        if 'Ы' in word:
            word = ''.join(word.split('Ы'))
        if 'Э' in word:
            word = ''.join(word.split('Э'))
        if 'Ж' in word:
            word = ''.join(word.split('Ж'))
        if 'П' in word:
            word = ''.join(word.split('П'))
        if 'Å' in word:
            word = ''.join(word.split('Å'))

    return word
