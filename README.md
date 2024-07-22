# apictesttools

apictesttools is a program that generates random API data in a json_lines format and posts it to an analytics platform using a provided ingestion or director URL. The produced events are randomised but realistic and unique. They are, by default (more details on other modes further on), grouped into indices of 100 events before each index is sent for ingestion in a loop of the program.

## Specifying key parameters

A number of key parameters for the program can be specified in an attached config.json file or as arguments when the program is executed from the command line.

Command line arguments:
```
python ./fireevents.py -h   
usage: fireevents.py [-h] [-d [DEBUG]] [-e [DRYRUN]] [-m [MULTIINDEX]] [-i [ingest_url]] [-f [direct_url]] [-a [numbofapis]]
                     [-b [numbofapps]] [-c [numbofcorgs]] [-p [numbofproducts]] [-l [numbofloops]]

API call faker

options:
  -h, --help            show this help message and exit
  -d [DEBUG], --debug [DEBUG]
                        Enables debug mode
  -e [DRYRUN], --dryrun [DRYRUN]
                        Generates a post and sends it to server (Will delete it from folder after)
  -m [MULTIINDEX], --multiindex [MULTIINDEX]
                        Executes serially from 30 days ago to now (1000 calls per day at random times) with 30 post output files
  -i [ingest_url], --ingestionurl [ingest_url]
                        Ingestion url to fake/make calls
  -f [direct_url], --directorurl [direct_url]
                        Director url to rollover in multiindex mode
  -a [numbofapis], --numberofapis [numbofapis]
                        Total number of APIs (Should be equal to or more than the number of Products)
  -b [numbofapps], --numberofapps [numbofapps]
                        --Total number of Apps (Should be equal to or more than the number of corgs)
  -c [numbofcorgs], --numberofcorgs [numbofcorgs]
                        Total number of corgs (Should be equal to or less than the number of Apps)
  -p [numbofproducts], --numberofproducts [numbofproducts]
                        Total number of Products (Should be equal to or less than the number of APIs)
  -l [numbofloops], --numberofloops [numbofloops]
                        Total number of loops to make
```

Config file:
```
{
  "dryrunReports" : true,
  "percent_ai_requests": 0.1,
  "dryrunRequests" : true,
  "ingestion_URL": "https://ai.cdm0701.supergirl.dev.ciondemand.com",
  "director_URL": "analytics-director:3009",
  "number_of_apis": 5,
  "number_of_apps": 5,
  "number_of_corgs": 3,
  "number_of_products": 3,
  "number_of_loops_to_make": 10,
  "scopes": [
    {
      "id": "dcef2f41-770e-4bbd-abc4-4adbf510b99f/113b4724-1ef8-4a4a-8295-3555862cd127",
      "name": "ibm/sandbox"
    },
    {
      "id": "dcef2f41-770e-4bbd-abc4-4adbf510b99f/3140821c-c2fe-4f09-a0e1-dd2a9e14c381",
      "name": "ibm/api-connect-catalog-1"
    }
  ]
}
```

## Default mode

The default mode performs loops of 100 API calls, each of which is added to a numbered post (default 10 loops, but this can be changed in the config file or entered as a command line argument).

In default mode, the program runs parallel and multi-threaded to send each loop's post to a server as quickly as possible (handling up to 7 posts at once).

## Multiindex mode

The multiindex mode produces loops of 1000 API calls, each of which contains a 24 hour period before the time the program is run, which are then added to a post named with the date at the start of the 24 hour period (default 30 loops/days, but this can also be changed in the config file or as a command line argument).

Activated with the ```-m``` command line argument.

In multiindex mode, the program runs serially and single-threaded to send each loop's post in chronological order to a server.

## Dryrun

apictesttools has dryrun functionality built in, in order to test its API call generation efficacy without requiring communication with an external server.

Activated with the ```-e``` command line argument or by setting ```"dryrunReports"``` and ```"dryrunRequests"``` to ```True``` in the config file.
