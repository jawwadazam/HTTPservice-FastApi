from fastapi import FastAPI, Request, Depends, Query
from typing import Optional
import services
import models
import sqlalchemy.orm as orm
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
from datetime import datetime, timedelta

database_uri = models.SQLALCHEMY_DATABASE_URI + '?check_same_thread=False'
sessionmaker = FastAPISessionMaker(database_uri)

app = FastAPI()



@app.on_event("startup")
@repeat_every(seconds=60*60, raise_exceptions=True) 
def calculate_stats():
    """
        Cron job script that will execute every 60 minutes from starttime
    """
    with sessionmaker.context_session() as db:
        print("CRON WORKING" , datetime.now())
        services.create_stats(db)

        
    return "success"

@app.post("/api/")
async def process_request(request: Request, db:orm.Session = Depends(services.get_db)):
    try:
        body = await request.json()
        isvalid, code = services.if_request_is_valid(body, db)
    except Exception as e:
        body = str(await request.body())
        isvalid = False
        code = 1
    info = services.get_invalid_code_description(code, db)
    id = services.create_log_entry(db=db, request_body=body, isvalid=isvalid, error_code=code)
    return {'isvalid':isvalid, 'status': info,'request': body}

@app.get("/api/stats/{customer_id}/{date}/")
async def get_customer_stats(customer_id:int, date:str, db:orm.Session = Depends(services.get_db)):  
    invalid_error = services.path_parmeters_validation(customer_id=customer_id, date=date)
    stats = dict()
    if invalid_error:
        stats['Error 400'] = {'Error 400' : invalid_error}
    else: 
        timestamp = "{}%".format(date)
        results = services.get_stats_by_datetime_by_customerID(db, customer_id, timestamp)
        stats = {'customer_id': customer_id,
                        'total_requests': 0,
                        'valid_requests': 0,
                        'invalid_requests': 0,
                        'date': date,
                        }
        if results:
            for result in results:
                stats['total_requests'] += result.total_requests_count
                stats['valid_requests'] += result.valid_requests_count
                stats['invalid_requests'] += result.invalid_requests_count   
        else:
            stats = {'Error 404': "No records Found"}

    return(stats)

@app.get("/api/stats/{customer_id}/{date}/{hour}")
async def get_customer_stats_by_hour(customer_id:int, date:str, hour:int, db:orm.Session = Depends(services.get_db)):
    invalid_error = services.path_parmeters_validation(customer_id=customer_id, date=date, hour=hour)
    stats = dict()
    if invalid_error:
        stats['Error 400'] = {'Error 400' : invalid_error}
    else:  
        timestamp = "{} {:02d}%".format(date, hour)
        results = services.get_stats_by_datetime_by_customerID(db, customer_id, timestamp)
        stats = {'customer_id': customer_id,
                            'total_requests': 0,
                            'valid_requests': 0,
                            'invalid_requests': 0,
                            'date': date,
                            }
        if results:
            for result in results:
                stats['total_requests'] += result.total_requests_count
                stats['valid_requests'] += result.valid_requests_count
                stats['invalid_requests'] += result.invalid_requests_count
        else:
            stats = {'Error 404': "No records Found"}
    return(stats)

@app.get("/api/stats/{date}/")
async def get_stats(date:str, db:orm.Session = Depends(services.get_db)):
    invalid_error = services.path_parmeters_validation(date=date)
    stats = dict()
    if invalid_error:
        stats['Error 400'] = {'Error 400' : invalid_error}
    else: 
        timestamp = "{}%".format(date)
        results = services.get_stats_by_datetime(db, timestamp)
        if results:
            for result in results:
                
                if result.customer_id in stats.keys():  
                    stats[result.customer_id]['customer_id'] =  result.customer_id             
                    stats[result.customer_id]['total_requests'] += result.total_requests_count
                    stats[result.customer_id]['valid_requests'] += result.valid_requests_count
                    stats[result.customer_id]['invalid_requests'] += result.invalid_requests_count
                else:                
                    data = {'customer_id': result.customer_id,
                            'total_requests': result.total_requests_count,
                            'valid_requests': result.valid_requests_count,
                            'invalid_requests': result.invalid_requests_count,
                            'date': date,
                            }
                    stats[result.customer_id] = data
                    
        else:
            stats['Error'] = " Error 404 : No records Found"

    return(list(stats.values()))

@app.get("/api/stats/{date}/{hour}")
async def get_stats_by_hour(date:str, hour:int, db:orm.Session = Depends(services.get_db)):
    invalid_error = services.path_parmeters_validation(date=date, hour=hour)
    stats = dict()
    if invalid_error:
        stats['Error'] = {'Error 400' : invalid_error}
    else:  
        timestamp = "{} {:02d}%".format(date, hour)
        results = services.get_stats_by_datetime(db, timestamp)

        if results:
            for result in results:
                if result.customer_id in stats.keys(): 
                    print("CUSTOMER ID is there, " , result.customer_id,  stats.keys())
                    stats[result.customer_id]['customer_id'] =  result.customer_id                 
                    stats[result.customer_id]['total_requests'] += result.total_requests_count
                    stats[result.customer_id]['valid_requests'] += result.valid_requests_count
                    stats[result.customer_id]['invalid_requests'] += result.invalid_requests_count
                else:
                    print("CUSTOMER ID is not there, " , result.customer_id,  stats.keys())
                    data = {'customer_id': result.customer_id,
                            'total_requests': result.total_requests_count,
                            'valid_requests': result.valid_requests_count,
                            'invalid_requests': result.invalid_requests_count,
                            'datetime': timestamp,
                            }
                    stats[result.customer_id] = data
        else:
            stats['Error'] = " Error 404 : No records Found"

    return(list(stats.values()))

