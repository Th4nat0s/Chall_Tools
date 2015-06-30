#!/usr/bin/env python
# coding=utf-8   
import re, sys
import json
import datetime

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'Convert HAR File to CURL-LOADER script'
    print 'To Use: '+ sys.argv[0]+  ' my_full_har'
    sys.exit(1)
  else:
    return sys.argv[1]

# Main Code #####
def main():
  param = getparam(1)
  json_data = open(param)
  data = json.load(json_data)


  # Load Data and sort according to retrieve timestamp
  # 2015-06-30T18:28:35.186Z
  fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
  queries = []
  lasttime = datetime.datetime.strptime( data['log']['entries'][0]['startedDateTime'], fmt)
  for entries in  data['log']['entries']:
    time = datetime.datetime.strptime( entries['startedDateTime'],  fmt)
    timedelta = (datetime.datetime.strptime( entries['startedDateTime'], fmt) - lasttime)
    hittime  = int( timedelta.total_seconds() * 1000) 
    if entries['request']['method'] == 'POST':
      data = entries['request']['postData']['text']
    else:
      data = None
    queries.append([hittime,  entries['request']['method'], entries['request']['url'], data])
  queries.sort(key=lambda tup: tup[0]) 
  
  #generate output
  lasttime = 0
  hit = 0
  current = lasttime
  for querie in queries:
    current = querie[0]
    print ('URL="%s"' % querie[2]) 
    print ('URL_SHORT_NAME="HIT%d"' % hit)
    print ('REQUEST_TYPE=%s' % querie[1]) 
    if querie[1] == "POST":
      print ('FORM_USAGE_TYPE = "AS_IS"' )
      print ('FORM_STRING = "%s"' % querie[3])
    print ('TIMER_URL_COMPLETION = 10000')
    delta = int(current) - int(lasttime)
    if delta <= 20:
      delta = 0
    print ('TIMER_AFTER_URL_SLEEP = %s' %( delta) )
    lasttime = current
    hit += 1 
    print ('')


if __name__ == '__main__':
  main()
