# apictesttools

apictesttools is a program that generates random API data in a jsonlines format and posts it to an analytics platform using a provided ingestion or director URL.

## Specifying key parameters

A number of key parameters for the program can be specified in an attached config.json file or as arguments when the program is executed from the command line.

## Default mode

The default mode performs loops of 100 API calls, each of which is added to a numbered post (default 10 loops, but this can be changed in the config file or entered as a command line argument).

## Multiindex mode

The multiindex mode produces loops of 1000 API calls, each of which contains a 24 hour period before the time the program is run, which are then added to a post named with the date at the start of the 24 hour period (default 30 loops/days, but this can also be changed in the config file or as a command line argument).

## Dryrun

apictesttools has dryrun functionality built in, in order to test its API call generation efficacy without requiring communication with an external server.
