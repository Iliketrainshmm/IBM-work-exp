# apictesttools

apictesttools is a program that generates random API data in a jsonlines format and posts it to an analytics platform using a provided ingestion or director URL.

## Specifying key parameters

A number of key parameters for the program can be specified in an attached config.json file or as arguments when the program is executed from the command line.

```
python ./fireevents.py -h 
usage: fireevents.py [-h] [-d [DEBUG]] [-e [DRYRUN]]
                     [-m [MULTIINDEX]] [-u [ingest_url]]
                     [-f [direct_url]] [-a [numbofapis]]
                     [-b [numbofapps]] [-c [numbofcorgs]]
                     [-q [numbofproducts]]

API call faker

options:
  -h, --help            show this help message and exit
  -d [DEBUG], --debug [DEBUG]
                        Enables debug mode
  -e [DRYRUN], --dryrun [DRYRUN]
                        Generates a post and sends it to server  
                        (Will delete it from folder after)       
  -m [MULTIINDEX], --multiindex [MULTIINDEX]
                        Executes serially from 30 days ago to    
                        now (1000 calls per day at random        
                        times) with 30 post output files
  -u [ingest_url], --ingestionurl [ingest_url]
                        Ingestion url to fake/make calls
  -f [direct_url], --directorurl [direct_url]
                        Director url to rollover in multiindex   
                        mode
  -a [numbofapis], --numberofapis [numbofapis]
                        Total number of APIs (Should be equal    
                        to or more than the number of Products)  
  -b [numbofapps], --numberofapps [numbofapps]
                        --Total number of Apps (Should be equal  
                        to or more than the number of corgs)     
  -c [numbofcorgs], --numberofcorgs [numbofcorgs]
                        Total number of corgs (Should be equal   
                        to or less than the number of Apps)      
  -q [numbofproducts], --numberofproducts [numbofproducts]       
                        Total number of Products (Should be      
                        equal to or less than the number of      
                        APIs)
```

## Default mode

The default mode performs loops of 100 API calls, each of which is added to a numbered post (default 10 loops, but this can be changed in the config file or entered as a command line argument).

## Multiindex mode

The multiindex mode produces loops of 1000 API calls, each of which contains a 24 hour period before the time the program is run, which are then added to a post named with the date at the start of the 24 hour period (default 30 loops/days, but this can also be changed in the config file or as a command line argument).

## Dryrun

apictesttools has dryrun functionality built in, in order to test its API call generation efficacy without requiring communication with an external server.
