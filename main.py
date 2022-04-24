from urllib.request import Request
from  rich import print
from pymongo import MongoClient
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ['*']

#CORS allows you to configure the web API's security
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# data = getdata.my_func()

with open("db.json", "r") as f:
        data = json.loads(f.read())
# print(data)

client = MongoClient()

#Creates a database
db = client['assessment']


"""This is a collection. A collection is the same as a tabe like SQL databases"""
mycol = db['Student Learning Objectives']


#Deletes all documetns in the collection
# mycol.delete_many({})

mycol.insert_one(data)
# print("The number of documents in mycol:", mycol.count_documents({}))

dict_db = mycol.find_one()


def get_dates_up_to_end_date(dates,end_date):

    end_index = 0

    for index, date in enumerate(dates):

        if(date == end_date):
            end_index = index

    result = dates[0:end_index+1] 

    return result



def get_all_target_values(slo,measure,target_type):

    target_values = []

    target_obj = dict_db[slo][measure][target_type]
  
    for date in target_obj:
       target_value = target_obj[date]["target"]

       target_values.append(target_value)

    return target_values


def get_all_percentage_met_values(slo,measure,target_type):
    percentage_met_values = []

    target_obj = dict_db[slo][measure][target_type]

    for date in target_obj:
    
       percentage_met_value = target_obj[date]["percentage"]
       numStudents = target_obj[date]["num_student"]
       numStudentsMet = target_obj[date]["num_student_met"]

        #-1 means a value wasn't entered
        #if there was no percentage met value
       if percentage_met_value == -1:
           
           #and num_student and num_student_met have values
           if numStudents != -1 and numStudentsMet != -1:
               #divide to get percentage met value
               percentage_met_value = round((numStudentsMet/numStudents)*100, 2)

            #else(if num_student and num_student_met == -1)
           else:

               #set percentage_met_value to 0
               percentage_met_value = 0
               
       percentage_met_values.append(percentage_met_value)

    return percentage_met_values


def get_most_recent_target_description(slo, measure, target_type):

    most_recent_target_description = ""

    target_obj = dict_db[slo][measure][target_type]

    dates = []

    for date in target_obj:
        dates.append(date)

    dates.sort(key=lambda date: int(date[0:2]))

    most_recent_target_date = dates[len(dates)-1]

    most_recent_target_description = dict_db[slo][measure][target_type][most_recent_target_date]["description"]


    return most_recent_target_description


def create_plot_title_multi_target(slo,measure, dict_db):

    slo_description = dict_db[slo]["description"]
    get_measure_description = dict_db[slo][measure]["description"]

    title = f"{slo}{measure} T1 & T2 \n {slo_description} & {get_measure_description}"

    return title


def has_current_date(slo:str, measure:str, target:str, date:str, dict_db):
    if date in dict_db[slo][measure][target]:
        return True
    return False


# ************************************************************************************************
#
# ************************************************************************************************


@app.post("/slo/all")
async def get_all_slo():
    all_slo = [slo for slo in dict_db]
    return all_slo

@app.get("/slo/description/{slo}")
async def get_slo_descritpion(slo):
    slo = slo.upper()
    slo_description = dict_db[slo]["description"]
    return slo_description

@app.post("/measure/{slo}")
async def get_measure(slo):
    slo = slo.upper()
    measures = [measure for measure in dict_db[slo]]
    return measures

@app.get("/measure/description/{slo}/{measure}")
async def get_measure_description(slo, measure):
    slo = slo.upper()
    measure = measure.upper()

    measure_description = dict_db[slo][measure]["description"]

    return measure_description

@app.get("/dates/{slo}/{measure}")
async def get_all_measure_dates(slo,measure):
    dates = set()
    slo = slo.upper()
    measure = measure.upper()
    targets = dict_db[slo][measure]
    print(targets)
    for target in targets:
        
        current_dates = dict_db[slo][measure][target]
        # print(current_dates)
        for date in current_dates:
            if(len(date) == 5):
                dates.add(date)

    dates = list(dates)
    # print(dates)
    dates.sort(key=lambda date: int(date[0:2]))
    

    return dates

#choose remainder of dates 
#includes start date
@app.get("/startdate/{slo}/{measure}")
async def get_all_measure_dates_after_start(slo:str, measure:str, start: str ):

    dates = await get_all_measure_dates(slo, measure)
    start_index = 0
    results = []

    for index, d in enumerate(dates):

        if d == start:
            start_index = index

    
    results = dates[start_index:len(dates)]

    return results 
    
#gets all targets
@app.get("/targets/{slo}/{measure}")
async def get_all_targets(slo:str,measure:str):
    targets = []
    slo = slo.upper()
    measure = measure.upper()
    targets_objs = dict_db[slo][measure]

    for target in targets_objs:
        targets.append(target)

    return targets

@app.get("/result/{slo}/{measure}/{target}")
def get_target_description(slo:str,measure:str,target:str,date:str):
    slo = slo.upper()
    measure = measure.upper()
    target = target.upper()
    
    result_summary = dict_db[slo][measure][target][date]["description"]
    return result_summary

@app.get("/plot")
async def get_plot_data(slo:str,measure:str,start_date:str,end_date:str):

    slo = slo.upper()
    measure = measure.upper()
    dates_from_start = await get_all_measure_dates_after_start(slo,measure,start_date)

    dates_from_start_to_end = get_dates_up_to_end_date(dates_from_start, end_date)

    #if there are missing dates/percentage/met we have to/fill in the data with fillers like 0, in the correct places.
    t1_values = get_all_target_values(slo, measure,"T1")
    t2_values = get_all_target_values(slo, measure, "T2")
    percentages_met_t1 = get_all_percentage_met_values(
        slo, measure, "T1")
    percentages_met_t2 = get_all_percentage_met_values(
        slo, measure, "T2")

    most_recent_t1_description = get_most_recent_target_description(
        slo, measure, "T1")

    most_recent_t2_description = get_most_recent_target_description(
        slo, measure, "T2")

    title = create_plot_title_multi_target(slo, measure)

    plot_data = {
        "title":title,
        "dates": dates_from_start_to_end,
        "T1": t1_values,
        "T2":t2_values,
        "percentagesMetT1":percentages_met_t1,
        "percentagesMetT2":percentages_met_t2,
        "mostRecentT1Des": most_recent_t1_description,
        "mostRecentT2Des": most_recent_t2_description
    }

    return plot_data

# Endpoint to return states the database is in for a 
# specific SLO, Measure, and Year into an array.
#
# State options include the following:
#   "Add T1"
#   "Edit T1"
#   "Add T2"
#   "Edit T2"
# So could be the following options
@app.get("/input/options/{slo}/{measure}/{date}")
async def get_state(slo:str, measure:str, date:str):
    states = []             # to hold all state options
    slo = slo.upper()
    measure = measure.upper()

    # Check Add T1, Check Edit T1
    if date in dict_db[slo][measure]["T1"]:
        states.append("Edit T1")
    else:
        states.append("Add T1")
    
    # Check Add T2, Check Edit T2
    if "T2" in dict_db[slo][measure]:
        if date in dict_db[slo][measure]["T2"]:
            states.append("Edit T2")
        else:
            states.append("Add T2")
    return states

#create endpoint to save data. Parameter should be an object
#Need an enpoint that adds new data for a specific date for both targets
@app.post("/input/{slo}/{measure}/{target}/{date}")
async def add_new_slo_data(slo:str, measure:str, target:str, date:str, information: Request):
    
    slo=slo.upper()
    measure = measure.upper()
    data = await information.json()

    #Return true or false
    if has_current_date(slo,measure,target,date,dict_db) == True:
        return{
            "status":"FAILED the data was not stored; data on this date already exists",
            "data": data
        }
    else:
        dict_db[slo][measure][target][date] = data
        return{
            "status": "SUCCESS the data was stored",
            "data": data
        }

#End point allows user to edit data
@app.put("/edit/{slo}/{measure}/{target}/{date}")
async def edit_slo_data(slo:str, measure:str, target:str, date:str, information: Request):
    
    slo=slo.upper()
    measure = measure.upper()
    data = await information.json()

    if has_current_date(slo,measure,target,date,dict_db) == False:
        return{
            "status":"FAILED the entry for this date does not exist",
            "data": data
        }
    else:
        dict_db[slo][measure][target][date] = data
        return{
            "status": "SUCCESS the data was edited",
            "data": data
        }
