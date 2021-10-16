from sqlalchemy.sql.sqltypes import Boolean
from typing import Optional
from sqlalchemy import func, log
import models as database
import sqlalchemy.orm as orm
import re
from datetime import datetime, timedelta
import json


def create_database():
    return database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_customers_by_id(db:orm.Session, id:int):
    return db.query(database.CustomerModel).filter(database.CustomerModel.id==id).first()

def get_blacklisted_ips_by_ip(db:orm.Session, ip:str):
    return db.query(database.IPBlacklistModel).filter(database.IPBlacklistModel.ip==ip).all()

def get_blacklisted_uas_by_ua(db:orm.Session, ua:str):
    return db.query(database.UserAgentBlacklistModel).filter(database.UserAgentBlacklistModel.user_agent==ua).all()

def get_invalid_codes(db:orm.Session, id:int):
    return db.query(database.InvalidCodesModel).filter(database.InvalidCodesModel.id==id).first()

def create_log_entry(db:orm.Session, request_body, isvalid:Boolean, error_code:int):
    request_id = create_request_entry(db,request_body)
    customer_id = get_customer_id(request_body)
    log_entry= database.LoggerModel(request_id= request_id, customer_id=customer_id, is_valid=isvalid, invalid_code_id=error_code, timestamp=datetime.now())
    db.add(log_entry)
    db.flush()
    db.refresh(log_entry)
    db.commit()
    return log_entry.id

def create_request_entry(db:orm.Session, request_body):
    request_entry = database.RequestsModel(request_body=str(request_body))
    db.add(request_entry)
    db.flush()
    db.refresh(request_entry)
    return request_entry.id
        
def create_stats(db:orm.Session):
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=3)
    cutomer_ids = db.query(database.LoggerModel.customer_id).filter(database.LoggerModel.timestamp > one_hour_ago).distinct().all()
    records_to_add = list()
    for customer_id in cutomer_ids:
        total_requests = db.query(database.LoggerModel.customer_id).filter(database.LoggerModel.timestamp > one_hour_ago, database.LoggerModel.customer_id==customer_id.customer_id).count()
        valid_requests = db.query(database.LoggerModel.customer_id).filter(database.LoggerModel.timestamp > one_hour_ago,
                                                                           database.LoggerModel.customer_id==customer_id.customer_id,
                                                                           database.LoggerModel.is_valid==True).count()
        records_to_add.append(database.HourlyStatsModel(customer_id=customer_id.customer_id,
                                                        total_requests_count= total_requests,
                                                        valid_requests_count= valid_requests,
                                                        invalid_requests_count= total_requests-valid_requests,
                                                        timestamp= now ))
    try:
        db.bulk_save_objects(records_to_add)
        db.commit()
    except Exception as e:
        print('Exception occured:', e )

def get_stats_by_datetime_by_customerID(db:orm.Session, customer_id:int, timestamp:str):
    print(customer_id, timestamp)
    return db.query(database.HourlyStatsModel).filter(database.HourlyStatsModel.customer_id==customer_id,
                                                     database.HourlyStatsModel.timestamp.like(timestamp)).all()

def get_stats_by_datetime(db:orm.Session, timestamp:str):
    return db.query(database.HourlyStatsModel).filter(database.HourlyStatsModel.timestamp.like(timestamp)).all()

def get_customer_id(request_body):
    if isinstance(request_body, str):
        substring = re.search("customerID=\d*", request_body)
        if substring:
            return int(substring[0].split('=')[1])
        else:
            return ''
    else:
        return request_body['customerID']
    
def get_invalid_code_description(code_id, db):
    """ 
        A Query to DB to get teh error code description stores in DB
    """
    result = get_invalid_codes(db=db, id=code_id)
    if result:
        result = result.__dict__
        return "Err({0}):{1}".format(code_id, result['info'])
    return "200: Success"

def if_request_is_valid(body, db):
    """
        Checks if the requests are valid
    """
    isvalid = True
    code = None
    if not is_complete(body):
        isvalid = False
        code = 2
    elif not is_valid_customer(body['customerID'], db):
        isvalid=False
        code = 3
    elif is_ip_blacklisted(body['remoteIP'], db):
        isvalid=False
        code = 4
    elif is_ua_blacklisted(body['userID'], db):
        isvalid=False
        code = 5
    return isvalid, code

def is_complete(body):
    """
        To check if the request is complete, i.e all information is available
    """
    headers = ['customerID', 'tagID', "userID","remoteIP","timestamp"]
    if len(body) == 5 and all(key in headers for key in body.keys()):
        return True
    return False

def is_valid_customer(customer_id, db):
    """
        checks if the customert is registered to our DB and is an active customer
    """
    result = get_customers_by_id(db=db, id=customer_id)
    if result:
        result = result.__dict__
        if not result['is_active']:
            return False
        return True
    return False

def is_ip_blacklisted(remote_ip, db):
    """
        checks if the IP is blacklisted
    """
    result = get_blacklisted_ips_by_ip(db=db, ip=remote_ip)
    if result:
        return True
    return False

def is_ua_blacklisted(user_id, db):
    """
        checks if the User Agent is blacklisted
    """
    result = get_blacklisted_uas_by_ua(db=db, ua=user_id)
    if result:
        return True
    return False

def path_parmeters_validation(customer_id:Optional[int] = None, date:Optional[str] = None, hour:Optional[int] = None):
    if customer_id and customer_id<0:
        return "Customer ID cannot be a negative number"

    if date :
        try:
            date_time_obj = datetime.fromisoformat(date)
            if date_time_obj > datetime.now() :
                return "Date entered is in future, Please enter a valid date in YYYY-MM-DD format"
        except:
            return "Please enter a valid date in YYYY-MM-DD format"

    if hour and 00<hour>23:
        return "Please enter a valid hour in 24hrs format. i.e a number between 00 - 23"

def process_request(body):
    """
        Code to process the request goes here
    """
    pass