#!/usr/bin/env python
"""
/***************************************************************************
 swd2dat

 Extract user's desired data from a .swd file and save them in istSOS
 acceptable format in .dat file
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

from istsosdat import *


def swd2dat(path, observationColumns, timestampColumn, timestampFormat, d):
    """
    extract user's desired data from .swd file and save them in istSOS
    acceptable format in .dat file
    :param path: path to the .csv file
    :param observationColumns: names of columns with observation data
    :param timestampColumn: name of column with timestamps
    :param timestampFormat: schema of original timestamp format
    :param d: a flag to decide whether parse just one file or whole directory
    """

    # TODO: Support -d flag
    i = open(path, 'r')
    datPath = get_dat_filepath(path[:-4])
    o = open(datPath, 'w')

    header, columnsIndexes = get_header(i.readline(),
                                        timestampColumn,
                                        observationColumns)
    o.write(header)

    i.readline()
    i.readline()

    for line in i.readlines():
        o.write(get_observations(line, timestampFormat, columnsIndexes))

    i.close()
    o.close()

# TODO: search for index.swd