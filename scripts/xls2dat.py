#!/usr/bin/env python
"""
/***************************************************************************
 swd2dat

 Extract user's desired data from a .xls file and save them in istSOS
 acceptable format in .dat file
                              -------------------
        begin                : 2017-08-23
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

import xlrd
from os import sep
from istsosdat import *

def xls2dat(path, dateColumn, timestampFormat, offset, procedure, d):
    """
    extract user's desired data from .swd file and save them in istSOS
    acceptable format in .dat file
    :param path: path to the .csv file
    :param dateColumn: name of column with dates
    :param timestampFormat: schema of original timestamp format
    :param offset: offset of timestamp
    :param procedure: who provides the observations
    :param d: a flag to decide whether parse just one file or whole directory
    """

    if d is False:
        xlWorkbook = xlrd.open_workbook(path)
        xlSheet = xlWorkbook.sheet_by_index(0)
        fileLength = xlSheet.nrows

        firstRow = list()
        for column in xlSheet.row(3):
            if column.ctype:
                firstRow.append(column.value)

        datPath = get_dat_filepath(path[:-4], procedure)
        o = open(datPath, 'w')

        if timestampFormat == 'DATE+TIME':
            observationColumns = list(firstRow)
            observationColumns.remove('Date')
            observationColumns.remove('Time')
            for i in ['Month', 'Year', 'Tre-id']:
                if i in observationColumns:
                    observationColumns.remove(i)

            header, columnsIndexes, timeColumnIndex = get_header(
                ','.join(firstRow), dateColumn, ','.join(observationColumns),
                'Time')
        else:
            header, columnsIndexes = get_header(','.join(firstRow), dateColumn,
                                                ','.join(firstRow))
        o.write(header)

        columnsMax = max(columnsIndexes.values()) + 1

        for rowIndex in range(4, fileLength):
            cells = list()
            for colIndex in range(columnsMax):
                cell = xlSheet.cell(rowIndex, colIndex).value
                if not isinstance(cell, unicode):
                    cell = str(cell)
                cells.append(cell)

            dateIndex = columnsIndexes[
                'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']
            cells[dateIndex] = 'DATE{}TIME{}'.format(cells[dateIndex],
                                                     cells[timeColumnIndex])
            o.write(get_observations('\t'.join(cells), timestampFormat, offset,
                                     columnsIndexes))

        o.close()
    else:
        import glob
        files = glob.glob("{}*.xls".format(path))
        for f in glob.glob("{}*.XLS".format(path)):
            files.append(f)

        for file in files:
            xlWorkbook = xlrd.open_workbook(file)
            xlSheet = xlWorkbook.sheet_by_index(0)
            fileLength = xlSheet.nrows

            firstRow = list()
            for column in xlSheet.row(3):
                if column.ctype:
                    firstRow.append(column.value)

            datPath = get_dat_filepath(file[:-4], procedure)
            o = open(datPath, 'w')

            if timestampFormat == 'DATE+TIME':
                observationColumns = list(firstRow)
                observationColumns.remove('Date')
                observationColumns.remove('Time')
                for i in ['Month', 'Year', 'Tre-id']:
                    if i in observationColumns:
                        observationColumns.remove(i)

                header, columnsIndexes, timeColumnIndex = get_header(
                    ','.join(firstRow), dateColumn,
                    ','.join(observationColumns),
                    'Time')
            else:
                header, columnsIndexes = get_header(','.join(firstRow),
                                                    dateColumn,
                                                    ','.join(firstRow[2:]))
            o.write(header)

            columnsMax = max(columnsIndexes.values()) + 1

            for rowIndex in range(4, fileLength):
                cells = list()
                for colIndex in range(columnsMax):
                    cell = xlSheet.cell(rowIndex, colIndex).value
                    if not isinstance(cell, unicode):
                        cell = str(cell)
                    cells.append(cell)

                    dateIndex = columnsIndexes[
                        'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']
                    cells[dateIndex] = 'DATE{}TIME{}'.format(
                        cells[dateIndex], cells[timeColumnIndex])
                o.write(get_observations('\t'.join(cells), timestampFormat,
                                         offset, columnsIndexes))

            o.close()