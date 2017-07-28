# istSOS-support

## What's that? 

Tools for importing data from a sensor directly on the istSOS server. 
istSOS is a python based server for maintaining sensor observation services. 

## Getting started

What you need and what shall you have installed before you start your work with
istSOS? 

### istSOS

A python based server for maintaining sensor observation services. On istSOS
you can manage and dispatch your sensor data with graphical user interface or
through python scripts. 

What does mean SOS? It's sensor observation service, an OGC format standard for
providing sensor observation data and even for some operations with them. 

### PostgreSQL

Object-relational database management system working with a database server. 

### PostGIS

PostgreSQL support for geographic data. 

### pgAdmin

Graphical user interface for PostgreSQL. 

### Apache

Server providing HTTP services. 

### libapache2-mod-wsgi

Python WSGI module for Apache. 

### psycopg2

Python interface for PostgreSQL.

## How to use these tools? 

Manuals are written for Linux OS. 

### Quick way using bash script

Clone this github repository to your computer:
```git clone https://github.com/NINAnor/istSOS-support.git```

Go to the new directory `istSOS-support`. Mostly:
```cd istSOS-support```

Run shell script with your own parameters (instead of asterisks):
```bash import2istsos.sh csv_path=* observation_columns=* timestamp_column=* timestamp_format=* url=* service=* offering=* procedure=*```

If you got message saying  `> Insert observation success: True`, your
data were imported and everything was OK. 

Need help? Don't know what these parameters mean? No problem, just run this
command:
```bash import2istsos.sh --help```

### Slower, but more thorough and much cooler way

Clone this github repository to your computer:
```git clone https://github.com/NINAnor/istSOS-support.git```

Go to the new directory `istSOS-support`. Mostly:
```cd istSOS-support```

Run python script with your own parameters (instead of asterisks):
```python csv2dat.py -path=* -observation_columns=* -timestamp_column=* -timestamp_format=*```

If there is no warning message, your data were converted into istSOS
acceptable format in .dat file in the same directory as your original file was.

Now go to the istSOS directory. Mostly: 
```cd /usr/share/istsos/```

Run python script with your own parameters (instead of asterisks):
```python scripts/csv2istsos.py -u * -s * -o * -p * -w * -m *```

If you got message saying  `> Insert observation success: True`, your
data were imported and everything was OK. 

Need help? Don't know what those parameters in commands mean? No problem, just
run on of those commands with flag `--help`:
```python csv2dat.py --help```
```python scripts/csv2istsos.py --help```

## Example 

I want to upload ids and temperatures to the server `localhost/istsos/`, on service `myservice` and offering
`temporary`. 

### My sample data

Repository cloned in `/home/user/workspace/`

Data are saved in folder `/home/user/Documents/myprocedure_20172807175100.csv`

| timestamp                        | id | garbage | urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature |
|----------------------------------|----|---------|:--------------------------------------------------------:|
| 2017-28-07T15:51:00.000000+01:00 | 1  | fox     |                           24.5                           |
| 2017-28-07T16:51:00.000000+01:00 | 2  | moose   |                            25                            |
| 2017-28-07T17:51:00.000000+01:00 | 3  | manatee |                           3.14                           |

### Import

#### Using shell script

```
cd /home/user/workspace/istSOS-support/
bash import2istsos.sh csv_path=/home/user/Documents/myprocedure_20172807175100.csv
observation_columns=id,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature timestamp_column=timestamp
timestamp_format=YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM url=http://localhost/istsos service=myservice offering=temporary procedure=myprocedure
```

Output: 
```
creating .dat from your .csv
done

uploading your .dat file on the server
Offering: temporary
Procedure: myprocedure
myprocedure > Sensor Description successfully loaded
myprocedure > GetObservation requested successfully executed
Searching: /home/user/Documents/myprocedure_[0-9]*.dat
Before insert ST: myprocedure
 > Begin: 2010-01-01T00:00:00+01:00
   + End: 2017-31-12T23:59:59+01:00
Insert ST: myprocedure
 > Begin: 2017-28-07T15:51:00+01:00
   + End: 2017-28-07T17:51:00+01:00
 > Values: 3
 > Insert observation success: True
```

#### Using shell script

```
python /home/user/workspace/istSOS-support/csv2dat.py -path=/home/user/Documents/myprocedure_20172807175100.csv -observation_columns=id,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature -timestamp_column=timestamp -timestamp_format=YYYY-MM-DDTHH:MM:SS.SSSSSS+HH:MM
cd /usr/share/istsos/
python scripts/csv2istsos.py -u http://localhost/istsos -s myservice -o temporary -p myprocedure -w /home/user/Documents/ -m 1000
```

Output: 
```
Offering: temporary
Procedure: myprocedure
myprocedure > Sensor Description successfully loaded
myprocedure > GetObservation requested successfully executed
Searching: /home/user/Documents/myprocedure_[0-9]*.dat
Before insert ST: myprocedure
 > Begin: 2010-01-01T00:00:00+01:00
   + End: 2017-31-12T23:59:59+01:00
Insert ST: myprocedure
 > Begin: 2017-28-07T15:51:00+01:00
   + End: 2017-28-07T17:51:00+01:00
 > Values: 3
 > Insert observation success: True
```






