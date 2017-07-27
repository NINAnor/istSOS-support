import argparse

def csv2dat(options):

    i = open(options['path'],'r')
    o = open('{}.dat'.format(options['path'][:-4]), 'w')

    header, columnsIndexes = get_header(i.readline(), options['timestamp_column'], options['observation_columns'])
    o.write(header)

    # TODO: Work only with desired columns

    for line in i.readlines():
        if ';' in line:
            outLine = line.split(';')
        else:
            outLine = line.split(',')

        # TODO: Not so format-specific function for timestamp conversion
        outLine[0] = '{}-{}-{}'.format(outLine[0][:4], outLine[0][4:6], outLine[0][6:])
        outLine[0] += 'T00:00:00.000000+01:00'
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import data from a csv file.')

    parser.add_argument('-path',
                        type=str,
                        dest='path',
                        required=True,
                        help='Path to CSV file')

    parser.add_argument('-observation_columns',
                        type=str,
                        dest='observation_columns',
                        required=True,
                        help='Name of columns with observations')

    parser.add_argument('-timestamp_column',
                        type=str,
                        dest='timestamp_column',
                        default='urn:ogc:def:parameter:x-istsos:1.0:time:iso8601',
                        help='Name of the column with timestamps')

    args = parser.parse_args()

    csv2dat(args.__dict__)