#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 insert2geometryindex

 A script for adding new procedures geometry to your geometry index file
                              -------------------
        begin                : 2017-09-04
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

import gpxpy
import gpxpy.gpx
import argparse
from pathlib import Path
from istsosdat import standardize_norwegian


def main():
    gpx_file = open(args.__dict__['gpx_file'], 'r')

    yetImported = list()
    if Path(args.__dict__['index_file']).is_file():
        yetImported = get_imported_procedures(args.__dict__['index_file'])
        f = open(args.__dict__['index_file'], 'a')
        print('*'*20)
    else:
        f = open(args.__dict__['index_file'], 'w')
        f.write('procid,[multiple_procnames],crs,x,y\n')

    gpx = gpxpy.parse(gpx_file)

    for waypoint in gpx.waypoints:
        waypointNames = get_possible_procedure_names(waypoint)

        if not any(i in yetImported for i in waypointNames):
            names = ','.join(waypointNames)
            f.write('{},{},{}\n'.format(names,
                                        waypoint.latitude,
                                        waypoint.longitude))


def get_imported_procedures(csvFile):

    namesList = list()
    with open(csvFile, 'r') as openedCsv:
        openedCsv.readline()
        for line in openedCsv.readlines():
            for i in line.split(',')[:-2]:
                namesList.append(i)

    return namesList


def get_possible_procedure_names(procedure):
    name = standardize_norwegian(procedure.name)
    if 'TOV' in name:
        name = ''.join(name.split('TOV'))
    if 'Nyveg' in name:
        name = ''.join(name.split('Nyveg'))
    if 'NYV' in name:
        name = ''.join(name.split('NYV'))
    if 'Veg' in name:
        name = ''.join(name.split('Veg'))
    while name[0].isalpha() is False:
        name = name[1:]
    if '--' in name:
        name = '-'.join(name.split('--'))
    names = [name]
    if '-' in name:
        names.append(''.join(name.split('-')))
        names.append('_'.join(name.split('-')))
    else:
        for i in reversed(range(len(name))):
            try:
                int(name[i])
            except:
                names.append('-'.join([name[:i + 1], name[i + 1:]]))
                names.append('_'.join([name[:i + 1], name[i + 1:]]))
                break

    return names


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update a geometry index file with new procedures')

    parser.add_argument(
        '-index_file',
        type=str,
        dest='index_file',
        required=True,
        help='Path to the index file')

    parser.add_argument(
        '-gpx_file',
        type=str,
        dest='gpx_file',
        required=True,
        help='Path to the GPX file containing measured geometry of procedures')

    args = parser.parse_args()

    main()



















