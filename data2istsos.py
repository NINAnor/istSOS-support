#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 data2istsos

 A starter script for feeding your istsos server with data from your
 device (sensor).
                              -------------------
        begin                : 2017-08-07
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
import os
import subprocess
import glob
from sys import exit
from istsosdat import standardize_norwegian, get_procedure_id


def main():
    walk_dir = args.__dict__['path']

    # TODO: See issue about changing csv to something better
    geometryIndex = args.__dict__['geometry_index']
    if geometryIndex[-4:] != '.csv':
        geometryIndex = '{}_{}.csv'.format(args.__dict__['geometry_index'],
                                           args.__dict__['service'])

    if args.__dict__['device_type'] == 'templogger':
        procedureDirectories = {'hoydegradient': list(), 'lemenplott': list(),
                                'templogstasjoner': list()}
        for root, subdirs, files in os.walk(walk_dir):
            for sd in subdirs:
                if ('Høydegradient' in root or 'høydegradient' in root or
                    'HЫydegradient' in root or 'hЫydegradient' in root) and \
                                os.path.join(root, sd) not in \
                                procedureDirectories['hoydegradient']:
                    procedureDirectories['hoydegradient'].append(
                        os.path.join(root, sd, ''))
                elif ('Lemenplott' in root or 'lemenplott' in root) and \
                                os.path.join(root, sd) not in \
                                procedureDirectories['lemenplott']:
                    procedureDirectories['lemenplott'].append(
                        os.path.join(root, sd, ''))
                elif ('Templogstasjoner' in root or
                              'templogstasjoner' in root) and \
                                os.path.join(root, sd) not in \
                                procedureDirectories['templogstasjoner']:
                    procedureDirectories['templogstasjoner'].append(
                        os.path.join(root, sd, ''))
    elif args.__dict__['device_type'] == 'TOV':
        procedureDirectories = dict()
        for root, subdirs, files in os.walk(walk_dir):
            if subdirs == []:
                obsFiles = [f for f in files if f[-4:] == '.xls']
                offering = standardize_norwegian(root.split(os.sep)[-2])
                if offering not in procedureDirectories.keys():
                    procedureDirectories.update({offering: {root: obsFiles}})
                else:
                    procedureDirectories[offering].update({root: obsFiles})

    create_dats(procedureDirectories, geometryIndex)

    if args.__dict__['u'] is True:
        upload_data(procedureDirectories, geometryIndex)

    if args.__dict__['f'] is True:
        delete_dat_files(procedureDirectories, geometryIndex)


def create_dats(procedureDirectories, geometryIndex):
    """
    create .dat files from all output files from your device
    :param procedureDirectories: Dictionary of directories containing data
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    """

    if args.__dict__['device_type'] == 'templogger':
        fileExtension = 'swd'
    elif args.__dict__['device_type'] == 'TOV':
        fileExtension = 'xls'

    for off in procedureDirectories.keys():
        if fileExtension == 'swd':
            for observationsPath in procedureDirectories[off]:
                procedureNick = observationsPath.split(os.sep)[-2]
                procedure = get_procedure_id(procedureNick, geometryIndex)

                p = subprocess.call(
                    ['python',
                     'convert2dat.py',
                     '-path={}'.format(observationsPath),
                     '-timestamp_column={}'.format(procedureNick),
                     '-timestamp_format=YYYY-MM-DD HH:MM',
                     '-procedure={}'.format(procedure),
                     '-file_extension={}'.format(fileExtension),
                     '-d',
                     '-t'])

                if p != 0:
                    print('Unexpected error. Execution stopped')
                    delete_dat_files(procedureDirectories)
                    exit(1)
        elif fileExtension == 'xls':
            for year in procedureDirectories[off].keys():
                for procedureNick in procedureDirectories[off][year]:
                    procedure = get_procedure_id(procedureNick[:-4],
                                                 geometryIndex)
                    p = subprocess.call([
                        'python',
                        'convert2dat.py',
                        '-path={}{}{}'.format(year, os.sep, procedureNick),
                        '-timestamp_column=Date',
                        '-timestamp_format=DATE+TIME',
                        '-procedure={}'.format(procedure),
                        '-file_extension={}'.format(fileExtension)
                        ])

                    if p != 0:
                        print('Unexpected error. Execution stopped')
                        delete_dat_files(procedureDirectories)
                        exit(1)


def upload_data(procedureDirectories, geometryIndex):
    """
    Upload data from .dat files to your istSOS server
    :param procedureDirectories: Dictionary of directories containing data
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    """

    for off in procedureDirectories.keys():
        if args.__dict__['device_type'] == 'templogger':
            for observationsPath in procedureDirectories[off]:
                procedure = get_procedure_id(
                    observationsPath.split(os.sep)[-2],
                    geometryIndex)

                subprocess.call(
                    ['python',
                     'scripts/csv2istsos.py',
                     '-w={}'.format(os.path.abspath(observationsPath)),
                     '-s={}'.format(args.__dict__['service']),
                     '-u={}'.format(args.__dict__['url']),
                     '-o={}'.format(off),
                     '-p={}'.format(procedure),
                     '-user={}'.format(args.__dict__['username']),
                     '-password={}'.format(args.__dict__['password'])],
                    cwd=args.__dict__['istsos_path'])
        elif args.__dict__['device_type'] == 'TOV':
            for year in procedureDirectories[off].keys():
                for procedureNick in procedureDirectories[off][year]:
                    procedure = get_procedure_id(procedureNick[:-4],
                                                 geometryIndex)
                    subprocess.call(
                        ['python',
                         'scripts/csv2istsos.py',
                         '-w={}'.format(os.path.abspath(
                             '{}{}'.format(year, os.sep))),
                         '-s={}'.format(args.__dict__['service']),
                         '-u={}'.format(args.__dict__['url']),
                         '-o={}'.format(off),
                         '-p={}'.format(procedure),
                         '-user={}'.format(args.__dict__['username']),
                         '-password={}'.format(args.__dict__['password'])],
                        cwd=args.__dict__['istsos_path'])


def delete_dat_files(procedureDirectories, geometryIndex):
    """
    Delete .dat files created as intermediates in data folders
    :param procedureDirectories: Dictionary of directories containing data
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    """

    for off in procedureDirectories.keys():
        if args.__dict__['device_type'] == 'templogger':
            for observationsPath in procedureDirectories[off]:
                procedure = get_procedure_id(
                    observationsPath.split(os.sep)[-2],
                    geometryIndex)
                files = glob.glob('{}{}*.dat'.format(observationsPath,
                                                     procedure))
                for f in files:
                    os.remove(f)
        elif args.__dict__['device_type'] == 'TOV':
            for year in procedureDirectories[off].keys():
                files = glob.glob('{}{}*.dat'.format(year, os.sep))
                for f in files:
                    os.remove(f)


if __name__ == '__main__':
    supportedDevices = ['templogger', 'TOV']

    parser = argparse.ArgumentParser(
        description='Import devices outputs on an istSOS server.')

    parser.add_argument(
        '-path',
        type=str,
        dest='path',
        required=True,
        help='Path to a directory containing observations')

    parser.add_argument(
        '-device_type',
        type=str,
        choices=supportedDevices,
        help='Type of your device (mostly sensor)')

    parser.add_argument(
        '-geometry_index',
        type=str,
        default=os.path.join(os.path.dirname(__file__),
                             'metadata',
                             'geometry_index'),
        help='Path to the CSV file with sensors metadata '
             '(names, crs, coordinates)')

    parser.add_argument(
        '-url',
        type=str,
        help='istSOS Server address IP or domain name')

    parser.add_argument(
        '-service',
        type=str,
        help='The name of the service instance')

    parser.add_argument(
        '-istsos_path',
        type=str,
        default='/usr/share/istsos/',
        help='Path to a directory where is istsos installed in your computer')

    parser.add_argument(
        '-username',
        type=str,
        help='Username used to access istSOS server')

    parser.add_argument(
        '-password',
        type=str,
        help='Password used to access istSOS server')

    parser.add_argument(
        '-u',
        action='store_true',
        help='Upload converted data to a server (url parameter is required)')

    parser.add_argument(
        '-f',
        action='store_true',
        help='Force deletion of intermediates .dat files after execution')

    args = parser.parse_args()

    if args.__dict__['service'] == '' or args.__dict__['service'] is None:
        args.__dict__['service'] = parser.parse_args().__dict__['device_type']

    if args.__dict__['path'][-1] != os.sep:
        print("WARNING: Your path doesn't end with '{}'. It will parse all "
              "directories beginning with '{}' in the path "
              "'{}{}'".format(os.sep,
                              args.__dict__['path'].split(os.sep)[-1],
                              args.__dict__['path'].rsplit(os.sep, 1)[0],
                              os.sep))

    main()
