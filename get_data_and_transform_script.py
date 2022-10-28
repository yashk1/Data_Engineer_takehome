#importing libraries
import jsonlines
import pandas as pd
from pandas import json_normalize
import inflection

#reading data 
with jsonlines.open('./ga_sessions.json', 'r') as jsonl_f:
     lst = [obj for obj in jsonl_f]


flattened_data_l1 = pd.json_normalize(lst, max_level = 1)
flattened_data_l1.head()

#########################Visits#########################
visits_cols = ['fullVisitorId', 'visitId', 'visitNumber', 'visitStartTime', 'device.browser', 'geoNetwork.country']
visits = flattened_data_l1.loc[:,visits_cols]

#changing visitiNumber to numeric
visits["visitNumber"] = pd.to_numeric(visits["visitNumber"])
visits["visitStartTime"] = pd.to_numeric(visits["visitStartTime"])

#changing visitstarttime to iso8601 timestamp (milliseconds) and then to string
visits['visitStartTime'] = visits['visitStartTime'] * 1000
visits['visitStartTime'] = pd.to_datetime(visits['visitStartTime'],unit='ms')
visits['visitStartTime'] = visits['visitStartTime'].astype(str)

#renaming columns in visits
visits.rename(columns= ({'device.browser': 'browser', 'geoNetwork.country': 'country'}), inplace = True)

#changing from camelCase to snake_case using inflection package
visits.rename(columns= (lambda x: inflection.underscore(x)), inplace = True)

#creating visits.json
visits.to_json('visits.json', orient='records', lines=True)


#########################Hits#########################

hits_cols = ['fullVisitorId', 'visitId', 'hits']

#Flattening data from lst -> stores json data
hits = pd.json_normalize(lst, record_path = ['hits'], meta = ['visitId', 'fullVisitorId','visitStartTime'])
hits = hits[['visitId','fullVisitorId','visitStartTime','hitNumber','type','time','page.pagePath','page.pageTitle','page.hostname']]

#changing hitnumber to numeric
hits["hitNumber"] = pd.to_numeric(hits['hitNumber'])

#changing visitStartTime to iso8601 timestamp
hits['visitStartTime'] = pd.to_numeric(hits['visitStartTime']) 
hits['visitStartTime'] = hits['visitStartTime'] * 1000

#converting time to numeric
hits['time'] = pd.to_numeric(hits['time']) 

#creating hit_timestamp
hits['hit_timestamp'] = hits['visitStartTime'] + hits['time']
hits['hit_timestamp'] = pd.to_datetime(hits['hit_timestamp'],unit='ms')
hits['hit_timestamp'] = hits['hit_timestamp'].astype(str)

#creating hit Id column -> hitId = visitId + fullVisitorId + hit_timestamp
hits["hit_id"] = hits['visitId'].astype(str) + '_' + hits['fullVisitorId'] + '_' + hits['hit_timestamp']

#dropping columns
hits.drop(columns = ['visitId','fullVisitorId','visitStartTime','time'], inplace = True)

hits.rename(columns= ({'page.pagePath': 'pagePath','page.pageTitle':'pageTitle', 'page.hostname': 'hostname','type': "hit_type"}), inplace = True)
hits.rename(columns= (lambda x: inflection.underscore(x)), inplace = True)

#creating hits.json
hits.to_json('hits.json', orient='records', lines=True)