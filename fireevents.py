# Libraries and pointers
from wonderwords import RandomWord
import json
import uuid
import random
import argparse
import datetime
import concurrent.futures
import jsonlines
from faker import Faker
import requests
import urllib3
import time
import os
import math
from colorama import Fore
import sys
import time
faker = Faker()
parser = argparse.ArgumentParser(description="API call faker")
r = RandomWord()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Make folders
if not os.path.isdir("Output"):
    os.makedirs("Output")

if not os.path.isdir("Reports"):
    os.makedirs("Reports")

# Extract config and users from files for later
def getconfig():
  try:
    with open("config.json", "r") as openfile:
      json_object = json.load(openfile)
    return json_object
  except:
    return None

def getuseragents():
  with open(str("useragents.json"), "r") as openfile:
    json_object = json.load(openfile)
  return json_object

# Returns default only if no config file to replace 
def configPresent(default):
  if config == None:
    return default
  else:
    return None

def setNumLoops():
  global num_of_loops
  if config != None:
    num_of_loops = int(config["number_of_loops_to_make"])
  else:
    global num_of_events
    num_of_events = 1000
    num_of_loops = 30

# Important variables to use later for generating fake API data
# Config in
methods = {
    "method":[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "TRACE",
        "OPTIONS",
        "HEAD"
    ],
    "weights":[
        0.45,
        0.20,
        0.10,
        0.10,
        0.05,
        0.05,
        0.05
    ]
}
ai_models = [
    "google/flan-ul2",
    "granite-7b-lab",
    "granite-13b-chat",
    "granite-13b-instruct",
    "llama-3-8b-instruct",
    "llama-2-13b-chat",
    "codellama-34b-instruct",
    "mixtral-8x7b-instruct",
    "merlinite-7b",
    "flan-t6-xl-3b",
    "starcoder-15.5b"
]
ai_models_length = len(ai_models)
config = getconfig()
num_of_events = 100
num_of_loops = 10

# Command line arguments
parser.add_argument('-d', '--debug', help='Enables debug mode',
                    required=False, type=bool, const=True, nargs='?')
parser.add_argument('-e', '--dryrun', help='Generates a post and sends it to server (Will delete it from folder after)',
                    required=False,type=bool, const=True, nargs='?')
parser.add_argument('-m', '--multiindex', help='Executes serially from 30 days ago to now (1000 calls per day at random times) with 30 post output files',
                    required=False,type=bool, const=True, nargs='?')
parser.add_argument('-i', '--ingestionurl', metavar='ingest_url', type=str, required=False, nargs='?',
                    help='Ingestion url to fake/make calls')
parser.add_argument('-f', '--directorurl', metavar='direct_url', type=str, required=False, nargs='?',
                    help='Director url to rollover in multiindex mode')
parser.add_argument('-a', '--numberofapis', metavar='numbofapis', type=int, required=False, nargs='?', default=configPresent(5),
                    help='Total number of APIs (Should be equal to or more than the number of Products)')
parser.add_argument('-b', '--numberofapps', metavar='numbofapps', type=int, required=False, nargs='?', default=configPresent(5),
                    help='--Total number of Apps (Should be equal to or more than the number of corgs)')
parser.add_argument('-c', '--numberofcorgs', metavar='numbofcorgs', type=int, required=False, nargs='?', default=configPresent(3),
                    help='Total number of corgs (Should be equal to or less than the number of Apps)')
parser.add_argument('-p', '--numberofproducts', metavar='numbofproducts', type=int, required=False, nargs='?', default=configPresent(3),
                    help='Total number of Products (Should be equal to or less than the number of APIs)')
parser.add_argument('-l', '--numberofloops', metavar='numbofloops', type=int, required=False, nargs='?', default=None,
                    help='Total number of loops to make')

# Puts arguments in variable
passed = parser.parse_args()

# Posts API data to Output
def fakepost(filename, data):
  with jsonlines.open(str("Output/"+filename + ".txt"), mode="w") as writer:
    writer.write_all(data)
    writer.close()

# Uses provided/default config if it exists
if config != None:
  num_of_apis = int(config["number_of_apis"])
  num_of_apps = int(config["number_of_apps"])
  num_of_corgs = int(config["number_of_corgs"])
  num_of_products = int(config["number_of_products"])

# Defined for error if no input
ingestion_url = None
director_url = None

# Other config info, without parser defaults
if config == None:
  percent_ai_calls = 0.1
  scopes = [
    {
      "id": "c7f6b296-a20c-4af2-bf8c-f2e0907cca77/5d9fbb72-1cfe-4441-be80-981b20a4fbe0",
      "name": "ibm/sandbox"
    },
    {
      "id": "c7f6b296-a20c-4af2-bf8c-f2e0907cca77/8fdd0e32-decd-4273-aa53-29ef517cfbac",
      "name": "ibm/demo"
    }
  ]
else:
  percent_ai_calls = float(config["percent_ai_requests"])
  ingestion_url = str(config["ingestion_URL"])
  director_url = str(config["director_URL"])
  scopes = config["scopes"]
  dryrunReports = bool(config["dryrunReports"])
  dryrunRequests = bool(config["dryrunRequests"])

# Handles (potential) command line input (debug, dryrun, and multiindex functions)
if passed.debug is True:
  debugmode = True
else:
  debugmode = False
if passed.dryrun is True:
  dryrunReports = True
  dryrunRequests = True
else:
  dryrunReports = False
  dryrunRequests = False
if passed.multiindex is True:
  multiindex = True
else:
  multiindex = False
setNumLoops()

# Prints out command line arguments for debugging
if debugmode == True:
  print(passed)

# Input data always overrides config file
if passed.ingestionurl:
  ingestion_url = passed.ingestionurl
if passed.directorurl:
  director_url = passed.directorurl
if passed.numberofapis:
  num_of_apis = passed.numberofapis
if passed.numberofapps:
  num_of_apps = passed.numberofapps
if passed.numberofcorgs:
  num_of_corgs = passed.numberofcorgs
if passed.numberofproducts:
  num_of_products = passed.numberofproducts
if passed.numberofloops:
  num_of_loops = passed.numberofloops

# Abort with error if no ingestion or director URL in config or arguments
if multiindex == False:
  if ingestion_url == None:
    sys.exit("Error: no ingestion URL found. Please provide an ingestion URL in a config file or as a command line argument.")
else:
  if director_url == None:
    sys.exit("Error: no director URL found. Please provide a director URL in a config file or as a command line argument.")

# Sorts out scopes
if scopes:
  scopes_exist = True
  amount_of_scopes = len(scopes)
else:
  scopes_exist = False

if num_of_apis < num_of_products:
  num_of_apis = num_of_products

products = {}

api_per_prod = num_of_apis//num_of_products
corg_list = []
app_list = []
product_list = []
api_list = []
for i in range(0, num_of_products):
  products[i] = {"productid": str(
      uuid.uuid1()), "productname": r.word(), "apis": {}}
  product_list.append(
      {"name": products[i]["productname"], "id": products[i]["productid"], "version": '1.0.0'})
  for i2 in range(0, api_per_prod):
    products[i]["apis"]["api" +
                        str(i2)] = {"apiid": str(uuid.uuid1()), "apiname": r.word()}
    api_list.append({"name": products[i]["apis"]["api"+str(i2)]["apiname"],
                    "id": products[i]["apis"]["api"+str(i2)]["apiid"], "version": '1.0.0'})
  if i == 0:
    api_per_prod_rem = num_of_apis % num_of_products
    for i3 in range(0, api_per_prod_rem):
      ifinal = i3+api_per_prod_rem-1
      products[i]["apis"]["api" +
                          str(ifinal)] = {"apiid": str(uuid.uuid1()), "apiname": r.word()}
      api_list.append({"name": products[i]["apis"]["api"+str(ifinal)]["apiname"],
                      "id": products[i]["apis"]["api"+str(ifinal)]["apiid"], "version": '1.0.0'})

if num_of_apps < num_of_corgs:
  num_of_apps = num_of_corgs

corgs = {}

apps_per_corg = num_of_apps//num_of_corgs

for a in range(0, num_of_corgs):
  corgs[a] = {"corgid": str(uuid.uuid1()), "corgname": r.word(), "apps": {}}
  corg_list.append({"name": corgs[a]["corgname"], "id": corgs[a]["corgid"]})
  for a2 in range(0, apps_per_corg):
    corgs[a]["apps"]["app" +
                     str(a2)] = {"appid": str(uuid.uuid1()), "appname": r.word()}
    app_list.append({"name": corgs[a]["apps"]["app"+str(a2)]
                    ["appname"], "id": corgs[a]["apps"]["app"+str(a2)]["appid"]})
  if a == 0:
    apps_per_corg_rem = num_of_apps % num_of_corgs
    for a3 in range(0, apps_per_corg_rem):
      afinal = a3+apps_per_corg_rem-1
      corgs[a]["apps"]["app" +
                       str(afinal)] = {"appid": str(uuid.uuid1()), "appname": r.word()}
      app_list.append({"name": corgs[a]["apps"]["app"+str(afinal)]
                      ["appname"], "id": corgs[a]["apps"]["app"+str(afinal)]["appid"]})

if debugmode is True:
  print(products)
if debugmode is True:
  print(corgs)

ipaddress = {}

for c in range(0, 150):
  ipaddress[c] = faker.ipv4_public()

if debugmode is True:
  print(ipaddress)

useragents = getuseragents()

# Sets up time parameters
currenttimeepoch = int(time.time())
if multiindex == False:
  oldtime = currenttimeepoch-2592000
  newtime = None
else:
  oldtime = currenttimeepoch - (num_of_loops * 24 * 3600) + 1
  newtime = oldtime + (24 * 3600) - 1

codedata = {
    "codes": [
        "200 OK",
        "201 Created",
        "204 No Content",
        "400 Bad Request",
        "401 Unauthorized",
        "403 Forbidden",
        "404 Not Found",
        "429 Too Many Requests",
        "500 Internal Server Error",
        "501 Not Implemented"
    ],
    "weights": [
        0.25,
        0.15,
        0.10,
        0.10,
        0.10,
        0.05,
        0.05,
        0.10,
        0.05,
        0.05
    ]
}
statcodes = codedata["codes"]
statcodeslength = len(statcodes)
weights = codedata["weights"]
weightslength = len(weights)

def createpost(newtime, oldtime):
  if scopes_exist is True:
    randomscope = random.randint(0, int(amount_of_scopes-1))
    idscope = str(scopes[randomscope]["id"])
    namescope = str(scopes[randomscope]["name"])
    if len(idscope.split("/")) == 2:
      org_id = str(idscope.split("/")[0])
      catalog_id = str(idscope.split("/")[1])
      space_id = ""
    elif len(idscope.split("/")) == 3:
      org_id = str(idscope.split("/")[0])
      catalog_id = str(idscope.split("/")[1])
      space_id = str(idscope.split("/")[2])
    if len(namescope.split("/")) == 2:
      org_name = str(namescope.split("/")[0])
      catalog_name = str(namescope.split("/")[1])
      space_name = ""
    elif len(namescope.split("/")) == 3:
      org_name = str(namescope.split("/")[0])
      catalog_name = str(namescope.split("/")[1])
      space_name = str(namescope.split("/")[2])

  if weightslength == statcodeslength:
    statcode = random.choices(statcodes, weights=weights, k=1)[0]
  else:
    statcode = "200 OK"

  if multiindex == False:
    randomtime = random.randint(oldtime, currenttimeepoch)
    randomtimedate = datetime.datetime.fromtimestamp(randomtime).isoformat()
    if debugmode is True:
      print(randomtimedate)
  else:
    randomtime = random.randint(oldtime, newtime)
    randomtimedate = datetime.datetime.fromtimestamp(randomtime).isoformat()
    if debugmode is True:
      print(randomtimedate)

  clientrandomip = ipaddress[random.randint(0, 149)]

  product_num = int(int(random.randint(0, num_of_products))-1)
  if product_num == -1:
    product_num = 0
  if debugmode is True:
    print("prodnum: "+str(product_num))
  numofapisinprod = len(products[product_num]["apis"])
  apinum = int(int(random.randint(0, numofapisinprod))-1)
  if apinum == -1:
    apinum = 0
  if debugmode is True:
    print("apinum: "+str(apinum))

  corg_num = int(int(random.randint(0, num_of_corgs))-1)
  if corg_num == -1:
    corg_num = 0
  if debugmode is True:
    print("corgnum: "+str(corg_num))
  numofappsincorg = len(corgs[corg_num]["apps"])
  appnum = int(int(random.randint(0, numofappsincorg))-1)
  if appnum == -1:
    appnum = 0
  if debugmode is True:
    print("appnum: "+str(appnum))

  api_id = products[product_num]["apis"]["api"+str(apinum)]["apiid"]
  app_id = corgs[corg_num]["apps"]["app"+str(appnum)]["appid"]
  corg_id = corgs[corg_num]["corgid"]
  product_id = products[product_num]["productid"]
  client_id = str(uuid.uuid1())

  transactionid1 = str(uuid.uuid1())
  transaction_id = transactionid1.replace("-", "")

  api_name = products[product_num]["apis"]["api"+str(apinum)]["apiname"]
  app_name = corgs[corg_num]["apps"]["app"+str(appnum)]["appname"]
  corg_name = corgs[corg_num]["corgname"]
  product_name = products[product_num]["productname"]

  useragent = useragents[random.randint(0, int(len(useragents)-1))]

  method = random.choices(
      methods["method"], weights=methods["weights"], k=1)[0]

  time_to_serve = random.randint(42, 1500)

  data = {
      "api_id": api_id,
      "api_name": api_name,
      "api_resource_id": api_name + ":1.0.0:get:/clothing/tshirts",
      "api_version": "1.0.0",
      "app_id": app_id,
      "app_lifecycle_state": "PRODUCTION",
      "app_name": app_name,
      "bytes_received": 0,
      "bytes_sent": 488,
      "catalog_id": catalog_id,
      "catalog_name": catalog_name,
      "client_id": client_id,
      "client_ip": clientrandomip,
      "datetime": randomtimedate,
      "developer_org_id": corg_id,
      "developer_org_name": corg_name,
      "developer_org_title": corg_name,
      "domain_name": "apiconnect",
      "endpoint_url": "N/A",
      "gateway_ip": "9.46.120.78",
      "gateway_service_name": "gateway-service1",
      "host": "172.16.227.15",
      "http_user_agent": useragent,
      "immediate_client_ip": "9.171.17.14",
      "latency_info": [
          {
              "started": 0,
              "task": "Start"
          },
          {
              "started": 2,
              "task": "api-routing"
          },
          {
              "started": 4,
              "task": "api-cors"
          },
          {
              "started": 5,
              "task": "api-client-identification"
          },
          {
              "started": 5,
              "task": "assembly-ratelimit"
          },
          {
              "started": 6,
              "task": "api-security"
          },
          {
              "started": 6,
              "task": "assembly-function-call"
          },
          {
              "started": 6,
              "task": "api-execute"
          },
          {
              "started": 6,
              "task": "assembly-invoke"
          },
          {
              "started": 40,
              "task": "assembly-function-call"
          },
          {
              "started": 40,
              "task": "assembly-function-call"
          },
          {
              "started": 40,
              "task": "api-result"
          }
      ],
      "log_policy": "payload",
      "opentracing_info": [],
      "org_id": org_id,
      "org_name": org_name,
      "plan_id": product_name + ":1.0.0:default",
      "plan_name": "default",
      "plan_version": "1.0.0",
      "product_id": product_id,
      "product_name": product_name,
      "product_title": product_name,
      "product_version": "1.0.0",
      "query_string": "client_id=" + client_id,
      "rateLimit": {
          product_name + "_1.0.0_default_rate-limit": {
              "period": 1,
              "count": 99,
              "limit": 100,
              "unit": "hour",
              "interval": 1,
              "reject": "false"
          }
      },
      "request_body": "",
      "request_http_headers": [
          {
              "Host": "apicdev1078.rtp.raleigh.ibm.com:9443"
          },
          {
              "User-Agent": "curl/7.82.0"
          },
          {
              "Accept": "*/*"
          }
      ],
      "request_method": method,
      "request_protocol": "https",
      "resource_id": "default:1.0.0:get:/clothing/tshirts",
      "response_body": "",
      "response_http_headers": [
          {
              "Date": "Fri, 23 Sep 2022 19:59:48 GMT"
          },
          {
              "Content-Type": "application/json"
          },
          {
              "Content-Length": "488"
          },
          {
              "Server": "gunicorn/19.9.0"
          },
          {
              "Access-Control-Allow-Origin": "*"
          },
          {
              "Access-Control-Allow-Credentials": "true"
          },
          {
              "X-Global-Transaction-ID": "196c5565632e102a5c805bc3"
          }
      ],
      "space_id": space_id,
      "space_name": space_name,
      "status_code": statcode,
      "tags": [
          "apicapievent"
      ],
      "time_to_serve_request": time_to_serve,
      "transaction_id": transaction_id,
      "uri_path": "/surf-shop/sandbox/clothing/" + api_name + "/price"
  }
  if random.random() <= percent_ai_calls:
    ai_model = ai_models[random.randint(0, int(ai_models_length-1))]
    ai_request_tokens = math.floor(random.random()*1000)
    ai_response_tokens = math.floor(random.random()*2000)
    ai_total_tokens = ai_request_tokens+ai_response_tokens
    cache_hit = bool(random.random() < 0.3)
    data["ai_model"] = ai_model
    data["ai_request_tokens"] = ai_request_tokens
    data["ai_response_tokens"] = ai_response_tokens
    data["ai_total_tokens"] = ai_total_tokens
    data["ai_cache_hit"] = cache_hit
  return data


def createreport(orgname, catalogname, spacename):
  reportdata = {
      "datetime": str(datetime.datetime.now(datetime.UTC).isoformat()),
      "org": orgname,
      "catalog": catalogname,
      "space": spacename,
      "api_count": len(api_list),
      "product_count": len(product_list),
      "corg_count": len(corg_list),
      "app_count": len(app_list),
      "sub_count": len(app_list),
      "app_list": app_list,
      "product_list": product_list,
      "api_list": api_list,
      "corg_list": corg_list
  }
  return reportdata


cwd = os.getcwd()
cert = (cwd + "/mounted/certs/tls.crt",
        cwd + "/mounted/certs/tls.key")


def realpost(post_num):
  outfile = open("Output/post"+str(post_num)+".txt")
  databuffer = outfile.read()
  outfile.close()
  if multiindex == False:
    requests.post(ingestion_url+"/ingestion", cert=cert,
                  data=databuffer, verify=False)
  else:
    requests.post(director_url+"/cloud/clustermgmt/storage/apic-api-r/rollover", cert=cert,
                data=databuffer, verify=False)


def firereports():
  for x in range(0,len(scopes)):
    names = str(scopes[x]["name"])
    names2 = names.split("/")
    orgname = names2[0]
    catalogname = names2[1]
    spacename = ""
    if len(scopes[x]["name"]) == 3:
      names2 = names.split("/")
      orgname = names2[0]
      catalogname = names2[1]
      spacename = names2[2]
    data = createreport(
        orgname=orgname, catalogname=catalogname, spacename=spacename)
    with open(str("Reports/Report"+str(x) + ".json"), "w") as outfile:
      json.dump(data, outfile, indent=2)
    if dryrunReports == False:
      infile = open("Reports/Report"+str(x)+".json")
      databuffer = infile.read()
      infile.close()
      if multiindex == False:
        requests.post(ingestion_url+"/all-content", cert=cert,
                    data=databuffer, verify=False)
      else:
        requests.post(director_url+"/all-content", cert=cert,
                    data=databuffer, verify=False)
      os.remove("Reports/Report"+str(x)+".json")


def percall(post_num, newtime, oldtime):
  posts = []
  for b in range(0, num_of_events):
    # print("Creating post data for loop {}, [{} / {}]".format(str(post_num),str(b),str(num_of_calls)))
    if debugmode is True:
      print(b)
    posts.append(createpost(newtime, oldtime))
  if debugmode is True:
    print(posts)
  post_name = postName(post_num)
  if dryrunRequests is True:
    fakepost("post"+ postName(post_num), posts)
  else:
    fakepost("post"+post_name, posts)
    realpost(post_name)
    os.remove("Output/post"+post_name+".txt")
    print("Sent post {}".format(post_name))

def postName(post_num):
  if multiindex == True:
    return str(datetime.datetime.fromtimestamp(oldtime).date())
  else:
    return str(post_num)

if multiindex == False:
  with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
    for i in range(0, num_of_loops):
      future = executor.submit(percall, i, newtime, oldtime)
  result = future.result()
else:
  for i in range(0, num_of_loops):
    percall(i, newtime, oldtime)
    # print("Posted data for loop starting at " + str(datetime.datetime.fromtimestamp(oldtime).date()))
    oldtime = oldtime + (24 * 3600)
    newtime = newtime + (24 * 3600)
    # time.sleep(1)
print(Fore.GREEN+"Posted "+Fore.RESET+str(num_of_loops)+Fore.GREEN+" of "+Fore.RESET+str(num_of_loops)+Fore.GREEN+" posts"+Fore.RESET)

print("Starting reports")
firereports()
print("All reports completed")
