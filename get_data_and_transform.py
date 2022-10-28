import jsonlines
import pandas as pd
from pandas import json_normalize
import inflection


with jsonlines.open('ga_sessions_20160801_(2)_(1)_(1)_(1) copy.json', 'r') as jsonl_f:
     lst = [obj for obj in jsonl_f]


flattened_data_l1 = pd.json_normalize(lst, max_level = 1)
flattened_data_l1.head()

#########################Visits#########################
visits_cols = ['fullVisitorId', 'visitId', 'visitNumber', 'visitStartTime', 'device.browser', 'geoNetwork.country']
visits = flattened_data_l1.loc[:,visits_cols]

#changing visitiNumber to numeric
visits["visitNumber"] = pd.to_numeric(visits["visitNumber"])

#renaming columns in visits
visits.rename(columns= ({'device.browser': 'browser', 'geoNetwork.country': 'country'}), inplace = True)

#changing from camelCase to snake_case using inflection package
visits.rename(columns= (lambda x: inflection.underscore(x)), inplace = True)

#creating visits.json
visits.to_json('visits.json', orient='records', lines=True)

#########################Hits#########################

hits_cols = ['fullVisitorId', 'visitId', 'hits']
hits = pd.json_normalize(lst, record_path = ['hits'], meta = ['visitId', 'fullVisitorId','visitStartTime'])
hits = hits[['visitId','fullVisitorId','visitStartTime','hitNumber','type','time','page.pagePath','page.pageTitle','page.hostname']]

hits.insert(0, 'hit_id', range(1, 1 + len(hits)))


#changing hitnumber to numeric
hits["hitNumber"] = pd.to_numeric(hits['hitNumber'])
hits['visitStartTime'] = pd.to_numeric(hits['visitStartTime']) 
hits['time'] = pd.to_numeric(hits['time']) 

hits.rename(columns= ({'page.pagePath': 'pagePath','page.pageTitle':'pageTitle', 'page.hostname': 'hostname','type': "hit_type"}), inplace = True)
hits.rename(columns= (lambda x: inflection.underscore(x)), inplace = True)

hits['visit_start_time'] = pd.to_numeric(hits['visit_start_time']) 
hits['time'] = pd.to_numeric(hits['time']) 


#creating hit_timestamp
hits['hit_timestamp'] = hits['visit_start_time'] *1000 + hits['time']
hits.drop(columns = ['visit_start_time','time'], inplace = True)

hits.to_json('hits.json', orient='records', lines=True)
