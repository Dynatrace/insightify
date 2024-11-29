import io, csv
import time
import json
import traceback
from venv import logger
import requests # type: ignore
import datetime
from pathlib import Path
from dynatrace_extension import Extension  # type: ignore
from .constant import * 

class ExtensionImpl(Extension):

    class problem_mgmt_zone:
        def __init__(self):
          self.mgmt_zone = 0
          self.problems = 0
          self.rootCause = 0
          self.application=0
          self.service=0
          self.infrastructure=0
          self.error=0
          self.avalability=0
          self.performance=0
          self.resource=0
          self.custom=0
          self.mttr_rca=0
          self.mttr_wo_rca=0
          self.mttr_rca_list=[]
          self.mttr_wo_rca_list=[]

    #When to collect the first sample of problem data
    COLLECT_PROBLEM_DATA=1

    DASHBOARDS="dashboards"
    GET_EXISTING_DASHBOARD="dashboards?owner=dynatraceone"
    INGEST_METRICS = "metrics/ingest"
    GET_DATA_INSERTED_DATA_POINT="metrics/query?metricSelector=record_insertion_time:filter(and(or(eq(config_id,entityIDentityID))))&resolution=1d&from=now-1y"
    TEST_GET_DATA_INSERTED_DATA_POINT="metrics/query?metricSelector=record_insertion_time:filter(and(or(eq(config_id,entityID))))&resolution=1m&from=now-1d"

    #PROBLEMS API
    PROBLEMS="problems?pageSize=500&from=starttime&to=endtime"
    SPECIFIC_PROBLEMS="problems?pageSize=500&from=starttime&to=endtime&problemSelector=managementZones%28%22mgmt_zone_name%22%29"
    TEST_PROBLEMS="problems?pageSize=1&from=starttime&to=endtime"

    def initialize(self):
        self.extension_name = "insightify"
        self.logger.info("Initializing......")
        try:
                #Flag to indicate if earlier record push value has been pulled
                self.problem_time_retrieve_flag = 0

                #Other variables
                self.dashboard_created = 0
                self.pull_prb_data_iterations = 0
                self.problem_dashboard_created = 0
                self.get_last_inserted_data_set=None
                self.problems_mgmt_zone = {}
                self.problem_time_interval = self.COLLECT_PROBLEM_DATA
                
        except Exception as e:
                self.logger.exception("Exception while running initialize", str(e), exc_info=True)

        finally:
                self.logger.info("Successful execution initialize ")

    # *********************************************************************    
    #           Function to get metrics/SLO using API V2 endpoint
    # *********************************************************************    
    def dtApiV2GetQuery(self, apiendpoint, endpoint_detail):
      self.logger.info("In dtApiV2GetQuery")
      try:
        data = {}
        config_url=endpoint_detail["url"]
        password=endpoint_detail["token"]
        
        config_url = config_url.replace("/v1","/v2")
        query = str(config_url) + apiendpoint
        self.logger.info(f"Query: {query}")
        
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(password)}
        response = requests.get(query, headers = get_param, verify=False)

        response.raise_for_status()
        
        if 200 <= response.status_code < 300:
            data = response.json()
            self.logger.info("RAW_DATA:", data)
        else:
            self.logger.info(f"[dtApiV2GetQuery] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
          self.logger.info(f"[dtApiV2GetQuery] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
          self.logger.info(f"[dtApiV2GetQuery] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
          self.logger.info(f"[dtApiV2GetQuery] JSON decode error: {json_err}")
      except Exception as e:
          self.logger.info(f"Unexpected error in dtApiV2GetQuery: {str(e)}")
          self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
    
      finally:
        self.logger.info("Successfully completed dtApiV2GetQuery")  
        return data

    # *********************************************************************
    #           Function to get metrics using API V2 endpoint
    # *********************************************************************
    def dtApiV2GetMetricDataPoint(self, endpoint, endpoint_config):
      try:
        self.logger.info(f"In dtApiV2GetMetricDataPoint endpoint: {endpoint}")
        data = {}

        config_url = endpoint_config["confurl"]
        conf_password = endpoint_config["conftoken"]
         
        query = str(config_url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(conf_password)}
        response = requests.get(query, headers = get_param, verify=False)
        self.logger.info(f"[dtApiV2GetMetricDataPoint] Query: {query} returned response {response}")

        response.raise_for_status()        
        if 200 <= response.status_code < 300:
            self.logger.info(f"Returned data: {response.json()}")
            data = response.json()
            return data
        else:
            self.logger.info(f"[dtApiV2GetMetricDataPoint] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
        self.logger.info(f"[dtApiV2GetMetricDataPoint] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
        self.logger.info(f"[dtApiV2GetMetricDataPoint] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
        self.logger.info(f"[dtApiV2GetMetricDataPoint] JSON decode error: {json_err}")
      except Exception as e:
        self.logger.info(f"Unexpected error in dtApiV2GetMetricDataPoint: {str(e)}")
        self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
    
      finally:
        self.logger.info("Succesfully completion dtApiV2GetMetricDataPoint")

    # *******************************************************************************    
    #            Function to push metrics using Ingest Metrics endpoint
    #      This is pushed to ingest host,dem and ddu units per management zone 
    # *******************************************************************************    
    def dtApiIngestMetrics(self, endpoint, payload, endpoint_config):
      try:
        self.logger.info("In dtApiIngestMetrics ")
        data = {}

        config_url = endpoint_config["confurl"] 
        conf_password = endpoint_config["conftoken"] 
        config_url = config_url.replace("/v1","/v2")

        query = str(config_url) + endpoint
        post_param = {'Content-Type':'text/plain;charset=utf-8', 'Authorization':'Api-Token {}'.format(conf_password)}
        
        response = requests.post(query, headers = post_param, data = payload, verify=False)
        response.raise_for_status()
        
        self.logger.info(f"Query: {query} \n Payload:{payload} \n Response:{response} \n Response: {response.content}")
        
        if 200 <= response.status_code < 300:
            data = response.json()
        else:
            self.logger.info(f"[dtApiIngestMetrics] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
        self.logger.info(f"[dtApiIngestMetrics] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
        self.logger.info(f"[dtApiIngestMetrics] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
        self.logger.info(f"[dtApiIngestMetrics] JSON decode error: {json_err}")
      except Exception as e:
        self.logger.info(f"Unexpected error in dtApiIngestMetrics: {str(e)}")
        self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
    
      finally:
        self.logger.info("Succesfully completion dtApiIngestMetrics")
        return data

    # *******************************************************************************    
    #           Function to post data using API v1 endpoint
    # *******************************************************************************    
    def dtApiV1PostQuery(self, endpoint, payload, endpoint_config):
      try:
        self.logger.info("In dtApiV1PostQuery")  
        data = {}

        config_url = endpoint_config["confurl"]
        conf_password = endpoint_config["conftoken"] 
        config_url = config_url.replace("/v2","/config/v1")
        
        query = str(config_url) + endpoint
        post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(conf_password)}
        response = requests.post(query, headers=post_param, data=json.dumps(payload), verify=False)
        self.logger.info(response)

        response.raise_for_status()
        
        if 200 <= response.status_code < 300:
            data = response.json()
        else:
            self.logger.error(f"[dtApiV1PostQuery] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
        self.logger.info(f"[dtApiV1PostQuery] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
        self.logger.info(f"[dtApiV1PostQuery] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
        self.logger.info(f"[dtApiV1PostQuery] JSON decode error: {json_err}")
      except Exception as e:
        self.logger.info(f"Unexpected error in dtApiV1PostQuery: {str(e)}")
        self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
    
      finally:
        self.logger.info("Succesfully completed dtApiV1PostQuery")

    # *******************************************************************************    
    #           Function query it executes every minute 
    # *******************************************************************************    
    def query(self):
        """
        The query method is automatically scheduled to run every minute
        """
        self.logger.info("query method started for insightify.")
        for endpoint in self.activation_config["endpoints"]:
           #try:
                url = endpoint["url"]
                get_problem_data_mgmt_zone = endpoint["get_problem_data_mgmt_zone"]
                prb_management_zone_list = endpoint["management_zone_name"]
                prb_report_date = endpoint["get_generate_report"]
                activegate_endpoint = endpoint["ag_endpoint"]

                config_id = self.monitoring_config_id
                config_name=self.monitoring_config_name
                
                #Dashboard logic
                if self.dashboard_created == -1:
                    dashboard_file = Path(__file__).parent / "dashboard.json"
                    fp = open(dashboard_file,'r')
                    dashboard_json = json.loads(fp.read())

                    payload = json.dumps(dashboard_json).replace('$1',config_id) 
                    dashboard_json = json.loads(payload)
                    dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                    dashboards = self.dtConfApiv1(self.GET_EXISTING_DASHBOARD, endpoint)

                    self.logger.info("Found dashboards: " + str(len(dashboards)))
                    #Check if the dashboard is already present
                    if len(dashboards) > 0:
                      dashboardList = dashboards["dashboards"]
                  
                      for dashboard in dashboardList:
                        if dashboard["name"].__eq__(dashboard_name):
                            self.logger.info("Found a dashboard already by that configuration. Skipping.. " + dashboard["name"])
                            self.dashboard_created = 1
                            continue

                    #Verifying that the dashboard is not already created
                    if (self.dashboard_created == 0):
                      self.logger.info("Will create a dashboard " + dashboard_name)
                      self.dtApiV1PostQuery(self.DASHBOARDS, dashboard_json, endpoint)
                      self.dashboard_created = 1
                   
                if (self.problem_dashboard_created == 0):
                    dashboard_file = Path(__file__).parent / "constant/operation_dashboard.json"
                    fp = open(dashboard_file,'r')
                    dashboard_json = json.loads(fp.read())
                    
                    payload = json.dumps(dashboard_json).replace('$1',config_id).replace('$Name', config_name) 
                    dashboard_json = json.loads(payload)
                    dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                    dashboards = self.dtConfApiv1(self.GET_EXISTING_DASHBOARD, endpoint)
                
                    self.logger.info("(problem_dashboard_check) Dashboard founds: " + str(len(dashboards))) 
                    #Check if the dashboard is already present
                    if len(dashboards) > 0:
                        dashboardList = dashboards["dashboards"]
                    
                        for dashboard in dashboardList:
                            self.logger.info("Creating dashboard: " + dashboard["name"]) 
                            if dashboard["name"].__eq__(dashboard_name):
                                self.logger.info("Found a dashboard already by that configuration. Skipping.. " + dashboard["name"])
                                self.problem_dashboard_created = 1
                                continue 
                
                    #Verifying that the dashboard is not already created
                    if (self.problem_dashboard_created == 0):
                        self.logger.info("Will create a dashboard " + dashboard_name)
                        self.dtApiV1PostQuery(self.DASHBOARDS, dashboard_json, endpoint)

                    #Create benefit value realisation dashboard 
                    dashboard_file = Path(__file__).parent / "constant/benefit_realisation_report.json"
                    fp = open(dashboard_file,'r')
                    dashboard_json = json.loads(fp.read())

                    dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                    self.logger.info("Will also create " + dashboard_name)

                    payload = json.dumps(dashboard_json).replace('$1',config_id).replace('$Name', config_name)
                    dashboard_json = json.loads(payload)
                    self.dtApiV1PostQuery(self.DASHBOARDS, dashboard_json, endpoint)

                    #Create problem trend analysis
                    dashboard_file = Path(__file__).parent / "constant/problem_trend_and_analysis.json"
                    fp = open(dashboard_file,'r')
                    dashboard_json = json.loads(fp.read())

                    dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                    payload = json.dumps(dashboard_json).replace('$1',config_id).replace('$Name', config_name)
                    dashboard_json = json.loads(payload)
                    self.dtApiV1PostQuery(self.DASHBOARDS, dashboard_json, endpoint)

                    self.problem_dashboard_created = 1


                #Local copy of the variable to identify when to pull problem data

                self.logger.info(f"Running endpoint with url '{url}'")
                #self.logger.info("config id = " + self.monitoring_config_id)

                # Your extension code goes here, e.g.
                
                entityID = self.monitoring_config_id
                self.logger.info("entityID: " + entityID)

                #Verify if there are any records inserted for the problem data before
                try:
                  #expected_insertion=datetime.datetime.fromtimestamp(expected_next_data_insertion)
                  self.logger.info(f"problem_time_retrieve_flag: {self.problem_time_retrieve_flag} problem_time_interval {self.problem_time_interval}")
                    
                  #Verify if there are any records inserted for the problem data before
                  if self.problem_time_retrieve_flag == 0: 
                    #Get the last inserted record timestamp
                    query = self.TEST_GET_DATA_INSERTED_DATA_POINT.replace("entityID",entityID)
                    self.get_last_inserted_data_set = self.dtApiV2GetMetricDataPoint( query, endpoint)
                    logger.info(f"last inserted record retrieved from db: {self.get_last_inserted_data_set}")
 
                    if self.get_last_inserted_data_set:
                      try:
                         logger.info("Will identify the last inserted record timestamp")

                         for result_obj in self.get_last_inserted_data_set['result']:
                             logger.info(result_obj)
                             for data_obj in result_obj['data']:
                                 logger.info(data_obj['dimensions'][0])
                                 if data_obj['dimensions'][0] == entityID:
                                   logger.info("Found the config id:" +  data_obj['dimensions'][0])

                                   for j in range(len(data_obj['values'])):
                                     if data_obj['values'][j]:
                                       logger.info(data_obj['values'][j])
                                       last_inserted_record_time = data_obj['values'][j]
                                       logger.info("last inserted record time: " + str(last_inserted_record_time))
          
                                       #Setup the next expected insertion time (using the last record timestamp)
                                       now = time.time()
                                       if endpoint['get_generate_report'] == "Last 1 day":
                                           expected_next_data_insertion = last_inserted_record_time +  (1*86400)
                                       elif endpoint['get_generate_report'] == "Last 7 days":
                                           expected_next_data_insertion = last_inserted_record_time+(7*86400)
                                       elif endpoint['get_generate_report'] == "Last 14 days":
                                           expected_next_data_insertion = last_inserted_record_time + (14*86400)
                                       elif endpoint['get_generate_report'] == "Last 30 days":
                                           expected_next_data_insertion = last_inserted_record_time + (30*86400)

                                       self.logger.info(f"Inserting the next time at 10 mins away {expected_next_data_insertion} now: {now} last_inserted_record_time: {last_inserted_record_time}")
                                       
                                       self.problem_time_interval = int((expected_next_data_insertion - now)/60)
                                       self.logger.info(f"Setting problem_time_interval {self.problem_time_interval}")
                                       self.problem_time_retrieve_flag = 1


                      except KeyError:
                        pass

                      except Exception as e:
                        logger.exception("Exception encountered while reading record insertion time: " + str(e),exc_info=True)

                    else:
                      logger.info("No records found and looks like first iteration")
                
                    self.logger.info(f"problem_time_interval: {self.problem_time_interval},pull_prb_data_iterations: {self.pull_prb_data_iterations}")

                  if get_problem_data_mgmt_zone == "Yes" and self.pull_prb_data_iterations >= self.problem_time_interval:
                    # Collect problem data
                    self.logger.info("Pulling and inserting problems data ")
                    self.pull_prb_data_iterations = 0
                    self.pull_prb_data(self.logger, entityID, self.problems_mgmt_zone, prb_management_zone_list, prb_report_date, activegate_endpoint, endpoint)
                  else:
                    self.pull_prb_data_iterations += 1
                    self.logger.info(f"Incremented pull_prb_data_iterations to: {self.pull_prb_data_iterations}")
                
                except Exception as e:
                    self.logger.exception("Exception logged in query " + str(e))
                    self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
                finally:
                    self.logger.info("Execution completed for query function in insightify")
                
    # *******************************************************************************    
    #           Function to pull the generated problems data 
    # *******************************************************************************

    def pull_prb_data(self, logger, entityID, problems_mgmt_zone, prb_management_zone_list, prb_report_date, ag_endpoint, endpoint_detail):
      try:
          self.logger.info(f"In pull_prb_data for problem_report_date {prb_report_date}")
        
          now = time.time()
          days = {'Last 1 day': 1, 'Last 7 days': 7, 'Last 14 days': 14, 'Last 30 days': 30}.get(prb_report_date, 7)
          end_date = now - (days * 86400)
          
          logger.info(f"calculated end_date: {end_date}")
          #end_date = now - 600 #Remove this after tests 
    
          start_time_ms = int(end_date) * 1000
          end_time_ms = int(now) * 1000
   
          logger.info(f"start ms: {start_time_ms}")
          logger.info(f"end_time_ms {end_time_ms}")

          if prb_management_zone_list != "" and prb_management_zone_list != "all" and prb_management_zone_list != "All":
            PRB_QUERY = self.SPECIFIC_PROBLEMS.replace("starttime", str(start_time_ms))
            PRB_QUERY = PRB_QUERY.replace("endtime", str(end_time_ms))
            PRB_QUERY = PRB_QUERY.replace("mgmt_zone_name",prb_management_zone_list)

          else:    
            PRB_QUERY = self.PROBLEMS.replace("starttime", str(start_time_ms))
            PRB_QUERY = PRB_QUERY.replace("endtime", str(end_time_ms))

          data = self.dtApiV2GetQuery(PRB_QUERY, endpoint_detail)
          data_to_be_added = 0

          if data is not None:
            if len(data) >= 0:
              try:
                nextPageKey = data['nextPageKey']

                while nextPageKey != "":
                  query = "problems?nextPageKey=" + nextPageKey
                  self.logger.info("Retrieve data " + query)

                  result = self.dtApiV2GetQuery(query, endpoint_detail)
                  nextPageKey = result['nextPageKey']
                  data["problems"] += result["problems"]
                  data_to_be_added = 1

              except KeyError:
                  if data_to_be_added == 1:
                    data["problems"] += result["problems"]
                    data_to_be_added = 0 

              except Exception as e:
                  self.logger.exception("Exception encountered in pull_prb_data" + str(e))

              self.logger.info("Getting some data")
              mean_resolution_time,problems_mgmt_zone = self.populate_problem_data(entityID, data["problems"], problems_mgmt_zone, ag_endpoint, endpoint_detail)

      except Exception as e:
          self.logger.exception("Exception encountered in pull_prb_data " + str(e))
          self.logger.info(f"Full traceback:\n{traceback.format_exc()}")
          

      finally:
         self.logger.info("Execution completed pull_prb_data")


    # ********************************************************************************************************
    #        Function to initialize the csv file which will be dumped as logs 
    # ********************************************************************************************************
    def initialize_csv_header(self):
      try:
          self.logger.info("In initialize_csv_header")  

          csv_data = ""
          csv_data="config_id,Endpoint Name,status,management.zone,Problem ID,Problem Link,problem.title,impact.level,severity.level,RCA or no RCA, MTTR(in hours)\n"

      except Exception as e:
          self.logger.exception("Exception encountered in initialize_csv_header: ", str(e), exc_info=True)


      finally:
          self.logger.info("Succesfully executed initialize_csv_header")  
          return csv_data 

    # ********************************************************************************************************
    #        Function to slice and dice problem trend and push metrics 
    # ********************************************************************************************************
    def slice_and_dice_problem_trend(self, logger, csv_data, endpoint_config):
       try:
           self.logger.info("In slice_and_dice_problem_trend")
           data = []
           f = io.StringIO(csv_data)
           reader = csv.DictReader(f)

           for row in reader:
             data.append(row)
             
           # Extract the timestamp column as a list of datetime objects
           timestamps = [datetime.datetime.fromtimestamp(int(row['starttime'])) for row in data]
           
           # Group the data by month,year, problem title and management zone, keeping track of the number of occurrences and the sum of downtime 
           result = {}
           for row, timestamp in zip(data, timestamps):
               key = (timestamp.year, timestamp.month, row["problem.title"], row["management.zone"],row["config_id"])
               if key not in result:
                   result[key] = {"count": 0, "downtime": []}
               result[key]["count"] += 1

               try:
                  mttr_value = float(row["mttr"])
               except ValueError:
                  self.logging.info(f"Non-numeric MTTR value encountered: {row['mttr']} for problem: {row['problem.title']}")
                  mttr_value = -1.0
                  
               result[key]["downtime"].append(mttr_value)
           
           # Format the result as a list of dictionaries, with keys being fieldnames
           result_data = []
           for key, value in result.items():
               year, month, column_value,zone,entityId = key
               count = value["count"]
               total_downtime = sum(value["downtime"])
               result_data.append({
                   "entityId":entityId,
                   "year": year,
                   "month": month,
                   "zone":zone,
                   "column_value": column_value,
                   "count": count,
                   "downtime": total_downtime
               })

           metric=""
           metric_downtime=""

           if (len(result_data) > 0):
            for item in result_data:
              metric += "incidents.seen,config_id=\"" + item['entityId'] + "\"" + ",year="+ str(item['year']) + ",month=" + str(item['month']) + ",problem_title=\"" + str(item['column_value']) + "\",mgmt_zone=\"" + str(item['zone']) + "\" " + str(item['count']) + "\n"
              metric_downtime += "downtime,config_id=\"" + item['entityId'] + "\"" + ",year="+ str(item['year']) + ",month=" + str(item['month']) + ",problem_title=\"" + str(item['column_value']) + "\",downtime=" + str(item['downtime']) + ",mgmt_zone=\"" + str(item['zone']) + "\" " + str(item['downtime']) + "\n"

            self.dtApiIngestMetrics(self.INGEST_METRICS,metric, endpoint_config)
            self.logger.info(f"MTTR {metric_downtime}")
            self.dtApiIngestMetrics(self.INGEST_METRICS,metric_downtime, endpoint_config)

           else:
            self.logger.info("[slice_and_dice_problem_trend] No problems data found to insert")           
      

       except Exception as e:
          self.logger.exception("Exception encountered slice_and_dice_problem_trend" + str(e), exc_info=True)

       finally:
          self.logger.info("Successful execution: slice_and_dice_problem_trend")

    # ********************************************************************************************************
    #        Function to populate problem metrics
    # ********************************************************************************************************
    def populate_problem_data(self, entityID, data, problems_mgmt_zone, ag_endpoint, endpoint_config):
        try:
          self.logger.info(f"In populate_problem_data:\n {entityID}")

          #Dictionary to maintain total number of problems at environment-level
          env_problem_data= {
          'service': 0,
          'resource': 0,
          'total_prb': 0,
          'availability': 0,
          'error_event': 0,
          'performance': 0,
          'application': 0,
          'custom_alert': 0,
          'infrastructure': 0,
          'environment': 0
        }

          env_problem_data['total_prb']=len(data)
          
          mean_rsp_time=[]
          median_rsp_time = 0
          total_prb_resolved = 0
          total_number_of_prb = 0 
          csv_data = self.initialize_csv_header()
          csv_data_list = []
          
          #Data that we will dump to log file so it can be retrieved (where logV2 is disabled)
          logger_csv_data = ""
          logger_csv_data="config_id,Endpoint Name,status,management.zone,Problem ID,Problem Link,starttime,endtime,problem.title,impact.level,severity.level,RCA or no RCA,mttr\n"

          #Value across the endpoint (and not limited to management zone)
          total_incident_reported = 0
          incidents_with_rca = 0
          incidents_wo_rca = 0
          total_mttr_rca = []
          total_mttr_wo_rca = []
          for i in range(len(data)):
            start_time = data[i]["startTime"]
            end_time = data[i]["endTime"]

            if end_time != -1:
              resolution_time = end_time - start_time
              logger.debug("Resolution_time", resolution_time)

              if int(resolution_time) >= int(endpoint_config["problem_to_incident_duration"]):
                total_incident_reported = total_incident_reported + 1
                #Management Zone
                key = ""

                try:
                  zones = data[i]['managementZones']

                  if len(zones) != 0:
                    for zone in zones:
                      key = key + zone['name'] + ","
                    key = key[:-1]
                  else:
                    key = "No management zone"

                except KeyError:
                  key = "No management zone"

                try:
                    problems_mgmt_zone[key].problems = problems_mgmt_zone[key].problems + 1

                except KeyError:
                    obj = self.problem_mgmt_zone()
                    obj.problems=1
                    obj.rootCause=0
                    obj.application=0
                    obj.service=0
                    obj.infrastructure=0
                    obj.error=0
                    obj.custom=0
                    obj.availability=0
                    obj.performance=0
                    obj.resource=0
                    obj.mttr_rca=0
                    obj.mgmt_zone=key
                    obj.mttr_wo_rca=-1
                    obj.mttr_rca_list=[]
                    obj.mttr_wo_rca_list=[]
                    problems_mgmt_zone[key]=obj
                
                if (data[i]["rootCauseEntity"]):
                   incidents_with_rca = incidents_with_rca + 1
                   total_mttr_rca.append(resolution_time)

                   problems_mgmt_zone[key].rootCause = problems_mgmt_zone[key].rootCause + 1
                   problems_mgmt_zone[key].mttr_rca_list.append(resolution_time)

                   #Check the length of csv_data since we have a limitation of allowing a string of only 5000 characters
                   if (csv_data.count('\n') >= 400):
                     csv_data_list.append(csv_data)
                     csv_data = self.initialize_csv_header()

                   csv_data = csv_data + entityID + "," + entityID + ",INFO,\"" + key + "\"," + data[i]["displayId"] + "," + endpoint_config["url"][:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",rca," + str(resolution_time/3600000) + "\n"
                   logger_csv_data = logger_csv_data + entityID + "," + entityID + ",INFO,\"" + key + "\"," + data[i]["displayId"] + "," + endpoint_config["url"][:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + str(int(start_time/1000)) + "," + str(end_time/1000) + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",rca," + str(resolution_time/3600000) + "\n"

                else:   
                   total_mttr_wo_rca.append(resolution_time)
                   incidents_wo_rca = incidents_wo_rca + 1 
                   problems_mgmt_zone[key].mttr_wo_rca_list.append(resolution_time)

                   #Check the length of csv_data since we have a limitation of allowing a string of only 5000 characters
                   if (csv_data.count('\n') >= 400):
                     csv_data_list.append(csv_data)
                     csv_data = self.initialize_csv_header()

                   csv_data = csv_data + entityID + "," + entityID + ",INFO,\"" +  key + "\"," + data[i]["displayId"] + "," + endpoint_config["url"][:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",no_rca,"+str(resolution_time/3600000)+"\n"
                   logger_csv_data = logger_csv_data + entityID + "," + entityID + ",INFO,\"" +  key + "\"," + data[i]["displayId"] + "," + endpoint_config["url"][:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + str(int(start_time/1000)) + "," + str(end_time/1000) + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",no_rca,"+str(resolution_time/3600000)+"\n"
                mean_rsp_time.append(resolution_time)
                severity = data[i]["severityLevel"]

                if severity == "AVAILABILITY":
                  env_problem_data['availability'] = env_problem_data['availability'] + 1
                  problems_mgmt_zone[key].availability += 1

                elif severity == "PERFORMANCE":
                  env_problem_data['performance'] = env_problem_data['performance'] + 1
                  problems_mgmt_zone[key].performance += 1

                elif severity == "ERROR":
                 env_problem_data['error_event'] = env_problem_data['error_event'] + 1
                 problems_mgmt_zone[key].error += 1

                elif severity == "RESOURCE_CONTENTION":
                  env_problem_data['resource'] = env_problem_data['resource'] + 1
                  problems_mgmt_zone[key].resource += 1

                elif severity == "CUSTOM_ALERT":
                  env_problem_data['custom_alert'] = env_problem_data['custom_alert'] + 1
                  problems_mgmt_zone[key].custom += 1

                impact_level = data[i]["impactLevel"]
                if impact_level == "SERVICES":
                  env_problem_data['service'] = env_problem_data['service'] + 1
                  problems_mgmt_zone[key].service += 1

                elif impact_level == "APPLICATION":
                  env_problem_data['application'] = env_problem_data['application'] + 1
                  problems_mgmt_zone[key].application += 1

                elif impact_level == "INFRASTRUCTURE":
                 env_problem_data['infrastructure'] = env_problem_data['infrastructure'] + 1
                 problems_mgmt_zone[key].infrastructure += 1
                 
                elif impact_level == "ENVIRONMENT":
                  env_problem_data['environment'] = env_problem_data['environment'] + 1
  

          for key in problems_mgmt_zone.keys():
              metric = ""
              self.logger.info("populating metrics for -> {}".format(key))
              #Find the median response time for each mgmt_zone and convert it to minutes (from microseconds)
              try:
                problems_mgmt_zone[key].mttr_rca = ((sum(problems_mgmt_zone[key].mttr_rca_list)/len(problems_mgmt_zone[key].mttr_rca_list)))/60000
              except ZeroDivisionError:
                problems_mgmt_zone[key].mttr_rca = -1

              #Find the median response time for each mgmt_zone and convert it to minutes (from microseconds)
              try:
                problems_mgmt_zone[key].mttr_wo_rca = ((sum(problems_mgmt_zone[key].mttr_wo_rca_list)/len(problems_mgmt_zone[key].mttr_wo_rca_list)))/60000
              except ZeroDivisionError:
                problems_mgmt_zone[key].mttr_wo_rca = -1 

              # Push management zone metric only if config is set to yes 
              if endpoint_config["get_problem_data_mgmt_zone"] == "Yes":
                metric += "total_reported_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].problems) + "\n"
                metric += "root_cause,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].rootCause) + "\n"
                metric += "reported_availability_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].availability) + "\n"
                metric += "reported_performance_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].performance) + "\n"
                metric += "reported_resource_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].resource) + "\n"
                metric += "reported_custom_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].custom) + "\n"
                metric += "reported_service_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].service) + "\n"
                metric += "reported_infra_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].infrastructure) + "\n"
                metric += "reported_application_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].application) + "\n"
                metric += "reported_error_problems,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].error) + "\n"
                metric += "mttr_with_rca,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].mttr_rca) + "\n"
                metric += "mttr_wo_rca,mgmt_zone=\"" + key + "\"" + ",config_id=" + entityID + " " + str(problems_mgmt_zone[key].mttr_wo_rca) + "\n"

                self.dtApiIngestMetrics(self.INGEST_METRICS, metric, endpoint_config)

          if (endpoint_config["get_problem_data_mgmt_zone"] == "Yes"):
              metric = ""
              import time
              now = time.time() 
 
              #Insert epoch time at the time of last record being inserted
              metric += "record_insertion_time" + ",config_id=" + entityID + " " + str(now) + "\n"
             
              mttr_rca = 0
              mttr_wo_rca = 0
              #Total mttr for the problems with rca 
              try:
                mttr_rca = ((sum(total_mttr_rca)))/60000
              except ZeroDivisionError:
                mttr_rca = -1

              #Total mttr for the problems with rca 
              try:
                mttr_wo_rca = ((sum(total_mttr_wo_rca)))/60000
              except ZeroDivisionError:
                mttr_wo_rca = -1
                
              #Find the median response time and convert it to minutes (from microseconds)
              try:
                median_rsp_time = ((sum(mean_rsp_time)/len(mean_rsp_time)))/60000
              except ZeroDivisionError:
                median_rsp_time = 0                

              #Insert the total incidents reported 
              metric += "total_incident_reported" + ",config_id=" + entityID + " " + str(total_incident_reported) + "\n"
              metric += "total_incidents_with_rca" + ",config_id=" + entityID + " " + str(incidents_with_rca) + "\n"
              metric += "total_incidents_wo_rca" + ",config_id=" + entityID + " " + str(incidents_wo_rca) + "\n"
              metric += "total_mttr_rca" + ",config_id=" + entityID + " " + str(mttr_rca) + "\n"
              metric += "total_mttr_wo_rca" + ",config_id=" + entityID + " " + str(mttr_wo_rca) + "\n"
              
              #Environment level metrics 
              metric += "env_problems" + ",config_id=" + entityID + " " + str(env_problem_data["total_prb"]) + "\n"
              metric += "env_service_problems" + ",config_id=" + entityID + " " + str(env_problem_data["service"]) + "\n"
              metric += "env_resource_problems" + ",config_id=" + entityID + " " + str(env_problem_data["resource"]) + "\n"
              metric += "env_availability_problems" + ",config_id=" + entityID + " " + str(env_problem_data["availability"]) + "\n"
              metric += "env_error_problems" + ",config_id=" + entityID + " " + str(env_problem_data["error_event"]) + "\n"
              metric += "env_performance_problems" + ",config_id=" + entityID + " " + str(env_problem_data["performance"]) + "\n"
              metric += "env_application_problems" + ",config_id=" + entityID + " " + str(env_problem_data["application"]) + "\n"
              metric += "env_custom_alert" + ",config_id=" + entityID + " " + str(env_problem_data["custom_alert"]) + "\n"
              metric += "env_infrastructure_problems" + ",config_id=" + entityID + " " + str(env_problem_data["infrastructure"]) + "\n"
              metric += "env_environment_problems" + ",config_id=" + entityID + " " + str(env_problem_data["environment"]) + "\n"
              metric += "problems_mttr" + ",config_id=" + entityID + " " + str(median_rsp_time) + "\n"

              self.dtApiIngestMetrics(self.INGEST_METRICS,metric, endpoint_config)
              
              prb_report_date = endpoint_config["get_generate_report"]

              #Once data is pushed, set next collection interval accordingly
              if prb_report_date == "Last 1 day":
                self.problem_time_interval = (1*1440) - 1 
              elif prb_report_date == "Last 7 days":
                self.problem_time_interval = (7*1440) - 1
              elif prb_report_date == "Last 14 days":
                self.problem_time_interval = (14*1440) - 1
              elif prb_report_date == "Last 30 days":
                self.problem_time_interval  = (30*1440) - 1
              
        except Exception as e:
          self.logger.exception("Exception encountered populate_problem_data" + str(e),exc_info=True)

        finally:
          self.logger.info("Successful execution: populate_problem_data")
          self.logger.info("Pushing the problem data in logs")
          self.logger.info(logger_csv_data)

          self.slice_and_dice_problem_trend(self.logger,logger_csv_data, endpoint_config)

          # Get the endpoint from ag_enpoint
          if ag_endpoint != "None":
            #Push the latest csv_data   
            csv_data_list.append(csv_data)  

            for csv_data in csv_data_list:
              reader = csv.DictReader(io.StringIO(csv_data))
              json_data = json.dumps(list(reader))

              query = ag_endpoint + "/logs/ingest"
              self.dtApiV2PushLogs(query,json_data, endpoint_config)

          return median_rsp_time, problems_mgmt_zone


    # *******************************************************************************    
    #           Function to post data using API v2 endpoint
    # *******************************************************************************    
              
    def dtApiV2PushLogs(self, query, payload, endpoint_config):
      try:    
        self.logger.info("In dtApiV2PushLogs")
                
        data = {}
        conf_password=endpoint_config["conftoken"]
        post_param = {'Accept':'application/json','Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = payload, verify=False)
        self.logger.info(f"Query executed {query} and received response {populate_data.status_code}")
                
        if populate_data.status_code == 401:
          msg = "Auth Error"
          self.logger.exception("Auth Error dtApiV2PushLogs: ")
              
      except Exception as e:
        self.logger.exception("Exception in dtApiV2PushLogs" + str(e), exc_info=True)
                
      finally:  
        self.logger.info("Succesfully completed dtApiV2PushLogs")


    # *******************************************************************************
    #           Function for configuration API for publish tenant
    # *******************************************************************************
    def dtConfApiv1(self, endpoint, endpoint_config):
      try:
        self.logger.info("In dtConfApiv1")
        data = {}

        url = endpoint_config["confurl"] 
        url = url.replace("/v1","/v2")
        conf_password = endpoint_config["conftoken"] 

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(conf_password)}
        response = requests.get(query, headers = get_param, verify=False)
        self.logger.info(f"Query: {query} Returned response: {response.status_code}")

        response.raise_for_status()  # This will raise an HTTPError for bad responses
        
        if 200 <= response.status_code < 300:
            data = response.json()
        else:
            self.logger.info(f"[dtConfApiv1] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
          self.logger.info(f"[dtConfApiv1] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
          self.logger.info(f"[dtConfApiv1] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
          self.logger.info(f"[dtConfApiv1] JSON decode error: {json_err}")
      except Exception as e:
          self.logger.info(f"Unexpected error in dtConfApiv1: {str(e)}")
    
      finally:
        self.logger.info("Successful execution of dtConfApiv1")  
        return data

    # *******************************************************************************    
    #           Function for configuration API for pulling data
    # *******************************************************************************    
    def dtConfApi(self, endpoint):
      try:
        self.logger.info("In dtConfApi")  
        data = {}

        url = self.url
        url = url.replace("/v1","/config/v1")

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        response = requests.get(query, headers = get_param, verify=False)
        self.logger.info(query)

        response.raise_for_status()  # This will raise an HTTPError for bad responses
        
        if 200 <= response.status_code < 300:
            data = response.json()
        else:
            self.logger.info(f"[dtConfApi] Unexpected status code: {response.status_code}")
            
      except requests.exceptions.HTTPError as http_err:
          self.logger.info(f"[dtConfApi] HTTP error encountered: {http_err}")
      except requests.exceptions.RequestException as req_err:
          self.logger.info(f"[dtConfApi] Request error encountered: {req_err}")
      except json.JSONDecodeError as json_err:
          self.logger.info(f"[dtConfApi] JSON decode error: {json_err}")
      except Exception as e:
          self.logger.info(f"Unexpected error in dtConfApi: {str(e)}")
    
      finally:
        self.logger.info("Successful execution of dtConfApi")  
        return data


def main():
    ExtensionImpl().run()

if __name__ == '__main__':
    main()