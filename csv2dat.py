import argparse


def csv2dat(options):

    i = open(options['path'], 'r')
    o = open('{}.dat'.format(options['path'][:-4]), 'w')

    header, columnsIndexes = get_header(i.readline(),
                                        options['timestamp_column'],
                                        options['observation_columns'])
    o.write(header)

    # TODO: Work only with desired columns

    for line in i.readlines():
        if ';' in line:
            outLine = line.split(';')
        else:
            outLine = line.split(',')

        outLine[0] = get_standardized_timestamp(outLine[0],
                                                options['timestamp_format'])
        outLine = ','.join(outLine)
        o.write(outLine)

    i.close()
    o.close()


def get_header(headerLine, timestampColumn, observationColumns):
    if ';' in headerLine:
        header = headerLine.split(';')
    else:
        header = headerLine.split(',')

    indexes = list()
    index = 0
    for column in header:
        if column.strip() == timestampColumn:
            header[index] = 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601'
            indexes.append(index)
        elif column.strip() in observationColumns.split(','):
            indexes.append(index)
        index += 1

    header = ','.join(header)

    return header, indexes


def get_standardized_timestamp(originalTimestamp, timestampFormat):

    # TODO: More formats
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
        help='Path to CSV file')

    parser.add_argument(
        '-observation_columns',
        type=str,
        dest='observation_columns',
        required=True,
        help='Name of columns with observations')

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
        choices=timestampFormats)

    args = parser.parse_args()

    csv2dat(args.__dict__)
