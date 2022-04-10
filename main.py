from operator import rshift
import pymongo
from  rich import print
from pymongo import MongoClient
import datetime
#imported to get data from db.json file
import getdata
import json
import fastapi


data = getdata.my_func()

# with open("mainpyDB.json", "r") as f:
#         data = json.loads(f.read())
# print(data)

client = MongoClient()

#Creates a database
db = client['assessment']


"""This is a collection. A collection is the same as a tabe like SQL databases"""
mycol = db['Student Learning Objectives']



# db.learning_objectives.drop() -> Deletes a collection

# result = collection.insert_many(post).inserted_id -> Returns the ids for all documents inteh collection

#inserts one item into the collection and will continue to insert as many times as this command runs
#hence why it is commented v

#Deletes all documetns in the collection
mycol.delete_many({})
mycol.insert_one(data)
print("The number of coments in mycol:", mycol.count_documents({}))

dict_db = mycol.find_one()

#Returns a list of collections
# print(db.list_collection_names())

#find/findOne works just like SELECT in MySQL db
# result = list(collection.find()) -> returns the first occurence/ document in the selection 

#result = list(collections.find_one()) -> gives same result as SELECT* in MySQL
#find() returns all the documents in the collection 
# print(result)

#This says don't print the id but print S4
# result = list(collections.find({}, {"_id":0}))


"""prints a list of all dbs that were created on the system"""
# print(client.list_database_names())

"""Returns a list of all the names of the dbs in the system"""
# dblist = client.list_database_names()
"""Searches the list for a specific db name """
# if "assessment" in dblist:
#     print("It exists")


def get_dates():
        pass
# def get_dates_up_to_end_date(dates,end_date):

#     end_index = 0

#     for index, date in enumerate(dates):

#         if(date == end_date):
#             end_index = index

#     result = dates[0:end_index+1] 

#     return result



def get_all_target_values(slo,measure,target_type):


    target_values = []

    target_obj = dict_db[slo][measure][target_type]
  
    for date in target_obj:
       target_value = target_obj[date]["target"]

       target_values.append(target_value)

    return target_values

print(get_all_target_values("S1","M1","T1"))


def get_all_percentage_met_values(slo,measure,target_type):
    percentage_met_values = []

    target_obj = dict_db[slo][measure][target_type]

    for date in target_obj:

       percentage_met_value = target_obj[date]["percentage"]

       percentage_met_values.append(percentage_met_value)

    return percentage_met_values

print(get_all_percentage_met_values("S1","M1","T1"))

# def get_most_recent_target_description(slo, measure, target_type):

#     most_recent_target_description = ""

#     target_obj = dict_db[slo][measure][target_type]

#     dates = []

#     for date in target_obj:
#         dates.append(date)

#     dates.sort(key=lambda date: int(date[0:2]))

#     most_recent_target_date = dates[len(dates)-1]

#     most_recent_target_description = dict_db[slo][measure][target_type][most_recent_target_date]["description"]


#     return most_recent_target_description


# def create_plot_title_multi_target(slo,measure):

#     slo_description = dict_db[slo]["description"]
#     get_measure_description = dict_db[slo][measure]["description"]

#     title = f"{slo}{measure} T1 & T2 \n {slo_description} & {get_measure_description}"

#     return title

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.post("/slo/all")
# async def get_all_slo():
#     all_slo = [slo for slo in dict_db]
#     return all_slo


# @app.get("/slo/description/{slo}")
# async def get_slo_descritpion(slo):
#     slo = slo.upper()
#     slo_description = dict_db[slo]["description"]
#     return slo_description



# @app.post("/measure/{slo}")
# async def get_measure(slo):
#     slo = slo.upper()
#     measures = [measure for measure in dict_db[slo]]
#     return measures


# @app.get("/measure/description/{slo}/{measure}")
# async def get_measure_description(slo, measure):
#     slo = slo.upper()
#     measure = measure.upper()

#     measure_description = dict_db[slo][measure]["description"]

#     return measure_description



# @app.get("/dates/{slo}/{measure}")
# async def get_all_measure_dates(slo,measure):
#     dates = set()
#     slo = slo.upper()
#     measure = measure.upper()
#     targets = dict_db[slo][measure]
#     print(targets)
#     for target in targets:
        
#         current_dates = dict_db[slo][measure][target]
#         # print(current_dates)
#         for date in current_dates:
#             if(len(date) == 5):
#                 dates.add(date)

#     dates = list(dates)
#     # print(dates)
#     dates.sort(key=lambda date: int(date[0:2]))
    

#     return dates


# #choose remainder of dates 
# @app.get("/startdate/{slo}/{measure}")
# async def get_all_measure_dates_after_start(slo:str, measure:str, start: str ):

#     dates = await get_all_measure_dates(slo, measure)
#     start_index = 0
#     results = []

#     for index, d in enumerate(dates):

#         if d == start:
#             start_index = index

    
#     results = dates[start_index:len(dates)]

#     return results 
    

# @app.get("/targets/{slo}/{measure}")
# async def get_all_targets(slo:str,measure:str):
#     targets = []
#     slo = slo.upper()
#     measure = measure.upper()
#     targets_objs = dict_db[slo][measure]

#     for target in targets_objs:
#         targets.append(target)

    

#     return targets


# @app.get("/result/{slo}/{measure}/{target}")
# def get_result_summary(slo:str,measure:str,target:str,date:str):
#     slo = slo.upper()
#     measure = measure.upper()
#     target = target.upper()
    
#     result_summary = dict_db[slo][measure][target][date]["description"]
#     return result_summary






# @app.get("/plot")
# async def get_plot_data(slo:str,measure:str,start_date:str,end_date:str):

#     slo = slo.upper()
#     measure = measure.upper()
#     dates_from_start = await get_all_measure_dates_after_start(slo,measure,start_date)

#     dates_from_start_to_end = get_dates_up_to_end_date(dates_from_start, end_date)

#     #if there are missing dates/percentage/met we have to/fill in the data with fillers like 0, in the correct places.
#     t1_values = get_all_target_values(slo, measure,"T1")
#     t2_values = get_all_target_values(slo, measure, "T2")
#     percentages_met_t1 = get_all_percentage_met_values(
#         slo, measure, "T1")
#     percentages_met_t2 = get_all_percentage_met_values(
#         slo, measure, "T2")

#     most_recent_t1_description = get_most_recent_target_description(
#         slo, measure, "T1")

#     most_recent_t2_description = get_most_recent_target_description(
#         slo, measure, "T2")

#     title = create_plot_title_multi_target(slo, measure)

#     plot_data = {
#         "title":title,
#         "dates": dates_from_start_to_end,
#         "T1": t1_values,
#         "T2":t2_values,
#         "percentagesMetT1":percentages_met_t1,
#         "percentagesMetT2":percentages_met_t2,
#         "mostRecentT1Des": most_recent_t1_description,
#         "mostRecentT2Des": most_recent_t2_description
#     }

#     return plot_data