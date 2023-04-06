
import os
import glob
import pandas as pd
import db_connect
import sqlalchemy as sal
import csv
import psycopg2


# connect to new DB to be populated with Viasat data after route-check
conn_HAIG = db_connect.connect_HAIG_ROMA()
cur_HAIG = conn_HAIG.cursor()


##########################################################
### Check routecheck DB ##################################
##########################################################

#### check how many TRIP ID we have ######################

# get all ID terminal of Viasat data
idterm = pd.read_sql_query(
    ''' SELECT DISTINCT "idterm" 
        FROM public.routecheck_trenta_bis ''', conn_HAIG)

# make a list of all unique trips
processed_idterms = list(idterm.idterm.unique())
## transform all elements of the list into integers
processed_idterms = list(map(int, processed_idterms))
print(len(processed_idterms))

## reload 'all_idterms' as list
with open("D:/ENEA_CAS_WORK/ROMA_2019/all_idterms.txt", "r") as file:
    all_ID_TRACKS = eval(file.readline())
print(len(all_ID_TRACKS))
## make difference between all idterm and processed idterms

all_ID_TRACKS_DIFF = list(set(all_ID_TRACKS) - set(processed_idterms))
print(len(all_ID_TRACKS_DIFF))

# ## save 'all_ID_TRACKS' as list
with open("D:/ENEA_CAS_WORK/ROMA_2019/all_idterms_new.txt", "w") as file:
    file.write(str(all_ID_TRACKS_DIFF))




# get all ID terminal of Viasat data
idtrajectory = pd.read_sql_query(
    ''' SELECT DISTINCT "idtrajectory" 
        FROM public.routecheck_trenta ''', conn_HAIG)

# make a list of all unique trips
processed_idtrajectory = list(idtrajectory.idtrajectory.unique())
## transform all elements of the list into integers
processed_idtrajectory = list(map(int, processed_idtrajectory))
print(len(processed_idtrajectory))

##########################################################
### Check route DB #######################################
##########################################################

#### check how many TRIP ID we have ######################

# get all ID terminal of Viasat data
idterm = pd.read_sql_query(
    ''' SELECT DISTINCT "idterm" 
        FROM public.route_cinque ''', conn_HAIG)

# make a list of all unique trips
processed_idterms = list(idterm.idterm.unique())
## transform all elements of the list into integers
processed_idterms = list(map(int, processed_idterms))
print(len(processed_idterms))

## reload 'all_idterms' as list
with open("D:/ENEA_CAS_WORK/ROMA_2019/idterms_2019.txt", "r") as file:
    all_ID_TRACKS = eval(file.readline())
print(len(all_ID_TRACKS))
## make difference between all idterm and processed idterms

all_ID_TRACKS_DIFF = list(set(all_ID_TRACKS) - set(processed_idterms))
print(len(all_ID_TRACKS_DIFF))

# ## save 'all_ID_TRACKS' as list
with open("D:/ENEA_CAS_WORK/ROMA_2019/idterms_2019_new.txt", "w") as file:
    file.write(str(all_ID_TRACKS_DIFF))


# get all ID terminal of Viasat data
idtrajectory = pd.read_sql_query(
    ''' SELECT DISTINCT "idtrajectory" 
        FROM public.route_trenta ''', conn_HAIG)

# make a list of all unique trips
processed_idtrajectory = list(idtrajectory.idtrajectory.unique())
## transform all elements of the list into integers
processed_idtrajectory = list(map(int, processed_idtrajectory))
print(len(processed_idtrajectory))




##################################################################
##################################################################

