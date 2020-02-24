import pandas as pd
import numpy as np

ind_dis = pd.read_csv('./data/individual_disasters.csv')
df = pd.read_csv('./data/census.csv')

def get_total_emps(zip_list):
    emps = 0
    for z in zip_list:
        try:
            emps += df[df['ZCTA'] == z]['EMP'].iloc[0]
        except:
            pass
    return emps

def get_avg_density(zip_list):
    total_dens = 0
    for z in zip_list:
        try:
            total_dens += df[df['ZCTA'] == z]['density'].iloc[0]
        except:
            pass
    avg_dens = total_dens / len(zip_list)
    return avg_dens

def get_households(zip_list):
    houses = 0
    for z in zip_list:
        try:
            houses += df[df['ZCTA'] == z]['n_households'].iloc[0]
        except:
            pass
    return houses

def get_pop_data(zip_list):
    pop = 0
    for z in zip_list:
        try:
            pop += df[df['ZCTA'] == z]['population'].iloc[0]
        except:
            pass
    return pop

#ind_dis['total_population'] = ind_dis['affected_zips'].apply(get_pop_data)

def get_inc(zip_list):
    inc = 0
    for z in zip_list:
        try:
            inc += df[df['ZCTA'] == z]['med_income'].iloc[0]
        except:
            pass
    return inc

#ind_dis['total_med_income'] = ind_dis['affected_zips'].apply(get_inc)

def get_payann(zip_list):
    payann = 0
    for z in zip_list:
        try:
            payann += df[df['ZCTA'] == z]['PAYANN'].iloc[0]
        except:
            pass
    return payann

#ind_dis['total_PAYANN'] = ind_dis['affected_zips'].apply(get_payann)

def get_estab(zip_list):
    estab = 0
    for z in zip_list:
        try:
            estab += df[df['ZCTA'] == z]['ESTAB'].iloc[0]
        except:
            pass
    return estab

#ind_dis['total_ESTAB'] = ind_dis['affected_zips'].apply(get_estab)