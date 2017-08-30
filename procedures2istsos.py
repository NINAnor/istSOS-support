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
import os, sys
import istsosdat


def main():

    insert_procedures(args.__dict__['url'],
                      args.__dict__['service'],
                      args.__dict__['path'],
                      args.__dict__['device_type'],
                      args.__dict__['geometry_index'],
                      args.__dict__['istsos_path'],
                      args.__dict__['username'],
                      args.__dict__['password'])


def insert_procedures(url, service, procedurePath, deviceType, geometryIndex,
                      istsosPath, username, password):
    """
    Insert procedures from your path to your server
    :param url: url address of your server
    :param service: The name of the service instance
    :param procedurePath: Path to the directory containing location folders
                          with procedures
    :param deviceType: Type of your device (mostly sensor)
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    :param istsosPath: Path to a directory where is istsos installed
    :param username: Username used to access istSOS server
    :param password: Password used to access istSOS server
    """

    walk_dir = procedurePath
    proceduresURL = '{}wa/istsos/services/{}/procedures'.format(url,
                                                                service)
    # TODO: See issue about changing csv to something better
    if geometryIndex[-4:] != '.csv':
        geometryIndex = '{}_{}.csv'.format(geometryIndex, deviceType)

    sys.path.append(istsosPath)
    from lib.requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth(username, password)
    requestsList = list()

    for root, subdirs, files in os.walk(walk_dir):
        if subdirs == []:
            observedProperties = get_observed_properties(root, deviceType,
                                                         files)
            if 'templogstasjoner' in root or 'Templogstasjoner' in root:
                locationName = root.split(os.sep)[-2].split(' ')[-1]
            else:
                locationName = root.split(os.sep)[-2].split(' ')[2:]
                locationName = '-'.join(locationName)

            if deviceType == 'templogger':
                requestsList.append(get_procedure_request(
                    root.split(os.sep)[-1],
                    observedProperties, locationName, geometryIndex))
            elif deviceType == 'TOV':
                for file in files:
                    requestsList.append(get_procedure_request(
                        file[:-4], observedProperties,
                        locationName, geometryIndex))

    for request in requestsList:
        r = requests.post(proceduresURL, data=json.dumps(request), auth=auth)
        if not r.json()['success']:
            print('Problem with procedure {}'.format(
                request['system_id']))
            print(r.json())


def get_procedure_request(procedureName, observedProperties, locationName,
                          geometryIndex):
    """
    Get dictionary for procedure import
    :param procedureName: Name of your sensor
    :param observedProperties: List of observed properties
    :param locationName: Geographical name of procedure location
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    :return procedure: dictionary containing all necessary aspects to import
    """

    procedureName = istsosdat.get_procedure_id(procedureName, geometryIndex)
    location = get_location(locationName, procedureName, geometryIndex)

    procedureName = istsosdat.standardize_norwegian(procedureName)
    procedure = {
        'system_id': procedureName,
        'system': procedureName,
        'description': 'Measuring fieldsensor {}'.format(
            procedureName),
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
    return procedure


def get_observed_properties(directory, deviceType, files):
    """
    Get observed properties of procedures in given directory
    :param directory: Directory containing procedures and index file
    :param deviceType: Type of your device (mostly sensor)
    :param files: List of files in the directory
    :return outputs: List of observed properties based on an index file
    """

    outputs = [{'name': 'Time',
                'definition':
                    'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601',
                'uom': 'iso8601',
                'description': '',
                'constraint': {}}]

    if deviceType == 'templogger':
        observedProperties = istsosdat.get_metadata(
            '{}{}INDEX.SWD'.format(directory, os.sep), returnUnits=True)
    elif deviceType == 'TOV':
        observedProperties = istsosdat.get_metadata(
            '{}{}{}'.format(directory, os.sep, files[0]), returnUnits=True)

    for observedProperty in observedProperties.split(','):
        outputs.append({
            'name': observedProperty.split('(')[0].strip(),
            'definition': observedProperty.split('(')[0].strip(),
            'uom':
                observedProperty.split('(')[1].split(')')[0].strip(),
            'description': '',
            'constraint': {}})

    return outputs


def get_location(locationName, procedure, geometryIndex):
    """
    Get location based on sensor location and its name
    :param locationName: Geographical name of procedure location
    :param procedure: Name of procedure
    :param geometryIndex: Path to the CSV file with procedures coords metadata
    :return location: json dictionary containing location name, crs and coords
    """

    with open(geometryIndex, 'r') as geometry:
        z = 0
        for line in geometry.readlines():
            lineFeatures = line.split(',')
            lineFeatures.append('0')

            if procedure[0] in ['B', 'b'] and procedure[-2:] == 'cm':
                z = procedure.split(
                    'cm')[0].strip().split('-')[-1].split(' ')[-1]

            if procedure in lineFeatures or \
                            '{}-temp'.format(procedure) in lineFeatures:
                coordinates = [lineFeatures[-3], lineFeatures[-2], z]
                # TODO: Make crs more general
                if lineFeatures[-4] == '32V':
                    crs = '32632'
                elif lineFeatures[-4] == '33W' or lineFeatures[-4] == '33N':
                    crs = '32633'
                elif lineFeatures[-4] == '34W':
                    crs = '32634'
                else:
                    raise ValueError('Unexpected coordinate system')
                break

    locationName = '{}-{}'.format(locationName, lineFeatures[0])
    locationName = istsosdat.standardize_norwegian(locationName)

    if 'templogger' in geometryIndex:
        if procedure[0] in ['B', 'b']:
            locationName = '{}-{}'.format(locationName.split(' ')[0], z)

        location = {'type': 'Feature',
                    'geometry': {'type': 'Point',
                                 'coordinates': coordinates},
                    'crs': {'type': 'name',
                            'properties': {'name': crs}},
                    'properties': {'name': locationName}}
    else:
        location = {'type': 'Feature',
                    'geometry': {'type': 'Point',
                                 'coordinates': coordinates},
                    'crs': {'type': 'name',
                            'properties': {'name': crs}},
                    'properties': {'name': locationName}}

    return location


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
        default='templogger',
        help='Type of your device (mostly sensor)')

    parser.add_argument(
        '-url',
        type=str,
        required=True,
        help='istSOS Server address IP or domain name')

    parser.add_argument(
        '-service',
        type=str,
        help='The name of the service instance')

    parser.add_argument(
        '-geometry_index',
        type=str,
        default=os.path.join(os.path.dirname(__file__),
                             'metadata',
                             'geometry_index'),
        help='Path to the CSV file with sensors metadata '
             '(names, crs, coordinates)')

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
