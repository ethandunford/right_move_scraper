# -- ---------------------------------------------------------------------------
# --
# -- Title:        right_move_scrapper.py
# -- Desc:         Scrapes right move
# -- License:      Apache License Version 2.0
# -- Author:       Ethan Dunford <github.com/ethandunford>
# -- Date:         19/12/2017
# -- Version:      1
# --
# -- ---------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui  import Select
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import time
import csv

class RightMove(object):

    def __init__(self):
        self.location      = None
        self.search_type   = None
        self.search_radius = 40.0
        self.min_price     = 'No min'
        self.max_price     = 'No max'
        self.min_bedrooms  = 'No max'
        self.max_bedrooms  = 'No max'
        self.property_type = 'Any'
        self.added_to_site = 'Anytime'
        self.distance      = 'Within 40 miles'
        self.argreed       = False
        self.csv_file      = 'right_move_properties'
        self.csv_headers   = ['priceValue', 'contactsPhoneNumber', 'title', 'address',
        'tagTitle', 'branchSummary', 'contactBranch', 'agent', 'properyUrl' ]

        # -- Rightmove form variables
        # -- -------------------------------------------------------------------

        self.raduis  = [(0, 'This area only'), (0.25, 'Within ¼ mile'), (0.5, 'Within ½ mile'),
        (1.0, 'Within 1 mile'), (3.0, 'Within 3 miles'),(5.0, 'Within 5 miles'),(10.0, 'Within 10 miles'),
        (15.0, 'Within 15 miles'), (20.0, 'Within 20 miles'), (30.0,'Within 30 miles'),(40.0, 'Within 40 miles')]

        self.price_range = { 'sale': ['50,000','60,000','70,000','80,000','90,000','100,000',
        '110,000','120,000','125,000', '130,000','140,000','150,000','160,000','170,000','175,000','180,000',
        '190,000','200,000','210,000','220,000','230,000','240,000','250,000','260,000','270,000','280,000',
        '290,000','300,000','325,000','350,000','375,000','400,000','425,000','450,000','475,000','500,000',
        '550,000','600,000','650,000','700,000','800,000','900,000','1,000,000','1,250,000','1,500,000',
        '1,750,000','2,000,000','2,500,000','3,000,000','4,000,000','5,000,000','7,500,000','10,000,000',
        '15,000,000','20,000,000'],'rent': ['100','150','200','250','300','350','400','450','500','600',
        '700','800','900','1,000','1,100','1,200','1,250','1,300','1,400','1,500','1,750','2,000','2,250',
        '2,500','2,750','3,000','3,500','4,000','4,500','5,000','5,500','6,000','6,500','7,000','8,000',
        '9,000','10,000','12,500','15,000','17,500','20,000','25,000','30,000','35,000','40,000']
        }

        self.no_of_beds     = ['Studio', '1', '2', '3', '4', '5']
        self.property_types = ['Any', 'Houses', 'Flats / Apartments', 'Bungalows', 'Land', 'Commercial', 'Property', 'Other']
        self.listing_peroid = ['Anytime', 'Last 24 hours', 'Last 3 days', 'Last 7 days', 'Last 14 days']

    #PCM for rental 'No min','No max',

    # -- csv tools
    # -- -----------------------------------------------------------------------

    def file_name(self, file_name):
        return '{0}_{1}{2}'.format(file_name,datetime.datetime.fromtimestamp(time.time()).strftime("%d%m%Y"), '.csv')

    def create_csv(self):
        csvfile    = open(self.file_name(self.csv_file), 'w')
        writer     = csv.DictWriter(csvfile, self.csv_headers)
        writer.writeheader()
        csvfile.close()

    def append_csv(self, data):
        csvfile    = open(self.file_name(self.csv_file), 'a')
        writer     = csv.DictWriter(csvfile, self.csv_headers)
        for d in data:
            writer.writerow(d)
        csvfile.close()

    # -- selenium tools
    # -- -----------------------------------------------------------------------

    def set_form_input_id(self, id, value):
        el = self.driver.find_element_by_id(id)
        el.clear()
        el.send_keys(value)

    def set_form_select_id(self, id, field_option):
        el = self.driver.find_element_by_id(id)
        for option in el.find_elements_by_tag_name('option'):
            if option.text == field_option:
                option.click()

    def set_form_select_class(self, class_name, field_option):
        el = self.driver.find_element_by_class_name(class_name)
        for option in el.find_elements_by_tag_name('option'):
            if option.text == field_option:
                option.click()

    def search(self):

        try:
            # search type buy / rent
            # --------------------------------------------
            self.set_form_input_id('searchLocation', self.location )
            self.driver.find_element_by_id(self.search_type).click()
            time.sleep(2)

            # -- Set radius
            # --------------------------------------------
            self.set_form_select_id('radius', self.distance)

            # -- Price range
            # --------------------------------------------
            self.set_form_select_id('minPrice', self.min_price)
            self.set_form_select_id('maxPrice', self.max_price)

            # -- No of bedrooms
            # --------------------------------------------
            self.set_form_select_id('minBedrooms', self.min_bedrooms)
            self.set_form_select_id('maxBedrooms', self.max_bedrooms)

            # -- Property type
            # --------------------------------------------
            self.set_form_select_id('displayPropertyType', self.property_type)

            # -- Added to site
            # --------------------------------------------
            self.set_form_select_id('maxDaysSinceAdded', self.added_to_site)

            # -- Include Under Offer, Sold STC
            # --------------------------------------------
            if self.argreed is True:
                self.driver.find_element_by_class_name('tickbox--indicator').click()

            # -- Perform search
            # --------------------------------------------
            self.driver.find_element_by_id('submit').click()

        except Exception as e:
            print('Error -> {0}'.format(e))
            self.driver.close()
            return False
        return True

    def get_properties(self):
        props_container = []
        properties      = self.driver.find_elements_by_class_name('is-list')

        for props in properties:
            if len(props.find_element_by_class_name('propertyCard-priceValue').text) > 0:
                props_container.append(
                {
                    'priceValue':          props.find_element_by_class_name('propertyCard-priceValue').text,
                    'contactsPhoneNumber': props.find_element_by_class_name('propertyCard-contactsPhoneNumber').text,
                    'title':               props.find_element_by_class_name('propertyCard-title').text.replace('for sale', '' ),
                    'address':             props.find_element_by_class_name('propertyCard-address').text,
                    'tagTitle':            props.find_element_by_class_name('propertyCard-tagTitle').text,
                    'branchSummary':       props.find_element_by_class_name('propertyCard-branchSummary-addedOrReduced').text,
                    'contactBranch':       props.find_element_by_class_name('propertyCard-branchSummary-addedOrReduced').text,
                    'agent':               props.find_element_by_class_name('propertyCard-branchLogo-link').get_attribute("href"),
                    'properyUrl':          props.find_element_by_class_name('propertyCard-img-link').get_attribute("href")
                }
                )

        return props_container

    def number_of_page(self):
        _pages = []
        el     = self.driver.find_element_by_class_name('pagination-dropdown')
        for option in el.find_elements_by_tag_name('option'):
            _pages.append(option.text)
        return _pages

    def scrape(self, location, search_type):
        self.location      = location
        self.search_type   = search_type
        self.driver        = webdriver.Chrome()
        self.driver.get('http://www.rightmove.co.uk/')
        time.sleep(2)
        search = self.search()
        time.sleep(2)

        if search is True:
            pages = self.number_of_page()
            self.create_csv()
            for page_number in pages:
                print('Scraping page -> {0}'.format(page_number))
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.append_csv(self.get_properties())
                self.driver.find_element_by_class_name('pagination-direction--next').click()
                time.sleep(2)
        self.drive.close()

a = RightMove()
a.scrape('Norwich', 'rent')
