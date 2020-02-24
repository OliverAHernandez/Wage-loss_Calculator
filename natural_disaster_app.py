import numpy as np
import pandas as pd
import pickle
import re
from flask import Flask, request, Response, render_template

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

from area_stats_methods import *

ind_dis = pd.read_csv('./data/individual_disasters.csv')
df = pd.read_csv('./data/census.csv')

#instantiating app
app = Flask('NaturalDisaster')

@app.route('/form')

def form():
    return render_template('form.html')

def get_affected_area(central_zip, severity):

    center = (float(df[df['ZCTA'] == central_zip]['lat']), float(df[df['ZCTA'] == central_zip]['lng']))

    polygon = Polygon([
        (center[0] - severity, center[1]), 
        (center[0], center[1] + severity),
        (center[0] + severity, center[1]),
        (center[0], center[1] - severity)
    ])

    affected_zips = []
    for i in range(df.shape[0]):
        point = Point(df.loc[i, 'lat'], df.loc[i, 'lng'])
        if polygon.contains(point):
            affected_zips.append(df.loc[i, 'ZCTA'])
    return affected_zips

def input_disaster(central_zip, severity):
    area_stats = {}
    affected_zips = get_affected_area(central_zip, severity)
    area_stats['total_population'] = get_pop_data(affected_zips)
    area_stats['total_households'] = get_households(affected_zips)
    area_stats['average_population_density'] = get_avg_density(affected_zips)
    area_stats['total_employees'] = get_total_emps(affected_zips)
    
    #area_stats['total_income'] = get_inc(affected_zips) * area_stats['total_population']
    area_stats['total_income'] = get_payann(affected_zips) * 1000 #(payann is in thousands)
    
    area_stats['total_businesses'] = get_estab(affected_zips)
    return area_stats

@app.route('/submit')



def submit():
    user_input = request.args
    print(*user_input, sep='\n')
    
    severity = float(user_input['severity'])
    central_zip = int(user_input['central_zip'])
    disaster_type = str(user_input['disaster_type'])
    
    area_stats = input_disaster(central_zip, severity)
    total_pop = area_stats['total_population']
    affected_zips_count = len(get_affected_area(central_zip, severity))
    
    earthquake = 0
    hurricane = 0
    tornado = 0
    wildfire = 0

    if disaster_type == 'earthquake':
        earthquake = 1
    elif disaster_type == 'hurricane':
        hurricane = 1
    elif disaster_type == 'tornado':
        tornado = 1
    elif disaster_type == 'wildfire':
        wildfire = 1

    # create list that contains dictionary of inputs for model
    data = [{
            'severity': severity,
            'affected_zips_count': affected_zips_count,
            'total_pop': total_pop,
            'earthquake': earthquake,
            'hurricane': hurricane,
            'tornado': tornado,
            'wildfire': wildfire,
            }]
    
    data_df = pd.DataFrame(data,index = [0])
    data_df = data_df[[
        'severity',
        'affected_zips_count',
        'total_pop',
        'earthquake',
        'hurricane',
        'tornado',
        'wildfire']]
    
    X = ind_dis[[
    'severity', 
    'affected_zips_count', 
    'total_population',
    'earthquake',
    'hurricane',
    'wildfire',
    'tornado']]
    y = ind_dis['displaced']

    ss = StandardScaler()
    X_scaled = ss.fit_transform(X)
    
    scaled_data_df = ss.transform(data_df)
    

    # load pickled model
    model = pickle.load(open('wageloss_rfr.pkl', 'rb'))

    displaced = model.predict(scaled_data_df)
    percent_displaced = displaced / area_stats['total_population']
    
    earners_per_household = 1.2
    earners = earners_per_household * area_stats['total_households']
    percent_earners = earners / area_stats['total_population']
    
    percent_displaced_earners = percent_displaced * percent_earners
    
    total_annual_loss = percent_displaced_earners * area_stats['total_income']
    total_daily_loss = total_annual_loss / 365
    
    if disaster_type == 'earthquake':
        url = 'https://media.nature.com/w700/magazine-assets/d41586-018-04258-2/d41586-018-04258-2_15593332.jpg'
    elif disaster_type == 'hurricane':
        url = 'https://s7d2.scene7.com/is/image/TWCNews/hurricane_florencejpg'
    elif disaster_type == 'tornado':
        url = 'https://sophosnews.files.wordpress.com/2019/03/shutterstock_626537093-compressor.jpg?w=780&h=408&crop=1g'
    elif disaster_type == 'wildfire':
        url = 'https://www.economist.com/sites/default/files/images/print-edition/20180804_STP001_0.jpg'
    
    return render_template(
        'results.html',
        area_stats = area_stats,
        displaced = int(displaced[0]),
        percent_displaced = round((percent_displaced[0]*100),4),
        earners = earners,
        percent_earners = round(percent_earners*100, 4),
        total_daily_loss = round(total_daily_loss[0], 2),
        affected_zips_count = affected_zips_count,
        total_population = area_stats['total_population'],
        total_households = area_stats['total_households'],
        total_businesses = area_stats['total_businesses'],
        average_population_density = int(area_stats['average_population_density']),
        url=url)

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(debug=True)

