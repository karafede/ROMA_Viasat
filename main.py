
import os
import pandas as pd

from load_DB import obu
from load_DB import upload_DB
from load_DB import idterm_vehtype_portata
from routecheck_viasat_ROMA_FK import func
import glob
import db_connect
import sqlalchemy as sal
import multiprocessing as mp
from sqlalchemy import exc
import sqlalchemy as sal
from sqlalchemy.pool import NullPool

os.chdir('D:/ViaSat/VIASAT_RM/obu')
cwd = os.getcwd()
## load OBU data (idterm, vehicle type and other metadata)
obu_CSV = "VST_ENEA_ROMA_ANAG_20191209.csv"

### upload Viasat data for into the DB (only dataraw, NOT OBU data!!!)
extension = 'csv'
os.chdir('D:/ViaSat/VIASAT_RM')
viasat_filenames = glob.glob('*.{}'.format(extension))

# connect to new DB to be populated with Viasat data
conn_HAIG = db_connect.connect_HAIG_ROMA()
cur_HAIG = conn_HAIG.cursor()

'''

cur_HAIG.execute("""
    CREATE EXTENSION postgis
""")

cur_HAIG.execute("""
CREATE EXTENSION postgis_topology
""")
conn_HAIG.commit()

'''
#########################################################################################
### upload OBU data into the DB. Create table with idterm, vehicle type and put into a DB

os.chdir('D:/ViaSat/VIASAT_RM/obu')
obu(obu_CSV)

### upload viasat data into the DB  # long time run...
os.chdir('D:/ViaSat/VIASAT_RM')
upload_DB(viasat_filenames)


###########################################################
### ADD a SEQUENTIAL ID to the dataraw table ##############
###########################################################


## add geometry WGS84 4286
cur_HAIG.execute("""
alter table dataraw add column geom geometry(POINT,4326)
""")

cur_HAIG.execute("""
update dataraw set geom = st_setsrid(st_point(longitude,latitude),4326)
""")
conn_HAIG.commit()



# long time run...
## create a consecutive ID for each row  (----->>> order by ideterm and timedate......)
cur_HAIG.execute("""
alter table "dataraw" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


#### add an index to the "idterm"
cur_HAIG.execute("""
CREATE index dataraw_idterm_idx on public.dataraw(idterm);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index dataraw_timedate_idx on public.dataraw(timedate);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index dataraw_vehtype_idx on public.dataraw(vehtype);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index dataraw_id_idx on public.dataraw("id");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index dataraw_lat_idx on public.dataraw(latitude);
""")
conn_HAIG.commit()

cur_HAIG.execute("""
CREATE index dataraw_lon_idx on public.dataraw(longitude);
""")
conn_HAIG.commit()

cur_HAIG.execute("""
CREATE index dataraw_geom_idx on public.dataraw(geom);
""")
conn_HAIG.commit()


########################################################################################
#### create table with 'idterm', 'vehtype' and 'portata' and load into the DB ##########

idterm_vehtype_portata()   # long time run...

## add an index to the 'idterm' column of the "idterm_portata" table
cur_HAIG.execute("""
CREATE index idtermportata_idterm_idx on public.idterm_portata(idterm);
""")
conn_HAIG.commit()

## add an index to the 'idterm' column of the "obu" table
cur_HAIG.execute("""
CREATE index obu_idterm_idx on public.obu(idterm);
""")
conn_HAIG.commit()


#########################################################################################
#########################################################################################
##### create table routecheck ###########################################################

## multiprocess.....
os.chdir('D:/ENEA_CAS_WORK/ROMA_2019')
os.getcwd()

# Create an SQL connection engine to the output DB
engine = sal.create_engine('postgresql://postgres:superuser@10.1.0.1:5432/HAIG_ROMA', poolclass=NullPool)

# get all ID terminal of Viasat data
all_VIASAT_IDterminals = pd.read_sql_query(
    ''' SELECT *
        FROM public.idterm_portata''', conn_HAIG)
all_VIASAT_IDterminals['idterm'] = all_VIASAT_IDterminals['idterm'].astype('Int64')
all_VIASAT_IDterminals['portata'] = all_VIASAT_IDterminals['portata'].astype('Int64')

# make a list of all IDterminals (GPS ID of Viasata data) each ID terminal (track) represent a distinct vehicle
all_ID_TRACKS = list(all_VIASAT_IDterminals.idterm.unique())


## pool = mp.Pool(processes=mp.cpu_count()) ## use all available processors
pool = mp.Pool(processes=10)     ## use 55 processors
print("++++++++++++++++ POOL +++++++++++++++++", pool)
## use the function "func" defined in "routecheck_viasat_ROMA_FK.py" to run multitocessing...
# results = pool.map(func, [(last_track_idx, track_ID) for last_track_idx, track_ID in enumerate(all_ID_TRACKS)])
pool.close()
pool.join()

'''
### to terminate multiprocessing
pool.terminate()
'''

#################################################################################
## add indices routecheck #######################################################

### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.routecheck ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()

cur_HAIG.execute("""
CREATE index routecheck_id_idx on public.routecheck("id");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_idterm_idx on public.routecheck("idterm");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_TRIP_ID_idx on public.routecheck("TRIP_ID");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_idtrajectory_ID_idx on public.routecheck("idtrajectory");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_timedate_idx on public.routecheck("timedate");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_grade_idx on public.routecheck("grade");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_anomaly_idx on public.routecheck("anomaly");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_speed_idx on public.routecheck("speed");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_lat_idx on public.routecheck(latitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_lon_idx on public.routecheck(longitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_border_idx on public.routecheck(border);
""")
conn_HAIG.commit()


### --->>>>>   routecheck trenta <<<<<----------------------------------------------
####################################################################################


### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.routecheck_trenta_bis ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()

cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_id_idx on public.routecheck_trenta_bis("id");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_idterm_idx on public.routecheck_trenta_bis("idterm");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_TRIP_ID_idx on public.routecheck_trenta_bis("TRIP_ID");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_idtrajectory_ID_idx on public.routecheck_trenta_bis("idtrajectory");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_timedate_idx on public.routecheck_trenta_bis("timedate");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_grade_idx on public.routecheck_trenta_bis("grade");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_anomaly_idx on public.routecheck_trenta_bis("anomaly");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_speed_idx on public.routecheck_trenta_bis("speed");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_lat_idx on public.routecheck_trenta_bis(latitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_lon_idx on public.routecheck_trenta_bis(longitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_trenta_bis_border_idx on public.routecheck_trenta_bis(border);
""")
conn_HAIG.commit()

####################################################################################
####################################################################################

### --->>>>>   routecheck cinque <<<<<----------------------------------------------
####################################################################################


### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.routecheck_cinque ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()

cur_HAIG.execute("""
CREATE index routecheck_cinque_id_idx on public.routecheck_cinque("id");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_idterm_idx on public.routecheck_cinque("idterm");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_cinque_TRIP_ID_idx on public.routecheck_cinque("TRIP_ID");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_idtrajectory_ID_idx on public.routecheck_cinque("idtrajectory");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_timedate_idx on public.routecheck_cinque("timedate");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_grade_idx on public.routecheck_cinque("grade");
""")
conn_HAIG.commit()



cur_HAIG.execute("""
CREATE index routecheck_cinque_anomaly_idx on public.routecheck_cinque("anomaly");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_speed_idx on public.routecheck_cinque("speed");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_lat_idx on public.routecheck_cinque(latitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_lon_idx on public.routecheck_cinque(longitude);
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index routecheck_cinque_border_idx on public.routecheck_cinque(border);
""")
conn_HAIG.commit()

####################################################################################
####################################################################################


####################################################################################
####################################################################################
##### create table route ###########################################################


## multiprocess.....
os.chdir('D:/ENEA_CAS_WORK/ROMA_2019')
os.getcwd()

# Create an SQL connection engine to the output DB
engine = sal.create_engine('postgresql://postgres:superuser@10.1.0.1:5432/HAIG_ROMA')


#### setup multiprocessing.......



# long time run...
## create a consecutive ID for each row
cur_HAIG.execute("""
alter table "route_trenta_bis" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


## create an ndex on the "id" field
cur_HAIG.execute("""
CREATE index route_trenta_bis_id_idx on public.route_trenta_bis("id");
""")
conn_HAIG.commit()



### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.route_trenta_bis ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


### create index for 'idterm'
cur_HAIG.execute("""
CREATE index route_trenta_bis_idterm_idx on public.route_trenta_bis(idterm);
""")
conn_HAIG.commit()


### create index for 'idtrajectory'
cur_HAIG.execute("""
CREATE index route_trenta_bis_idtrajectory_idx on public.route_trenta_bis(idtrajectory);
""")
conn_HAIG.commit()


### create index for 'tripdistance_m'
cur_HAIG.execute("""
CREATE index route_trenta_bis_tripdistance_idx on public.route_trenta_bis(tripdistance_m);
""")
conn_HAIG.commit()


### create index for 'timedate_o'
cur_HAIG.execute("""
CREATE index route_trenta_bis_timedate_idx on public.route_trenta_bis(timedate_o);
""")
conn_HAIG.commit()


### create index for 'breaktime_s'
cur_HAIG.execute("""
CREATE index route_trenta_bis_breaktime_idx on public.route_trenta_bis(breaktime_s);
""")
conn_HAIG.commit()


### create index for 'triptime_s'
cur_HAIG.execute("""
CREATE index route_trenta_bis_triptime_s_idx on public.route_trenta_bis(triptime_s);
""")
conn_HAIG.commit()



### create index for 'deviation_pos_m'
cur_HAIG.execute("""
CREATE index route_trenta_bis_deviation_pos_idx on public.route_trenta_bis(deviation_pos_m);
""")
conn_HAIG.commit()

### create index for 'border_flag'
cur_HAIG.execute("""
CREATE index route_trenta_bis_border_flag_idx on public.route_trenta_bis(border_flag);
""")
conn_HAIG.commit()

#######################################################################
###########--- route_trenta_bis #######################################


# long time run...
## create a consecutive ID for each row
cur_HAIG.execute("""
alter table "route_trenta_bis" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


## create an ndex on the "id" field
cur_HAIG.execute("""
CREATE index route_trenta_bis_id_idx on public.route_trenta_bis("id");
""")
conn_HAIG.commit()



### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.route_trenta_bis ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


### create index for 'idterm'
cur_HAIG.execute("""
CREATE index route_trenta_bis_idterm_idx on public.route_trenta_bis(idterm);
""")
conn_HAIG.commit()


### create index for 'idtrajectory'
cur_HAIG.execute("""
CREATE index route_trenta_bis_idtrajectory_idx on public.route_trenta_bis(idtrajectory);
""")
conn_HAIG.commit()


### create index for 'tripdistance_m'
cur_HAIG.execute("""
CREATE index route_trenta_bis_tripdistance_idx on public.route_trenta_bis(tripdistance_m);
""")
conn_HAIG.commit()


### create index for 'timedate_o'
cur_HAIG.execute("""
CREATE index route_trenta_bis_timedate_idx on public.route_trenta_bis(timedate_o);
""")
conn_HAIG.commit()


### create index for 'breaktime_s'
cur_HAIG.execute("""
CREATE index route_trenta_bis_breaktime_idx on public.route_trenta_bis(breaktime_s);
""")
conn_HAIG.commit()


### create index for 'triptime_s'
cur_HAIG.execute("""
CREATE index route_trenta_bis_triptime_s_idx on public.route_trenta_bis(triptime_s);
""")
conn_HAIG.commit()



### create index for 'deviation_pos_m'
cur_HAIG.execute("""
CREATE index route_trenta_bis_deviation_pos_idx on public.route_trenta_bis(deviation_pos_m);
""")
conn_HAIG.commit()

### create index for 'border_flag'
cur_HAIG.execute("""
CREATE index route_trenta_bis_border_flag_idx on public.route_trenta_bis(border_flag);
""")
conn_HAIG.commit()



#######################################################################
###########--- route_trenta_tris #######################################


# long time run...
## create a consecutive ID for each row
cur_HAIG.execute("""
alter table "route_trenta_tris" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


## create an ndex on the "id" field
cur_HAIG.execute("""
CREATE index route_trenta_tris_id_idx on public.route_trenta_tris("id");
""")
conn_HAIG.commit()



### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.route_trenta_tris ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


### create index for 'idterm'
cur_HAIG.execute("""
CREATE index route_trenta_tris_idterm_idx on public.route_trenta_tris(idterm);
""")
conn_HAIG.commit()


### create index for 'idtrajectory'
cur_HAIG.execute("""
CREATE index route_trenta_tris_idtrajectory_idx on public.route_trenta_tris(idtrajectory);
""")
conn_HAIG.commit()


### create index for 'tripdistance_m'
cur_HAIG.execute("""
CREATE index route_trenta_tris_tripdistance_idx on public.route_trenta_tris(tripdistance_m);
""")
conn_HAIG.commit()


### create index for 'timedate_o'
cur_HAIG.execute("""
CREATE index route_trenta_tris_timedate_idx on public.route_trenta_tris(timedate_o);
""")
conn_HAIG.commit()


### create index for 'breaktime_s'
cur_HAIG.execute("""
CREATE index route_trenta_tris_breaktime_idx on public.route_trenta_tris(breaktime_s);
""")
conn_HAIG.commit()


### create index for 'triptime_s'
cur_HAIG.execute("""
CREATE index route_trenta_tris_triptime_s_idx on public.route_trenta_tris(triptime_s);
""")
conn_HAIG.commit()



### create index for 'deviation_pos_m'
cur_HAIG.execute("""
CREATE index route_trenta_tris_deviation_pos_idx on public.route_trenta_tris(deviation_pos_m);
""")
conn_HAIG.commit()

### create index for 'border_flag'
cur_HAIG.execute("""
CREATE index route_trenta_tris_border_flag_idx on public.route_trenta_tris(border_flag);
""")
conn_HAIG.commit()




######################################################################################
######################## table route_cinque ##########################################




# long time run...
## create a consecutive ID for each row
cur_HAIG.execute("""
alter table "route_cinque" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


## create an ndex on the "id" field
cur_HAIG.execute("""
CREATE index route_cinque_id_idx on public.route_cinque("id");
""")
conn_HAIG.commit()



### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.route_cinque ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


### create index for 'idterm'
cur_HAIG.execute("""
CREATE index route_cinque_idterm_idx on public.route_cinque(idterm);
""")
conn_HAIG.commit()


### create index for 'idtrajectory'
cur_HAIG.execute("""
CREATE index route_cinque_idtrajectory_idx on public.route_cinque(idtrajectory);
""")
conn_HAIG.commit()


### create index for 'tripdistance_m'
cur_HAIG.execute("""
CREATE index route_cinque_tripdistance_idx on public.route_cinque(tripdistance_m);
""")
conn_HAIG.commit()


### create index for 'timedate_o'
cur_HAIG.execute("""
CREATE index route_cinque_timedate_idx on public.route_cinque(timedate_o);
""")
conn_HAIG.commit()


### create index for 'breaktime_s'
cur_HAIG.execute("""
CREATE index route_cinque_breaktime_idx on public.route_cinque(breaktime_s);
""")
conn_HAIG.commit()


### create index for 'triptime_s'
cur_HAIG.execute("""
CREATE index route_cinque_triptime_s_idx on public.route_cinque(triptime_s);
""")
conn_HAIG.commit()



### create index for 'deviation_pos_m'
cur_HAIG.execute("""
CREATE index route_cinque_deviation_pos_idx on public.route_cinque(deviation_pos_m);
""")
conn_HAIG.commit()

### create index for 'border_flag'
cur_HAIG.execute("""
CREATE index route_cinque_border_flag_idx on public.route_cinque(border_flag);
""")
conn_HAIG.commit()



######################################################################################
######################################################################################

####### NEW TABLE "route" #############################################
#### -->>>>> ##########################################################


# long time run...
## create a consecutive ID for each row
cur_HAIG.execute("""
alter table "route_new" add id serial PRIMARY KEY
     """)
conn_HAIG.commit()


## create an ndex on the "id" field
cur_HAIG.execute("""
CREATE index route_new_id_idx on public.route_new("id");
""")
conn_HAIG.commit()



### change type of "idterm" from text to bigint
cur_HAIG.execute("""
ALTER TABLE public.route_new ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


### create index for 'idterm'
cur_HAIG.execute("""
CREATE index route_new_idterm_idx on public.route_new(idterm);
""")
conn_HAIG.commit()


### create index for 'idtrajectory'
cur_HAIG.execute("""
CREATE index route_new_idtrajectory_idx on public.route_new(idtrajectory);
""")
conn_HAIG.commit()


### create index for 'tripdistance_m'
cur_HAIG.execute("""
CREATE index route_new_tripdistance_idx on public.route_new(tripdistance_m);
""")
conn_HAIG.commit()


### create index for 'timedate_o'
cur_HAIG.execute("""
CREATE index route_new_timedate_idx on public.route_new(timedate_o);
""")
conn_HAIG.commit()


### create index for 'breaktime_s'
cur_HAIG.execute("""
CREATE index route_new_breaktime_idx on public.route_new(breaktime_s);
""")
conn_HAIG.commit()


### create index for 'triptime_s'
cur_HAIG.execute("""
CREATE index route_new_triptime_s_idx on public.route_new(triptime_s);
""")
conn_HAIG.commit()



### create index for 'deviation_pos_m'
cur_HAIG.execute("""
CREATE index route_new_deviation_pos_idx on public.route_new(deviation_pos_m);
""")
conn_HAIG.commit()

### create index for 'border_flag'
cur_HAIG.execute("""
CREATE index route_new_border_flag_idx on public.route_new(border_flag);
""")
conn_HAIG.commit()


## ------>>>>> #######################################################################
######################################################################################
######################################################################################



##### convert "geometry" field on LINESTRING

# Create an SQL connection engine to the output DB
engine = sal.create_engine('postgresql://postgres:superuser@10.1.0.1:5432/HAIG_ROMA')

## Convert the `'geom'` column back to Geometry datatype, from text
with engine.connect() as conn, conn.begin():
    print(conn)
    sql = """ALTER TABLE public."route"
                                  ALTER COLUMN geom TYPE Geometry(LINESTRING, 4326)
                                    USING ST_SetSRID(geom::Geometry, 4326)"""
    conn.execute(sql)





####################################################################################
####################################################################################
##### create table mapmatching #####################################################

## multiprocess.....
os.chdir('D:/ENEA_CAS_WORK/ROMA_2019')
os.getcwd()

# Create an SQL connection engine to the output DB
engine = sal.create_engine('postgresql://postgres:superuser@10.0.0.1:5432/HAIG_Viasat_RM_2019')


#### setup multiprocessing.......
## make indices

cur_HAIG.execute("""
ALTER TABLE public.mapmatching ALTER COLUMN "idterm" TYPE bigint USING "idterm"::bigint
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index mapmatching_idterm_idx on public.mapmatching("idterm");
""")
conn_HAIG.commit()


## create index on the column (u,v) togethers in the table 'mapmatching_2017' ###
cur_HAIG.execute("""
CREATE INDEX UV_idx_match ON public.mapmatching(u,v);
""")
conn_HAIG.commit()


## create index on the "TRIP_ID" column
cur_HAIG.execute("""
CREATE index match_trip_id_idx on public.mapmatching("TRIP_ID");
""")
conn_HAIG.commit()


## create index on the "idtrace" column
cur_HAIG.execute("""
CREATE index match_idtrace_idx on public.mapmatching("idtrace");
""")
conn_HAIG.commit()


cur_HAIG.execute("""
CREATE index match_timedate_idx on public.mapmatching(timedate);
""")
conn_HAIG.commit()



#######################################################################################
#######################################################################################

##### "OSM_edges": convert "geometry" field as LINESTRING

with engine.connect() as conn, conn.begin():
    print(conn)
    sql = """ALTER TABLE public."OSM_edges"
                                  ALTER COLUMN geom TYPE Geometry(LINESTRING, 4326)
                                    USING ST_SetSRID(geom::Geometry, 4326)"""
    conn.execute(sql)


##### "OSM_nodes": convert "geometry" field as POINTS

with engine.connect() as conn, conn.begin():
    print(conn)
    sql = """ALTER TABLE public."OSM_nodes"
                                  ALTER COLUMN geom TYPE Geometry(POINT, 4326)
                                    USING ST_SetSRID(geom::Geometry, 4326)"""
    conn.execute(sql)



