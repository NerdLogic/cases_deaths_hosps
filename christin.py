#!/usr/bin/env python
# Created by Duane Bronson
# Inspired by Era Iyer
# Nov 2020 
# Christin's data file converter to json
# parses every state's coronavirus history to create a json file with state, dates, total cases, new cases, and rolling average cases 
#
# also, determines appropriate color representation based on data 
#                   regarding daily new coronavirus cases
#
# winning = green
# nearly there = orange
# needs action = red
#
# methods to determine color representation:
#   1. green --> current average < 10 OR current average < 20  and current avrage < 0.5*peak
#   2. orange --> current average < 1.5*20 and current average < peak*0.5 
#                 OR current average < peak*0.2
#   3. red --> all other cases 

import sys
import csv
import json
import requests
from lxml import html
import re
from datetime import datetime
#import numpy as np


#import pandas as pd
us_states = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", 
            "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", 
            "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota",
            "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", 
            "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", 
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", 
            "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

new_hospitalizations = []
datesHospitalizations = []
# Create a set for easy checking
state_set = set(us_states)
state_data = {}

json_out = []

with open('christin.csv', newline='') as csvfile:
  csvreader = csv.reader(csvfile, delimiter="\t")
  column = 0
  headers = {}
  header_row = next(csvreader)
  for header in header_row:
    headers[header]=column
    column+=1
  firstdate = headers["County"]+1
  for row in csvreader:
    state_name=row[headers["State"]]
    if not state_name in state_set:
      next
    if state_name in state_data:
      state_dict = state_data[state_name]
      for col in range(firstdate,len(headers)-1):
        try:
          state_dict["new_cases"][col-firstdate] += float(row[col])
          state_dict["avg_cases"][col-firstdate] += float(row[col])
        except:
          pass
    else:
      state_dict = {"state":state_name, "dates": [], "new_cases": [], "avg_cases": [], "new_deaths": [], "avg_deaths": [], "hospDates": [], "new_hospitalizations": [], "avg_hospitalizations": []}
      state_data[state_name] = state_dict
      json_out.append(state_dict)
      for col in range(firstdate,len(headers)):
        state_dict["dates"].append(header_row[col])
        try:
          state_dict["new_cases"].append(float(row[col]))
          state_dict["avg_cases"].append(float(row[col]))
        except:
          pass

# Write as json
with open('result.json', 'w') as fp:
    json.dump(json_out, fp)
