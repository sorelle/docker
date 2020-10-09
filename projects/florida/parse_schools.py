from bs4 import BeautifulSoup
import pandas
import requests
import argparse
#from pathlib import Path
import os
import urllib.request, urllib.parse, urllib.error, json
from json_extract import flatten_json
import csv
import math

list_of_schools = []
parsed_data = pandas.DataFrame(columns = ['location_name', 'location_type', 'address', 'latitude', 'longitude'])
url = "https://web03.fldoe.org/Schools/schoolreport.asp?id="  # 1 - 67
url_header = "http://localhost:4000/v1/autocomplete?text="
parsed_unavailable_addresses = 0
total = 0
counter = 0

for x in range(1, 68):    
    page = requests.get(url + str(x))
    soup = BeautifulSoup(page.text, 'html.parser')
    school_name_raw = soup.find('table' , {'cellpadding':'4',  'cellspacing' : '0', 'border' : '0' })
    sections = school_name_raw.find_all('tr')   # first element will be the list of location types

    current_location_type = ''
    for index, tag in enumerate(sections):
        if index == 0:
            continue
        if tag.find('h3'):      # We're at a header for a new section 
            current_location_type = tag.find('h3').contents[0].strip()
            #print("LOCATION: " + current_location_type)
            continue
        place_tag = tag.find('td', {'style' : "border-bottom:#DDCFE6 1px solid;"}).contents[0].strip()      # No hyperlink
        address_tag = tag.find('br').next_sibling.strip()
        if not place_tag:
            place_tag = tag.find('a', {'style' : "font-size:100%"}).contents[0].strip()     # Hyperlinked
        if (address_tag.find('Unavailable') != -1):
            parsed_unavailable_addresses = parsed_unavailable_addresses + 1
        if (place_tag == 'Map'):
            continue

        latitude = ''
        longitude = ''

        response = urllib.request.urlopen(url_header + urllib.parse.quote((address_tag).encode('utf-8')))
        json_data = json.loads(response.read())
        coords = flatten_json(json_data)
        try:
            latitude = coords['features_0_geometry_coordinates_1']
            longitude = coords['features_0_geometry_coordinates_0']
            # print("found coords: " + str(coords['features_0_geometry_coordinates_1']) + ", " +str(coords['features_0_geometry_coordinates_0']))
        except KeyError:
            counter = counter + 1 
            # print("no coords")
            # print(full_location + " has no available coordinates, maybe its an address on a highway?")
        
        total = total + 1
        if total % 100 == 0:
            print(str(total) + " records processed")

        # print(("location: " + current_location_type))
        # print(("place: " + place_tag))
        # print(("address: " + address_tag))
        # print(("lat n long: +" + str(latitude) + " " + str(longitude)))
        parsed_data = parsed_data.append({'location_name': place_tag, 'location_type' : current_location_type, 'address' : address_tag, 'latitude' : latitude, 'longitude' : longitude},  ignore_index=True)

print(("Frame has " + str(len(parsed_data.index)) + " entries"))
parsed_data.to_csv("~/Downloads/fl_schools_statewide_latsandlongs.csv", mode='w', header=True, sep='\t', index=False)
print((str(counter) + " / " + str(total) + " had missing latitude/longitude"))
print((str(parsed_unavailable_addresses) + " had no address listed"))



        


            


