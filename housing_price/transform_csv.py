import pandas as pd
import re
import json


pd.set_option('display.max_column', None)

data = pd.read_csv('dataset/avito_house.csv')
data = data.drop(['web-scraper-order', 'web-scraper-start-url', 'name-href', 'name'], axis=1)
data = data.drop(index=762).reset_index(drop=True)
def split_area(area):
    area = area.split('\xa0')
    area = area[0].split(':')
    return area[1]

def descript(desc):
    rooms = None
    kitchen_area = None
    total_area = None
    living_area = None
    ceiling_height = None
    studio = 'no'
    open_plan = 'no'
    floor = None
    total_floor = None
    balcony = None
    bathrooms = None
    repair = None
    for i in desc:
        if 'оличество комнат' in i:
            i = i.split(':')
            if 'студия' in i[1]:
                studio = 'yes'
                rooms = 0
            if 'планировка' in i[1]:
                open_plan = 'yes'
                rooms = 'no_info'
            if rooms !=0:
                rooms = i[1]
        if 'бщая площадь' in i:
            total_area = float(split_area(i))
        if 'кухни' in i:
            kitchen_area = float(split_area(i))
        if 'илая площадь' in i:
            living_area =  float(split_area(i))
        if 'таж:' in i:
            i = i.split(':')
            i = i[1].split('из')
            floor = int(i[0])
            total_floor = int(i[1])
        if 'ысота потолков' in i:
            ceiling_height = float(split_area(i))
        if 'лоджия' in i:
            i = i.split(':')
            balcony = i[1]
        if 'анузел' in i:
            i = i.split(':')
            bathrooms = i[1]
        if 'емонт' in i:
            i = i.split(':')
            repair = i[1]
    return rooms, total_area, kitchen_area, living_area, \
           ceiling_height, floor, total_floor, balcony, \
           bathrooms, repair, studio, open_plan


def params_dict(data):
    for_json = []
    year_of_construction = None
    house_type = None
    district_name = None
    price = None
    for row in range(len(data)):
        if 'от' in data.loc[row, 'price']:
            data.loc[row, 'price'] = data.loc[row, 'price'].split()[1]
        try:
            price = int(data.loc[row, 'price'].replace('\xa0', ''))
        except:
            price = int(data.loc[row, 'price'].replace('\xa0', '')[:-1])
        if  pd.isnull(data.loc[row, 'year_of_construction']):
            year_of_construction = None
        elif 'Год' in data.loc[row, 'year_of_construction'] :
            year_of_construction = int(data.loc[row, 'year_of_construction'].split(':')[1])
        else:
            year_of_construction = None
        house_type = data.loc[row, 'house_type'].split(':')[1]
        district_name = data.loc[row, 'area']
        desc = data.loc[row, 'descript']
        desc_split = re.split('[А-Я]', desc)
        params_desc = descript(desc_split)
        params = {
            'rooms': params_desc[0],
            'studio': params_desc[10],
            'open_plan': params_desc[-1],
            'kitchen_area': params_desc[2],
            'total_area': params_desc[1],
            'living_area': params_desc[3],
            'ceiling_height': params_desc[4],
            'floor': params_desc[5],
            'total_floor': params_desc[6],
            'balcony': params_desc[7],
            'bathrooms': params_desc[8],
            'repair': params_desc[9],
            'year_of_construction': year_of_construction,
            'house_type': house_type,
            'district_name': district_name,
            'price': price
        }

        for_json.append(params)
    return for_json

for_json = params_dict(data)

with open("dataset/housing_price_dict.json", "w", encoding='utf-8') as file:
    json.dump(for_json, file, indent=4, ensure_ascii=False)