#!/usr/bin/env python
# Created by Duane Bronson
# Inspired by Era Iyer
# Aug 2020 
# worldometer scraper
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

worldometers = "https://www.worldometers.info"

#import pandas as pd
us_states = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", 
            "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", 
            "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota",
            "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", 
            "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", 
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", 
            "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

new_hospitalizations = []
#state_code = dict(zip(us_states,us_states_codes))
datesHospitalizations = []

usa_url = worldometers + "/coronavirus/country/us/"
page = requests.get(usa_url)
tree = html.fromstring(page.content)

results = []

# Create a set for easy checking
state_set = set(us_states)
for state in tree.xpath("//table[@id='usa_table_countries_yesterday']/tbody/tr/td/a[@class='mt_a']"):
  if state.text_content() in state_set:
    state_dict = {"state":state.text_content(), "dates": [], "new_cases": [], "avg_cases": [], "new_deaths": [], "avg_deaths": [], "hospDates": [], "new_hospitalizations": [], "avg_hospitalizations": []}
    #try:
    state_page = requests.get(worldometers + state.get('href'))
    state_tree = html.fromstring(state_page.content)
    for script in state_tree.xpath("//div[@class='col-md-12']/script"):
      script_text = script.text_content()
      if re.search("Highcharts\\.chart\\('graph-cases-daily', {",script_text):
        script_text = re.sub("responsive:.*","",script_text,flags=re.DOTALL) # clip anything past this because data repeats
        m = re.search("categories: \\[\"([\"\\w\\s,]*)\"\\]",script_text)
        dates = re.split('","',m.group(1))
        for n, d in enumerate(dates):
          state_dict["dates"].append(datetime.strptime(d + " 2020", '%b %d %Y').date().isoformat())
        matches = re.findall("name:\s*'([\w\s-]*)',[^}]*data:\s*\\[([\"\\w\\s,]*)\\]",script_text,flags = re.DOTALL)
        for m in matches:
          name = m[0]
          data = re.split(',',m[1])
          if name == "Daily Cases":
            state_dict["new_cases"] = data 
          elif name == "7-day moving average":
            state_dict["avg_cases"] = data 
          #print (name + ": " + dates[3] + " : " + data[3])
      if re.search("Highcharts\\.chart\\('graph-deaths-daily', {",script_text):
        script_text = re.sub("responsive:.*","",script_text,flags=re.DOTALL) # clip anything past this because data repeats
        m = re.search("categories: \\[\"([\"\\w\\s,]*)\"\\]",script_text)
        dates = re.split('","',m.group(1))
        death_dates=[]
        for n, d in enumerate(dates):
          death_dates.append(datetime.strptime(d + " 2020", '%b %d %Y').date().isoformat())
        if death_dates != state_dict["dates"]:
          raise Exception("Death and Infection dates do not match")
        matches = re.findall("name:\s*'([\w\s-]*)',[^}]*data:\s*\\[([\"\\w\\s,]*)\\]",script_text,flags = re.DOTALL)
        for m in matches:
          name = m[0]
          data = re.split(',',m[1])
          if name == "Daily Deaths":
            state_dict["new_deaths"] = data 
          elif name == "7-day moving average":
            state_dict["avg_deaths"] = data 
          #print (name + ": " + dates[3] + " : " + data[3])
    #except None as err:
      #print ("Couldn't load page for " + state.text_content() + ": ", end='')
      #print (err)
      #print (worldometers + state.get('href'))

    results.append(state_dict)

#json.dump(results,sys.stdout)
with open('result.json', 'w') as fp:
    json.dump(results, fp)

