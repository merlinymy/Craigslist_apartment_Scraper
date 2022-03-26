#!/usr/bin/env python
# coding: utf-8

# In[1]:

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LightYellow='\033[93m'

    Bold='\033[1m'
    Underlined='\033[4m'
    Blink='\033[5m'
    Inverted='\033[7m'
    Hidden='\033[8m'

    Black='\033[30m'
    Red='\033[31m'
    Green='\033[32m'
    Yellow='\033[33m'
    Blue='\033[34m'
    Purple='\033[35m'
    Cyan='\033[36m'
    LightGray='\033[37m'
    DarkGray='\033[30m'
    LightRed='\033[31m'
    LightGreen='\033[32m'
    LightYellow='\033[93m'
    LightBlue='\033[34m'
    LightPurple='\033[35m'
    LightCyan='\033[36m'
    White='\033[97m'

    BckgrDefault='\033[49m'
    BckgrBlack='\033[40m'
    BckgrRed='\033[41m'
    BckgrGreen='\033[42m'
    BckgrYellow='\033[43m'
    BckgrBlue='\033[44m'
    BckgrPurple='\033[45m'
    BckgrCyan='\033[46m'
    BckgrLightGray='\033[47m'
    BckgrDarkGray='\033[100m'
    BckgrLightRed='\033[101m'
    BckgrLightGreen='\033[102m'
    BckgrLightYellow='\033[103m'
    BckgrLightBlue='\033[104m'
    BckgrLightPurple='\033[105m'
    BckgrLightCyan='\033[106m'
    BckgrWhite='\033[107m'

    Achtung=LightRed+Bold+Blink
    Error=LightRed+Bold
def get_apartments():
    
    import googlemaps
    import pandas as pd
    from requests import get
    from datetime import datetime
    from bs4 import BeautifulSoup
    from time import sleep
    import re
    from random import randint #avoid throttling by not sending too many requests one after the other
    from warnings import warn
    from time import time
    from IPython.core.display import clear_output
    import numpy as np
    
    def parse_time(time):
        if not pd.isna(time.strip()):
            mins = 0
            fields=re.findall(r'[A-Za-z]+|\d+', time.strip())
            #print(fields) #inserted this line to debug why output was 0
            for idx in range(0, len(fields)-1):
                if fields[idx+1] in ('min', 'mins', 'minutes'):
                    mins += int(fields[idx])
                elif fields[idx+1] in ('h', 'hour', 'hours'):
                    mins += int(fields[idx]) * 60

            return mins


    post_timing = []
    post_hoods = []
    post_title_texts = []
    bedroom_counts = []
    sqfts = []
    post_links = []
    post_prices = []
    walking_time = []
    biking_time = []
    public_transit_time = []

        #get request
    max_price = input(f"{bcolors.OKCYAN}Enter Maximum Price: ${bcolors.ENDC}")
    min_price = input(f"{bcolors.OKCYAN}Enter Minimum Price: ${bcolors.ENDC}")
    bedroom_num = input(f"{bcolors.OKCYAN}Enter Minimum Bedrooms:{bcolors.ENDC}")
    bathroom_num = input(f"{bcolors.OKCYAN}Enter Minimum Bathrooms:{bcolors.ENDC}")
    postal = input(f"{bcolors.OKCYAN}Enter Postal Code:{bcolors.ENDC}")
    distance = input(f"{bcolors.OKCYAN}Enter Search Distance (miles):{bcolors.ENDC}")


    url = f'https://chicago.craigslist.org/search/hhh?hasPic=1&search_distance={distance}&postal={postal}&min_price={min_price}&max_price={max_price}&min_bedrooms={bedroom_num}&min_bathrooms={bathroom_num}&availabilityMode=0&sale_date=all+dates'
    response = get(url)
    #throw warning for status codes that are not 200
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    #define the html text
    page_html = BeautifulSoup(response.text, 'html.parser')

    #define the posts
    posts = page_html.find_all('li', class_= 'result-row')

    #find the total number of posts to find the limit of the pagination
    results_num = page_html.find('div', class_= 'search-legend')
    results_total = int(results_num.find('span', class_='totalcount').text) #pulled the total count of posts as the upper bound of the pages array

    #each page has 119 posts so each new page is defined as follows: s=120, s=240, s=360, and so on. So we need to step in size 120 in the np.arange function
    pages = np.arange(0, results_total+1, 120)
    MY_KEY = "AIzaSyBeKXFT-0g8nPb4N0IrDvP0TkJLGr30H7c"
    appartment_counter =0
    iterations = 0

    for page in pages:
        url_page = f'{url}&s={page}'
        response_page = get(url_page)
        sleep(randint(1,5))
         #throw warning for status codes that are not 200
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response_page.status_code))

        #define the html text
        page_html = BeautifulSoup(response_page.text, 'html.parser')

        #define the posts
        posts = page_html.find_all('li', class_= 'result-row')


        #extract data item-wise
        for post in posts:

            if post.find('span', class_ = 'result-hood') is not None:

                #posting date
                #grab the datetime element 0 for date and 1 for time
                post_datetime = post.find('time', class_= 'result-date')['datetime']
                post_timing.append(post_datetime)

                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} posting date retrieved: {post_datetime}{bcolors.ENDC}")

                #neighborhoods
                post_hood = post.find('span', class_= 'result-hood').text
                post_hoods.append(post_hood)

                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} neighborhood information retrieved: {post_hood}{bcolors.ENDC}")



                #title text
                post_title = post.find('a', class_='result-title hdrlnk')
                post_title_text = post_title.text
                post_title_texts.append(post_title_text)
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} title text retrieved: {post_title_text}{bcolors.ENDC}")


                #post link
                post_link = post_title['href']
                post_links.append(post_link)
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} URL retrieved: {post_link}{bcolors.ENDC}")



                ###get deeper into the link
                #get address
                post_response = get(post_link)

                page_html_soup = BeautifulSoup(post_response.text, 'html.parser')

                ## lat and long
                ## lat and long
                latlonglist = page_html_soup.find_all(attrs={"data-latitude": True, "data-longitude": True})
                for latlong in latlonglist:
                    latitude = latlong['data-latitude']
                    longtitude = latlong['data-longitude']
                latlon = latitude + ', ' + longtitude
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} latitude longtitude Retrieved: {latitude}, {longtitude}{bcolors.ENDC}")
                ## use google map find walking, biking and transit duration

                UIC_LAT_LONG = "41.87072, -87.67085"


                gmaps = googlemaps.Client(key = MY_KEY)


                now = datetime.now()
                walking_result = gmaps.directions(UIC_LAT_LONG,
                                                     latlon,
                                                     mode="walking"
                                                    )
                biking_result = gmaps.directions(UIC_LAT_LONG,
                                                     latlon,
                                                     mode="bicycling"
                                                    )

                bus_result = gmaps.directions(UIC_LAT_LONG,
                                                     latlon,
                                                     mode="transit"
                                                    )
                if not walking_result:
                    walking_time.append(np.nan)
                else: 
                    walking_time.append(walking_result[0]['legs'][0]['duration']['text'])

                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} walking duration retrieved: {walking_result[0]['legs'][0]['duration']['text']}{bcolors.ENDC}")

                if not biking_result:
                    biking_time.append(np.nan)
                else:
                    biking_time.append(biking_result[0]['legs'][0]['duration']['text'])
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} biking duration retrieved: {biking_result[0]['legs'][0]['duration']['text']}{bcolors.ENDC}")

                try:
                    if not bus_result: 
                        public_transit_time.append(np.nan)
                    else:
                        public_transit_time.append(bus_result[0]['legs'][0]['duration']['text'])
                    print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} public transit duration retrieved: {bus_result[0]['legs'][0]['duration']['text']}{bcolors.ENDC}")
                except IndexError:
                    print(f"{bcolors.Error}Public transportation not available.{bcolors.ENDC}")






                #removes the \n whitespace from each side, removes the currency symbol, and turns it into an int
                post_price = post.a.text.strip().replace("$", "").replace(",", "")
                post_prices.append(post_price)
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} rent retrieved: {post_price}{bcolors.ENDC}")


                if post.find('span', class_ = 'housing') is not None:

                    #if the first element is accidentally square footage
                    if 'ft2' in post.find('span', class_ = 'housing').text.split()[0]:

                        #make bedroom nan
                        bedroom_count = np.nan
                        bedroom_counts.append(bedroom_count)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} bedroom number retrieved: {bedroom_count}{bcolors.ENDC}")

                        #make sqft the first element
                        sqft = int(post.find('span', class_ = 'housing').text.split()[0][:-3])
                        sqfts.append(sqft)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} sqfts retrieved: {sqft}{bcolors.ENDC}")


                    #if the length of the housing details element is more than 2
                    elif len(post.find('span', class_ = 'housing').text.split()) > 2:

                        #therefore element 0 will be bedroom count
                        bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                        bedroom_counts.append(bedroom_count)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} bedroom number retrieved: {bedroom_count}{bcolors.ENDC}")

                        #and sqft will be number 3, so set these here and append
                        sqft = int(post.find('span', class_ = 'housing').text.split()[2][:-3])
                        sqfts.append(sqft)

                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} sqfts retrieved: {sqft}{bcolors.ENDC}")               

                    #if there is num bedrooms but no sqft
                    elif len(post.find('span', class_ = 'housing').text.split()) == 2:

                        #therefore element 0 will be bedroom count
                        bedroom_count = post.find('span', class_ = 'housing').text.replace("br", "").split()[0]
                        bedroom_counts.append(bedroom_count)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} bedroom number retrieved: {bedroom_count}{bcolors.ENDC}")

                        #and sqft will be number 3, so set these here and append
                        sqft = np.nan
                        sqfts.append(sqft)          
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} sqfts retrieved: {sqft}{bcolors.ENDC}")          

                    else:
                        bedroom_count = np.nan
                        bedroom_counts.append(bedroom_count)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} bedroom number retrieved: {bedroom_count}{bcolors.ENDC}")

                        sqft = np.nan
                        sqfts.append(sqft)
                        print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} sqfts retrieved: {sqft}{bcolors.ENDC}")

                #if none of those conditions catch, make bedroom nan, this won't be needed    
                else:
                    bedroom_count = np.nan
                    bedroom_counts.append(bedroom_count)
                    print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} bedroom number retrieved: {bedroom_count}{bcolors.ENDC}")

                    sqft = np.nan
                    sqfts.append(sqft)
                    print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN} sqfts retrieved: {sqft}{bcolors.ENDC}")
                #    bedroom_counts.append(bedroom_count)

                #    sqft = np.nan
                #    sqfts.append(sqft)



                
                print(f"{bcolors.OKBLUE}Apartment {appartment_counter + 1}{bcolors.ENDC}"+f"{bcolors.OKGREEN}{bcolors.BOLD} all data retrieved{bcolors.ENDC}")
                appartment_counter += 1
                print("\n")
        iterations += 1
        print(f"{bcolors.LightYellow}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n{bcolors.ENDC}")
        print(f"{bcolors.LightYellow}Page {iterations} scraped successfully!\n{bcolors.ENDC}")
        print(f"{bcolors.LightYellow}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n{bcolors.ENDC}\n")



    print(f"{bcolors.LightYellow}{bcolors.BOLD}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n{bcolors.ENDC}")
    print(f"{bcolors.LightYellow}{bcolors.BOLD}Scrape complete!{bcolors.ENDC}\n")
    print(f"{bcolors.LightYellow}{bcolors.BOLD}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n{bcolors.ENDC}\n\n")
    
    chicago_crag_apts = pd.DataFrame({'posted_time':post_timing,
                                 'neighborhood':post_hoods,
                                 'post_title':post_title_texts,
                                 'bedrooms':bedroom_counts,
                                 'sqfts':sqfts,
                                 'price':post_prices,
                                 'walking_time':walking_time,
                                 'biking_time':biking_time,
                                 'public_transit_time':public_transit_time,
                                 'links':post_links})
    try:
        chicago_crag_apts['biking_time'] = chicago_crag_apts['biking_time'].map(parse_time)
        chicago_crag_apts['public_transit_time'] = chicago_crag_apts['public_transit_time'].map(parse_time)
        chicago_crag_apts['walking_time'] = chicago_crag_apts['walking_time'].map(parse_time)
    except AttributeError:
        print(f"{bcolors.Error}can't convert public transit time{bcolors.ENDC}")
    file_name = input(f"{bcolors.OKCYAN}Enter file name (no file type needed): {bcolors.ENDC}")
    saved_path = f"/Users/Merlin/Downloads/{file_name}.csv"
    chicago_crag_apts.to_csv(saved_path,index = False)
    print(f"{bcolors.LightYellow}{bcolors.BOLD}CSV file export complete! Export to {saved_path}{bcolors.ENDC}")
get_apartments()

# In[ ]:




