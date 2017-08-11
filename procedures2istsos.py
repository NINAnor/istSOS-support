#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 procedures2istsos

 A script for adding all your procedures on your istSOS server
                              -------------------
        begin                : 2017-08-10
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

import requests
import json
import argparse
import os
import istsosdat


def main():

    insert_procedures(args.__dict__['url'], args.__dict__['path'], args.__dict__['device_type'])


def insert_procedures(url, procedurePath, deviceType):
    walk_dir = procedurePath
    proceduresURL = '{}wa/istsos/services/{}/procedures'.format(url, deviceType)

    for root, subdirs, files in os.walk(walk_dir):
        if subdirs == []:
            observedProperties = get_observed_properties(root)
            location = get_location(root.split(os.sep)[-2].split(' ')[-1],
                                    root.split(os.sep)[-1])

            procedure = {
                'system_id': root.split(os.sep)[-1],
                'system': root.split(os.sep)[-1],
                'description': 'Measuring fieldsensor {}'.format(
                    root.split(os.sep)[-1]),
                'keywords': '',
                'classification': [{
                    'name': 'System Type',
                    'definition':
                        'urn:ogc:def:classifier:x-istsos:1.0:systemType',
                    'value': 'insitu-fixed-point'},
                    {
                        'name': 'Sensor Type',
                        'definition':
                            'urn:ogc:def:classifier:x-istsos:1.0:sensorType',
                        'value': 'WatchDog'}],
                'capabilities': [],
                'location': location,
                'outputs': observedProperties
            }

            r = requests.post(proceduresURL, data=json.dumps(procedure))
            if not r.json()['success']:
                print("problem with ", procedure['system_id'])
                print(r.json())


def get_observed_properties(directory):
    outputs = [{'name': 'Time',
                'definition':
                    'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601',
                'uom': 'iso8601',
                'description': '',
                'constraint': {}}]

    observedProperties = istsosdat.get_metadata(
        '{}{}INDEX.SWD'.format(directory, os.sep), returnUnits=True)

    for observedProperty in observedProperties.split(','):
        outputs.append({
            'name': observedProperty.split('(')[0].strip(),
            'definition': observedProperty.split('(')[0].strip(),
            'uom':
                observedProperty.split('(')[1].split(')')[0].strip(),
            'description': '',
            'constraint': {}})

    return outputs


def get_location(locationName, procedure):
    with open(os.path.join(os.path.dirname(__file__),
                           'metadata',
                           'geometry_index.csv'), 'r') as geometry:
        z = 0
        for line in geometry.readlines():
            lineFeatures = line.split(',')
            lineFeatures.append('0')

            if procedure[0] in ['B', 'b'] and procedure[-2:] == 'cm':
                if procedure[1] == '1':
                    stationSuffix = 'Bat'
                elif procedure[1] == '2':
                    stationSuffix = 'Sims'
                elif procedure[1] in ['3', '4']:
                    stationSuffix = 'Ran'
                elif procedure[1] == '5':
                    stationSuffix = 'Tjo'
                elif procedure[1] == '6':
                    stationSuffix = 'Bis'

                z = procedure.split('cm')[0].strip().split('-')[-1].split(' ')[-1]
                procedure = '{} - {}'.format(procedure[0:2], stationSuffix)

            if procedure in lineFeatures or '{}-temp'.format(procedure) in lineFeatures:
                coordinates = [lineFeatures[3], lineFeatures[4], z]
                # TODO: Make crs more general
                if lineFeatures[2] == '32V':
                    crs = '32632'
                elif lineFeatures[2] == '33W':
                    crs = '32633'
                else:
                    raise ValueError('Unexpected coordinate system')
                break

    if procedure[0] in ['B', 'b']:
        procedure = '{}-{}'.format(procedure.split(' ')[0], z)
    if 'ø' in locationName:
        locationName = 'o'.join(locationName.split('ø'))
    if 'Ø' in locationName:
        locationName = 'o'.join(locationName.split('Ø'))
    if 'æ' in locationName:
        locationName = 'ae'.join(locationName.split('æ'))
    if 'å' in locationName:
        locationName = 'a'.join(locationName.split('å'))
    if 'Ы' in locationName:
        locationName = 'o'.join(locationName.split('Ы'))
    if 'Э' in locationName:
        locationName = 'O'.join(locationName.split('Э'))
    if 'Ж' in locationName:
        locationName = 'a'.join(locationName.split('Ж'))

    location = {'type': 'Feature',
                'geometry': {'type': 'Point',
                             'coordinates': coordinates},
                'crs': {'type': 'name',
                        'properties': {'name': crs}},
                'properties': {'name': '{}-{}'.format(locationName, procedure)}}

    return location


if __name__ == '__main__':
    supportedDevices = ['templogger']

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
        '-url',
        type=str,
        help='istSOS Server address IP or domain name')

    args = parser.parse_args()

    if args.__dict__['path'][-1] != os.sep:
        print("WARNING: Your path doesn't end with '{}'. It will parse all "
              "directories beginning with '{}' in the path "
              "'{}{}'".format(os.sep,
                              args.__dict__['path'].split(os.sep)[-1],
                              args.__dict__['path'].rsplit(os.sep, 1)[0],
                              os.sep))

    main()
