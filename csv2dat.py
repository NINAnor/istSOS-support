import argparse


def csv2dat(options):

    i = open(options['path'], 'r')
    o = open('{}.dat'.format(options['path'][:-4]), 'w')

    header, columnsIndexes = get_header(i.readline(),
                                        options['timestamp_column'],
                                        options['observation_columns'])
    o.write(header)

    for line in i.readlines():
        o.write(get_observations(line, options['timestamp_format'], columnsIndexes))

    i.close()
    o.close()


def get_header(headerLine, timestampColumn, observationColumns):
    if ';' in headerLine:
        headerLine = headerLine.split(';')
    else:
        headerLine = headerLine.split(',')

    indexes = dict()
    header = str()
    index = 0
    for column in headerLine:
        if column.strip() == timestampColumn:
            indexes.update({'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601': index})
            header += 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,'
        elif column.strip() in observationColumns.split(','):
            indexes.update({column.strip(): index})
            header += '{},'.format(column.strip())
        index += 1

    header = header[:-1]

    if not header.endswith('\n'): #header[-2:] != '\n':
        header += '\n'

    return header, indexes


def get_observations(line, timestampFormat, columnsIndexes):

    index = 0
    columns = list()

    if ';' in line:
        line = line.split(';')
    else:
        line = line.split(',')

    for column in line:
        if index in columnsIndexes.values():
            if index == columnsIndexes['urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']:
                columns.append(get_standardized_timestamp(column, timestampFormat))
            else:
                columns.append(column)
        index += 1

    outLine = ','.join(columns)
    if not outLine.endswith('\n'):
        outLine += '\n'

    return outLine


def get_standardized_timestamp(originalTimestamp, timestampFormat):

    # TODO: Support more formats
    if timestampFormat == 'YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM':
        standardizedTimestamp = timestampFormat
    elif timestampFormat == 'YYYYMMDD':
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000+01:00'.format(
            originalTimestamp[:4],
            originalTimestamp[4:6],
            originalTimestamp[6:])
    elif timestampFormat == 'DD.MM.YYYY':
        originalTimestamp = originalTimestamp.split('.')
        standardizedTimestamp = '{}-{}-{}T00:00:00.000000+01:00'.format(
            originalTimestamp[2],
            originalTimestamp[1],
            originalTimestamp[0])

    return standardizedTimestamp


if __name__ == '__main__':
    timestampFormats = ['YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM', 'YYYYMMDD',
                        'DD.MM.YYYY']

    parser = argparse.ArgumentParser(
        description='Import data from a csv file on an istSOS server.')

    parser.add_argument(
        '-path',
        type=str,
        dest='path',
        required=True,
        help='Path to CSV file with observations')

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

    args = parser.parse_args()

    csv2dat(args.__dict__)
