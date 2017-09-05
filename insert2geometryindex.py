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
from os import sep
from istsosdat import standardize_norwegian


def main():
    if args.__dict__['d'] is True and args.__dict__['gpx_path'][-1] != sep:
        print("WARNING: Your path doesn't end with '{}'. It will parse all "
              "files beginning with '{}' and ending with 'GPX' in the path"
              "'{}{}'".format(sep,
                              args.__dict__['gpx_path'].split(sep)[-1],
                              args.__dict__['gpx_path'].rsplit(sep, 1)[0],
                              sep))

    yetImported = list()
    if Path(args.__dict__['index_file']).is_file():
        yetImported = get_imported_procedures(args.__dict__['index_file'])
        f = open(args.__dict__['index_file'], 'a')
    else:
        f = open(args.__dict__['index_file'], 'w')
        f.write('procid,[multiple_procnames],crs,x,y\n')

    if args.__dict__['d'] is False:
        gpx_file = open(args.__dict__['gpx_path'], 'r')
        gpx = gpxpy.parse(gpx_file)

        for waypoint in gpx.waypoints:
            waypointNames = get_possible_procedure_names(waypoint)

            if not any(i in yetImported for i in waypointNames):
                names = ','.join(waypointNames)
                f.write('{},33W,{},{}\n'.format(names,
                                                waypoint.latitude,
                                                waypoint.longitude))
    else:
        import glob
        files = glob.glob("{}*.gpx".format(args.__dict__['gpx_path']))
        for f in glob.glob("{}*.GPX".format(args.__dict__['gpx_path'])):
            files.append(f)

        for file in files:
            gpx_file = open(file, 'r')
            gpx = gpxpy.parse(gpx_file)

            for waypoint in gpx.waypoints:
                waypointNames = get_possible_procedure_names(waypoint)

                if not any(i in yetImported for i in waypointNames):
                    names = ','.join(waypointNames)
                    f.write('{},33W,{},{}\n'.format(names,
                                                    waypoint.latitude,
                                                    waypoint.longitude))


def get_imported_procedures(csvFile):
    """
    Get names of procedures that were imported anytime before
    :param csvFile: csvFile containing procedures geometry
    :return namesList: List of names of imported procedures
    """

    namesList = list()

    with open(csvFile, 'r') as openedCsv:
        openedCsv.readline()
        for line in openedCsv.readlines():
            for i in line.split(',')[:-3]:
                namesList.append(i)

    return namesList


def get_possible_procedure_names(procedure):
    """
    Get all often used variants of procedure name
    :param procedure: Name of procedure
    :return names: List containing mostly used variations of procedure name
    """

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
        '-gpx_path',
        type=str,
        dest='gpx_path',
        required=True,
        help='Path to the GPX file containing geometry of procedures')

    parser.add_argument(
        '-d',
        action='store_true',
        help='Use if you would like to parse all GPX files in the directory')

    args = parser.parse_args()

    main()
