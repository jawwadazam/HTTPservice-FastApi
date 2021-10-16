import requests
import json
import time
import random
import aiohttp
import asyncio


BASE = "http://127.0.0.1:8000/"

customerIDs = [1,2,3,6,'a','b']
tagIDs= [1,2,3,4,'a','b0']
userIDs= [1,2,3, "A6-Indexer", 'Google', 'aaaaa-bbbb-ssss-xxxx' ]
remoteIPs = ["123.123.0.0", "0.0.0.0", 12, "127.0.0.1"]
timestamps= [15000, 4000]


start_time = time.time()

"""
        Code for async requests using Asyncio, 
        ref: https://www.youtube.com/watch?v=ln99aRAcRt0
"""
async def main():
        async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(10000):
                        task = asyncio.ensure_future(send_request(session))
                        tasks.append(task)
                
                responses = await asyncio.gather(*tasks)
        print(responses)
                        

async def send_request(session):
        data = {"customerID": random.choice(customerIDs),
                        "tagID": random.choice(tagIDs),
                        "userID": random.choice(userIDs),
                        "remoteIP":random.choice(remoteIPs),
                        "timestamp":random.choice(timestamps)}
        async with session.post(BASE + 'api/', json=data) as response:
                return await response.json()


asyncio.run(main())
print('Total RunTime : ' , time.time()-start_time, 'Secs')

