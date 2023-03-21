import io, csv
import math
import time
import json
import logging
import requests
import tempfile
import datetime
from enum import Enum
import iteration
#from iteration import COLLECT_FF_DATA,COLLECT_PROBLEM_DATA,COLLECT_CONSUMPTION_DATA,PROBLEM_INCIDENT
from constant import *
from pprint import pprint
from pathlib import Path
from random import randrange
from ruxit.api.data import PluginProperty
from ruxit.api.base_plugin import RemoteBasePlugin

logger = logging.getLogger(__name__)

class RemoteInsightifyExtension(RemoteBasePlugin):

    class split_consumption:
        def __init__(self):
          self.dem_units = 0
          self.ddu_units = 0
          self.host_units = 0
          self.mgmt_zone = 0

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

    class mgmt_zone_data:
        def __init__(self):
          self.tag = 0
          self.req_attr = 0
          self.problems = 0
          self.host_group = 0
          self.api_tokens = 0
          self.ddu_units = 0.0
          self.dem_units = 0.0
          self.host_units = 0.0
          self.applications = 0
          self.process_group= 0
          self.key_requests = 0
          self.session_replay = 0
          self.key_usr_actions = 0
          self.alerting_profile = 0
          self.problem_notification = 0
          self.configured_mgmt_zones = 0
          self.request_attribute = 0
          self.conversion_goals = 0
          self.session_properties = 0

    class problem_data:
      def __init__(self):
        self.service = 0
        self.resource = 0
        self.total_prb = 0
        self.availability= 0
        self.prb_resolved = 0 
        self.error_event = 0
        self.performance = 0
        self.application = 0
        self.environment = 0
        self.custom_alert = 0
        self.infrastructure = 0

    class app:
      def __init__(self):
       self.name = ""
       self.type = ""
       self.entityId = ""
       self.consumption = 0
       self.dem = 0

        
    class State(Enum):
        UNDERUTILIZED = 0
        NEEDSATTENTION = 1
        HEALTHY = 2
    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to populate the host as per management zone 
    #------------------------------------------------------------------------
    def populate_host_cache(self, split_data, hostGroup_splitdata, entity = ""):
      try:
          logger.info("In populate_host_cache")
          #If entity is null, it indicates the entire populate_host_cache 
          if entity == "":
            hosts = self.dtApiQuery(INFRA_API)

            for host in hosts:
              mgtzone = ""
              hostGroup = ""
              #logger.info(host)

              #Populate Management Zone(s) for each host
              try:
                zones = host['managementZones']

                for zone in zones:
                  mgtzone = mgtzone + zone['name'] + ","
                mgtzone = mgtzone[:-1]

              except KeyError:
                mgtzone = "No management zone"

              #Populate Host group(s) for each host
              try:
                if host['hostGroup']:
                  hostGroup = host['hostGroup']['name']
              except KeyError:
                  hostGroup = "No host Group"
              
              if host['entityId'] not in split_data.keys():
                obj = RemoteInsightifyExtension.split_consumption()
                obj.mgmt_zone = mgtzone
                obj.host_units = host['consumedHostUnits']
                split_data[host['entityId']] = obj 

              if hostGroup not in hostGroup_splitdata.keys():
                obj = RemoteInsightifyExtension.split_consumption()
                obj.mgmt_zone = hostGroup 
                obj.host_units = host['consumedHostUnits']
                hostGroup_splitdata[host['entityId']] = obj 

            logger.info("Cache")
            for key in hostGroup_splitdata.keys():
              logger.info(key)
          #If entity is sent, it indicates just push that host in the cache 
          else:
            host = entity
            mgtzone = ""
            hostGroup = ""

            #Populate Management Zone(s) for each host

            try:
              zones = host['managementZones']
              for zone in zones:
                mgtzone = mgtzone + zone['name'] + ","
              mgtzone = mgtzone[:-1]
            except KeyError:
              mgtzone = "No management zone"
          
            #Populate Host group(s) for each host
            try:
              if host['hostGroup']:
                hostGroup = host['hostGroup']['name']
            except KeyError:
                hostGroup = "No host Group"
                pass

            if host['entityId'] not in split_data.keys():
              logger.info("Not in cache ", host['entityId'])  
              obj = RemoteInsightifyExtension.split_consumption()
              obj.host_units = host['consumedHostUnits']
              obj.mgmt_zone = mgtzone
              split_data[host['entityId']] = obj 

            if hostGroup not in hostGroup_splitdata.keys():
              obj = RemoteInsightifyExtension.split_consumption()
              obj.mgmt_zone = hostGroup 
              obj.host_units = host['consumedHostUnits']
              hostGroup_splitdata[host['entityId']] = obj 

      except Exception as e:
          logger.exception("Exception while running populate_host_cache", str(e), exc_info=True)

      finally:
          logger.info("Successful execution: populate_host_cache")
          return split_data, hostGroup_splitdata 

    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to categorize the entity for DDU as per management zone 
    #------------------------------------------------------------------------

    def push_entity(self, ddu_mgmt_zone, availability_mgmt_zone, entity):
      try:
         logger.info("In push_entity " + entity)
         availability_zone = ""
         # The logic would be different for EBS_VOLUME & DYNAMO_DB_TABLE since these are associated to AWS EC2 instance or AWS AVAILABILITY 
         if 'EBS_VOLUME' in entity:
             try:
                mz = ddu_mgmt_zone[entity] 

             except KeyError:
                 fetch_entity_detail_query = DDU_ENTITY_DETAILS + "/" + entity 
                 data = self.dtApiV2GetQuery(fetch_entity_detail_query)
  
                 if data is not None: 
                    ec2 = data.get('fromRelationships', {}).get('isDiskOf', [{}])[0].get('id')
                    availability_zone = data['properties']['arn'].split(':volume')[:-1][0]
                    
                    try:
                      mgmt_zone = availability_mgmt_zone[availability_zone]
                    except KeyError:
                      ec2_detail = DDU_ENTITY_DETAILS + "/" + ec2 

                      data = self.dtApiV2GetQuery(ec2_detail)
                      #Management Zone
                      key = ""
                      try:
                        zones = data['managementZones']
                     
                        if len(zones) is not 0:
                          for zone in zones:
                            key = key + zone['name'] + ","
                          key = key[:-1]

                        else:  
                          key = "No management zone"

                      except KeyError:
                        key = "No management zone"

                      ddu_mgmt_zone[entity] = key
                      availability_mgmt_zone[availability_zone] = key 


         elif 'DYNAMO_DB_TABLE' in entity:
             try:
                mz = ddu_mgmt_zone[entity]
             
             except KeyError:
                 fetch_entity_detail_query = DDU_ENTITY_DETAILS + "/" + entity
                 data = self.dtApiV2GetQuery(fetch_entity_detail_query)
                 
                 if data is not None: 
                    ec2 = data.get('toRelationships', {}).get('isSiteOf', [{}])[0].get('id')
                    availability_zone = data['properties']['arn'].split(':table')[:-1][0]
                    
                    try:
                      mgmt_zone = availability_mgmt_zone[availability_zone]
                    except KeyError:
                      ec2_detail = DDU_ENTITY_DETAILS + "/" + ec2 
                 
                      data = self.dtApiV2GetQuery(ec2_detail)
                      
                      #Management Zone
                      key = ""
                      try:
                        zones = data['managementZones']
                     
                        if len(zones) is not 0:
                          for zone in zones:
                            key = key + zone['name'] + ","
                          key = key[:-1]
                        else:  
                          key = "No management zone"
                      
                      except KeyError:
                        key = "No management zone"
                      
                      ddu_mgmt_zone[entity] = key
                      availability_mgmt_zone[availability_zone] = key 
                      
         else :
             try:
                mz = ddu_mgmt_zone[entity]

             except KeyError:
                fetch_entity_detail_query = DDU_ENTITY_DETAILS + "/" + entity
                data = self.dtApiV2GetQuery(fetch_entity_detail_query)

                if data is not None:
                  #Management Zone
                  key = ""
                  try:
                    zones = data['managementZones']
                    if len(zones) is not 0:
                      for zone in zones:
                        key = key + zone['name'] + ","
                      key = key[:-1]
                    else:  
                      key = "No management zone"

                  except KeyError:
                    key = "No management zone"

                  ddu_mgmt_zone[entity] = key
                  availability_mgmt_zone[availability_zone] = key

      except Exception as e:
          logger.exception("Exception while running push_entity", str(e), exc_info=True)

      finally:
          logger.info("Successful execution: push_entity")
          return ddu_mgmt_zone, availability_mgmt_zone 
    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to categorize all the entity consuming DDUs as per management zone 
    #------------------------------------------------------------------------
    def populate_ddu_cache(self, ddu_mgmt_zone, availability_mgmt_zone, entity = ""):
      try:
          logger.info("In populate_ddu_cache")
          ddu_consumption_mgmt_zone = {}
          ddu_consumption = self.dtApiV2GetQuery(DDU_ENTITY_CONSUMPTION)

          try:
            if (len(ddu_consumption['result'])) > 0:
                entity_list = ddu_consumption['result'][0]['data']

                for item in entity_list:
                    entity = item['dimensions'][0]
                    ddu_mgmt_zone, availability_mgmt_zone = self.push_entity(ddu_mgmt_zone, availability_mgmt_zone, entity)

          except KeyError:
             logger.info("Found no records in DDU consumption") 
             pass 
         
      except Exception as e:
          logger.exception("Exception while running populate_ddu_cache ", str(e), exc_info=True)

      finally:
          logger.info("Successful execution: populate_ddu_cache")
          return ddu_mgmt_zone, availability_mgmt_zone 

    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to categorize the applications as per management zone 
    #------------------------------------------------------------------------
    
    def populate_app_cache(self, app_mgmt_zone):
      try:
        logger.info("In populate_app_cache")
       
        applications = self.dtApiQuery(FETCH_APPLICATIONS)
    
        for application in applications:
          appInfo = RemoteInsightifyExtension.app()
          appInfo.name = application['displayName']
    
          #For custom-type application, applicationType is not populated, hence the check
          try:
            appInfo.type = application['applicationType']
          except KeyError:
            appInfo.type = "Not available"
    
          appInfo.entityId = application['entityId']
     
          key = ""
          #Management Zone
          try:
            zones = application['managementZones']
            for zone in zones:
              key = key + zone['name'] + ","
            key = key[:-1]
          except KeyError:
            key = "No management zone"
    
          if key in app_mgmt_zone.keys():
            app_mgmt_zone[key].append(appInfo)
          else:
            app_mgmt_zone[key] = [appInfo]
       
        logger.info("Successful execution: populate_app_cache")
        
      except Exception as e:
        logger.exception("Exception while running populate_app_cache", str(e))
    
      finally:
        logger.info("Successful execution: populate_app_cache")
        return app_mgmt_zone

    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to fetch all the synthetic browsers and append it to the directory "app_mgmt_zone" 
    #------------------------------------------------------------------------
    def populate_syn_app_cache(self, app_mgmt_zone):
      try:
        logger.info("In populate_syn_app_cache")
       
        applications = self.dtApiQuery(FETCH_SYN_APPLICATIONS)
        application = applications['monitors']
    
        for i in range(len(application)):
          appInfo = RemoteInsightifyExtension.app()
          appInfo.name = application[i]['name']
    
          #For custom-type application, applicationType is not populated, hence the check
          try:
            if application[i]['type'] is not "HTTP":
              appInfo.type = "Synthetic"
            else:
              appInfo.type = "HTTP"
          except KeyError:
            appInfo.type = "Synthetic"
              
          appInfo.entityId = application[i]['entityId']
     
          #Management Zone
          key = ""
          try:
            zones = application[i]['managementZones']
            for zone in zones:
              key = key + zone['name'] + ","
            key = key[:-1]
          except KeyError:
            key = "No management zone"
    
          if key in app_mgmt_zone.keys():
            app_mgmt_zone[key].append(appInfo)
          else:
            app_mgmt_zone[key] = [appInfo]
     
        logger.info("Successful execution: fetch_sync_application")
        
      except Exception as e:
        logger.exception("Exception while running populate_syn_app_cache", str(e), exc_info=True)
    
      finally:
        logger.info("Execution completed populate_syn_app_cache")
        return app_mgmt_zone
    # ****************************************************************************************************    
    #           Function to initialize the cache that will be used for management zone slicing 
    # ****************************************************************************************************    
    def initialize(self, **kwargs):
        try:  
            self.url = self.config.get("url", "https://demo.live.dynatrace.com/api/v1/")
            self.password = self.config.get("token", "admin")
            self.state_interval = self.config.get("state_interval", 60)

            self.get_mgmt_zone_data = self.config.get("get_mgmt_zone_data", "True")
            self.get_hu_hostgroup_data = self.config.get("get_hu_hostgroup_data", "False")
            self.get_problem_data = self.config.get("get_problem_data", "Yes")
            self.get_ff_data = self.config.get("get_ff_data", "Yes")
            self.get_problem_data_mgmt_zone = self.config.get("get_problem_data_mgmt_zone","Yes")
            self.confurl = self.config.get("confurl","https://push.live.dynatrace.com/api/v2/")
            self.conf_password = self.config.get("conftoken", "Token")
            self.prb_management_zone_list = self.config.get("management_zone_name","all")
            self.prb_report_date = self.config.get("get_generate_report","Last 30 days")
            self.activegate_endpoint = self.config.get("ag_endpoint","")
            self.converted_to_incident_duration = self.config.get("problem_to_incident_duration","30")
       
            #Convert mins to ms (as problems api v2 reports resolution time in ms)
            self.converted_to_incident_duration = int(self.converted_to_incident_duration)*60000

            #Flag to indicate if earlier record push value has been pulled
            self.problem_time_retrieve_flag = 0

            #Local copy of the variable to identify when to pull problem data
            self.problem_time_interval = iteration.COLLECT_PROBLEM_DATA 

            #Other variables
            self.consumption_data_iterations = 0
            self.pull_prb_data_iterations = 0
            self.ff_data_iterations = 0
            self.state_iterations = 0
            self.host_consumption = 0
            self.dem_consumption = 0
            self.ddu_consumption = 0

            self.dashboard_created = 0
            self.problem_dashboard_created = 0
            #dictionary to maintain mapping of EC2 availability zone with management zones useful for DDUs 
            self.availability_mgmt_zone = {}

            #dictionary to maintain mapping of entities with management zones used for DDUs 
            self.ddu_mgmt_zone={}

            self.split_data={}
            self.hostGroup_splitdata = {}
            self.app_mgmt_zone = {}
            self.problems_mgmt_zone = {}

            if self.get_mgmt_zone_data == "Yes" or self.get_hu_hostgroup_data == "Yes":
                logger.info("In initialize")

                #Populate the hosts as per management zone and host group
                self.split_data, self.hostGroup_splitdata = self.populate_host_cache(self.split_data, self.hostGroup_splitdata)

                #First fetch all the applications
                self.app_mgmt_zone = self.populate_app_cache(self.app_mgmt_zone)

                #Now fetch all the synthetic applications 
                self.app_mgmt_zone = self.populate_syn_app_cache(self.app_mgmt_zone)

                #Commenting this as enabling DDUs to split per management zone results in multiple API calls which potentially 
                #can impact any automation suites that use API calls as there is a limit of number of API calls/min. So, uncomment it accordingly. 
                #Populate DDUs as per management zone 
                #self.ddu_mgmt_zone, self.availability_mgmt_zone = self.populate_ddu_cache(self.ddu_mgmt_zone, self.availability_mgmt_zone)
                

        except Exception as e:
            logger.exception("Exception while running initialize", str(e), exc_info=True)

        finally:
            logger.info("Successful execution initialize ")

    # *********************************************************************    
    #           Function to get metrics/SLO using API V2 endpoint
    # *********************************************************************    
    def dtApiV2GetQuery(self, endpoint):
      try:
        logger.info("In dtApiV2GetQuery")  
        data = {}

        config_url = self.url
        config_url = config_url.replace("v1","v2")

        query = str(config_url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("in dtApiV2GetQuery ", str(e))

      finally:
        logger.info("In dtApiV2GetQuery")  
        return data

    # *********************************************************************
    #           Function to get metrics using API V2 endpoint
    # *********************************************************************
    def dtApiV2GetMetricDataPoint(self, endpoint):
      try:
        logger.info("In dtApiV2GetMetricDataPoint")
        data = {}

        config_url = self.confurl
        query = str(config_url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.info("in dtApiV2GetMetricDataPoint", str(e))

      finally:
        logger.info("Succesfully completion dtApiV2GetMetricDataPoint")
        return data


    # *******************************************************************************    
    #            Function to push metrics using Ingest Metrics endpoint
    #      This is pushed to ingest host,dem and ddu units per management zone 
    # *******************************************************************************    
    def dtApiIngestMetrics(self, endpoint, payload):
      try:
        logger.info("In dtApiIngestMetrics ")
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v1","v2")

        query = str(config_url) + endpoint
        post_param = {'Content-Type':'text/plain;charset=utf-8', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = payload, verify=False)

        logger.info(query)
        logger.info(payload)
        logger.info(populate_data)
        logger.info(populate_data.content)


        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception in dtApiIngestMetrics ", str(e))

      finally:
        logger.info("Succesfully completed dtApiIngestMetrics")  
        return data

    # *******************************************************************************    
    #           Function to post data using API v2 endpoint
    # *******************************************************************************    

    def dtApiV2PostQuery(self, endpoint, payload):
      try:
        logger.info("In dtApiV2PostQuery")  
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v1","v2")
        
        query = str(config_url) + endpoint
        post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = json.dumps(payload), verify=False)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception in dtApiV2PostQuery " + str(e))

      finally:
        logger.info("Succesfully completed dtApiV2PostQuery")  
        return data

    # *******************************************************************************    
    #           Function to post data using API v1 endpoint
    # *******************************************************************************    
    def dtApiV1PostQuery(self, endpoint, payload):
      try:
        logger.info("In dtApiV1PostQuery")  
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v2","config/v1")
        
        query = str(config_url) + endpoint
        post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        populate_data = requests.post(query, headers=post_param, data=json.dumps(payload), verify=False)
        logger.info(populate_data)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.info("In dtApiV1PostQuery: " + str(e))  

      finally:
        logger.info("Succesfully completed dtApiV1PostQuery")  

    # *******************************************************************************    
    #           Function to post data using API v1 endpoint
    # *******************************************************************************    
    def query(self, **kwargs):
        try:  
            logger.info("In query function")
            group_name = self.get_group_name()

            endpoint=self.activation.endpoint_name.strip()
            g1 = self.topology_builder.create_group(group_name, group_name)
            topology_device = g1.create_element(group_name + " - " + endpoint, group_name + " - " + endpoint)
            entityID = f"CUSTOM_DEVICE-{topology_device.id:X}"

            topology_device.report_property("Tenant", endpoint)
            deviceID = "Adoption Metrics - " + endpoint
            topology_device.report_property("Tenant", endpoint)
            topology_device.report_property("Plugin version", kwargs["json_config"]["version"])

            if self.dashboard_created == 0:
                dashboard_file = Path(__file__).parent / "dashboard.json"
                fp = open(dashboard_file,'r')
                dashboard_json = json.loads(fp.read())

                payload = json.dumps(dashboard_json).replace('$1',endpoint) 
                dashboard_json = json.loads(payload)
                dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                dashboards = self.dtConfApiv1(GET_EXISTING_DASHBOARD)

                logger.info("Found dashboards: " + str(len(dashboards)))
                #Check if the dashboard is already present
                if len(dashboards) > 0:
                  dashboardList = dashboards["dashboards"]
                  
                  for dashboard in dashboardList:
                      if dashboard["name"].__eq__(dashboard_name):
                        logger.info("Found a dashboard already by that configuration. Skipping.. " + dashboard["name"])
                        self.dashboard_created = 1
                        continue

                #Verifying that the dashboard is not already created
                if (self.dashboard_created == 0):
                  logger.info("Will create a dashboard " + dashboard_name)
                  self.dtApiV1PostQuery(DASHBOARDS, dashboard_json)
                  self.dashboard_created = 1
                  
            if (self.get_problem_data_mgmt_zone == "Yes" and self.problem_dashboard_created == 0):
                dashboard_file = Path(__file__).parent / "operation_dashboard.json"
                fp = open(dashboard_file,'r')
                dashboard_json = json.loads(fp.read())
                
                payload = json.dumps(dashboard_json).replace('$1',endpoint) 
                dashboard_json = json.loads(payload)
                dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                dashboards = self.dtConfApiv1(GET_EXISTING_DASHBOARD)
            
                logger.info("(problem_dashboard_check) Dashboard founds: " + str(len(dashboards))) 
                #Check if the dashboard is already present
                if len(dashboards) > 0:
                  dashboardList = dashboards["dashboards"]
                
                  for dashboard in dashboardList:
                      logger.info(dashboard["name"]) 
                      if dashboard["name"].__eq__(dashboard_name):
                        logger.info("Found a dashboard already by that configuration. Skipping.. " + dashboard["name"])
                        self.problem_dashboard_created = 1
                        continue 
            
                #Verifying that the dashboard is not already created
                if (self.problem_dashboard_created == 0):
                  logger.info("Will create a dashboard " + dashboard_name)
                  self.dtApiV1PostQuery(DASHBOARDS, dashboard_json)

                  #Create benefit value realisation dashboard 
                  dashboard_file = Path(__file__).parent / "benefit_realisation_report.json"
                  fp = open(dashboard_file,'r')
                  dashboard_json = json.loads(fp.read())

                  dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                  logger.info("Will also create " + dashboard_name)

                  payload = json.dumps(dashboard_json).replace('$1',endpoint)
                  dashboard_json = json.loads(payload)
                  self.dtApiV1PostQuery(DASHBOARDS, dashboard_json)

                  #Create problem trend analysis
                  dashboard_file = Path(__file__).parent / "problem_trend_and_analysis.json"
                  fp = open(dashboard_file,'r')
                  dashboard_json = json.loads(fp.read())

                  dashboard_name = dashboard_json["dashboardMetadata"]["name"]
                  payload = json.dumps(dashboard_json).replace('$1',endpoint)
                  dashboard_json = json.loads(payload)
                  self.dtApiV1PostQuery(DASHBOARDS, dashboard_json)

                  self.problem_dashboard_created = 1

            #Pull problem data and other feature flags
            detailed_data = RemoteInsightifyExtension.mgmt_zone_data()
            detailed_prb_data = RemoteInsightifyExtension.problem_data()

            if self.consumption_data_iterations >= iteration.COLLECT_CONSUMPTION_DATA:
                self.consumption_data_iterations = 0 
                host_consumption, dem_consumption, ddu_consumption, detailed_data = self.pull_consumption_data(logger, self.host_consumption, self.dem_consumption, self.ddu_consumption, detailed_data)
                # Push consumption data 
                topology_device.absolute("databases.host_unit_consumption", host_consumption, {"dimension":"Total Host Units"} ) 
                topology_device.absolute("databases.dem_unit_consumption", dem_consumption, {"dimension":"Total DEM Units" } ) 
                topology_device.absolute("databases.ddu_unit_consumption", ddu_consumption, {"dimension":"Total DDU Units" } ) 

                logger.info("pull ddu_units_consumption: " + str(ddu_consumption))
                logger.info("pul dem_units_consumption: " + str(dem_consumption))
                logger.info("pull host_units_consumption: " +  str(host_consumption))

                if (self.get_mgmt_zone_data == "Yes") or (self.get_hu_hostgroup_data == "Yes"):
                  ddu_mgmt_zone = self.populate_management_zone_consumption(entityID, self.split_data, self.hostGroup_splitdata, self.availability_mgmt_zone, self.ddu_mgmt_zone, self.app_mgmt_zone)
            else:
              self.consumption_data_iterations = self.consumption_data_iterations + 1

            #Verify if there are any records inserted for the problem data before 
            if self.problem_time_retrieve_flag == 0: 
              #Get the last inserted record timestamp
              query = GET_DATA_INSERTED_DATA_POINT.replace("ID",entityID)
              get_last_inserted_data_set = self.dtApiV2GetMetricDataPoint(query)
              logger.info(get_last_inserted_data_set)
 
              if get_last_inserted_data_set:
                try:
                   logger.info("Will identify the last inserted record timestamp")
                  
                   for result_obj in get_last_inserted_data_set['result']:
                       logger.info(result_obj)
                       for data_obj in result_obj['data']:
                           logger.info(data_obj['dimensions'][0])
                           if data_obj['dimensions'][0] == entityID:
                             logger.info("Found the custom-device" +  data_obj['dimensions'][0])

       
                             for j in range(len(data_obj['values'])):
                               if data_obj['values'][j]:
                                 logger.info(data_obj['values'][j])
                                 #logger.info(data_obj['timestamps'][j])
                                 last_inserted_record_time = data_obj['values'][j]
                                 logger.info("Last inserted record time: " + str(last_inserted_record_time))
          
                                 #Setup the next expected insertion time (using the last record timestamp)
                                 now = time.time()
                                 if self.prb_report_date == "Last 30 days":
                                     expected_next_data_insertion = last_inserted_record_time+(30*86400)
                                 elif self.prb_report_date == "Last 60 days":
                                     expected_next_data_insertion = last_inserted_record_time + (60*86400)
                                 elif self.prb_report_date == "Last 90 days":
                                     expected_next_data_insertion = last_inserted_record_time + (90*86400)
                                 else:
                                     expected_next_data_insertion = last_inserted_record_time + (365*86400)

                                 self.problem_time_interval = int((expected_next_data_insertion - now)/60)
                                 self.problem_time_retrieve_flag = 1


                except KeyError:
                  pass

                except Exception as e:
                  logger.exception("Exception encountered while reading record insertion time: " + str(e))

              else:
                logger.info("No records found and looks like first iteration")

            logger.info("iteration.COLLECT_PROBLEM_DATA " +  str(iteration.COLLECT_PROBLEM_DATA))
            logger.info("self.problem_time_interval " + str(self.problem_time_interval))
            logger.info("self.pull_prb_data_iterations " + str(self.pull_prb_data_iterations))

            if (self.get_problem_data == "Yes") and self.pull_prb_data_iterations >= self.problem_time_interval:
                # Collect problem data
                self.pull_prb_data_iterations = 0 
                detailed_prb_data = self.pull_prb_data(logger, entityID, topology_device, detailed_prb_data, self.problems_mgmt_zone, self.prb_management_zone_list, self.prb_report_date, self.activegate_endpoint,endpoint)
            else:
              self.pull_prb_data_iterations = self.pull_prb_data_iterations + 1 

            if (self.get_ff_data == "Yes") and self.ff_data_iterations >= iteration.COLLECT_FF_DATA:
                # Collect feature flag data after a week 
                self.ff_data_iterations = 0 
                detailed_data = self.pull_ff_data(logger, topology_device, detailed_data)
            else:
              self.ff_data_iterations = self.ff_data_iterations + 1 

        except Exception as e:
          logger.exception("Exception encountered in query " + str(e))

        finally:
          logger.info("Execution completed query function")

    # *******************************************************************************    
    #           Function to pull the generated problems data 
    # *******************************************************************************    

    def pull_prb_data(self, logger, entityID, topology_device, detailed_prb_data, problems_mgmt_zone, prb_management_zone_list, prb_report_date, ag_endpoint, endpoint):
        try:
          logger.info("In pull_prb_data")

          now = time.time()
          if prb_report_date == "Last 30 days":
              end_date = now - (30*86400) 

          elif prb_report_date == "Last 60 days":
              end_date = now - (60*86400) 

          elif prb_report_date == "Last 90 days":
              end_date = now - (90*86400) 

          else:
              end_date = now - (365*86400) 

          start_time_ms = int(end_date) * 1000
          end_time_ms = int(now) * 1000
   
          if prb_management_zone_list != "" and prb_management_zone_list != "all" and prb_management_zone_list != "All":
            PRB_QUERY = SPECIFIC_PROBLEMS.replace("starttime", str(start_time_ms))
            PRB_QUERY = PRB_QUERY.replace("endtime", str(end_time_ms))
            PRB_QUERY = PRB_QUERY.replace("mgmt_zone_name",prb_management_zone_list)

          else:    
            PRB_QUERY = PROBLEMS.replace("starttime", str(start_time_ms))
            PRB_QUERY = PRB_QUERY.replace("endtime", str(end_time_ms))

          data = self.dtApiV2GetQuery(PRB_QUERY)

          data_to_be_added = 0

          if data is not None:
            if len(data) >= 0:
              try:
                nextPageKey = data['nextPageKey']

                while nextPageKey != "":
                  query = "problems?nextPageKey=" + nextPageKey
                  result = self.dtApiV2GetQuery(query)

                  nextPageKey = result['nextPageKey']
                  data["problems"] += result["problems"]
                  data_to_be_added = 1

              except KeyError:
                  if data_to_be_added == 1:
                    data["problems"] += result["problems"]
                    data_to_be_added = 0 

              except Exception as e:
                  logger.exception("Exception encountered in pull_prb_data" + str(e))

              detail_prb_data, mean_resolution_time,problems_mgmt_zone = self.populate_problem_data(entityID, data["problems"], detailed_prb_data, problems_mgmt_zone, ag_endpoint, endpoint)

              topology_device.absolute("databases.problem_analysis", detailed_prb_data.total_prb, {"dimension":"Total Problems"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.availability, {"dimension":"Availability Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.performance, {"dimension":"Performance Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.error_event, {"dimension":"Error Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.resource, {"dimension":"Resource Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.service, {"dimension":"Service Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.application, {"dimension":"Application Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.infrastructure, {"dimension":"Infrastructure Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.environment, {"dimension":"Environment Problem"})
              topology_device.absolute("databases.problem_analysis", detailed_prb_data.custom_alert, {"dimension":"Custom Problem"})
              topology_device.absolute("databases.problem_analysis", mean_resolution_time, {"dimension":"Mean Resolution Time"})

        except Exception as e:
          logger.exception("Exception encountered in pull_prb_data " + str(e))

        finally:
          logger.info("Execution completed pull_prb_data")
          return detailed_prb_data

    # *******************************************************************************    
    #                Function to push ff data 
    # *******************************************************************************    
    def push_ff_data(self, logger, topology_device, detailed_data):
       try:
           logger.info("In push_ff_data")

           topology_device.absolute("databases.alerting_profile", detailed_data.alerting_profile,{"dimension":"Alerting Profiles"})
           topology_device.absolute("databases.session_properties", detailed_data.session_properties,{"dimension":"Session Properties"})
           topology_device.absolute("databases.process_groups", detailed_data.process_group,{"dimension":"Process Groups"})
           topology_device.absolute("databases.tags", detailed_data.tag,{"dimension":"Tags"})
           topology_device.absolute("databases.mgmt_zone", detailed_data.configured_mgmt_zones,{"dimension":"Management Zone"})
           topology_device.absolute("databases.problem_notifications", detailed_data.problem_notification, {"dimension":"Problem Notifications"})
           topology_device.absolute("databases.key_requests", detailed_data.key_requests,{"dimension":"Key Requests"})
           topology_device.absolute("databases.request_attributes", detailed_data.request_attribute,{"dimension":"Request Attributes"})
           topology_device.absolute("databases.conversion_goals", detailed_data.conversion_goals,{"dimension":"Conversion Goals"})
           topology_device.absolute("databases.session_replay", detailed_data.session_replay,{"dimension":"Session Replay"})

       except Exception as e:
         logger.exception("Exception encountered in push_ff_data" + str(e))

       finally:
         logger.info("Execution completed push_ff_data")
         return detailed_data

    # *******************************************************************************    
    #           Function to categorize consumption data as per management zones 
    # *******************************************************************************    
    def populate_consumption(self, app_mgmt_zone, query, multiplying_factor, syn = 0):
      try:
        consumption_details = {}
        logger.info("In populate_consumption")
        applications = self.dtApiV2Query(logger, query)

        #First fetch all the applications
        self.app_mgmt_zone = self.populate_app_cache(self.app_mgmt_zone)

        #Now fetch all the synthetic applications
        self.app_mgmt_zone = self.populate_syn_app_cache(self.app_mgmt_zone)

        if (len(applications)) > 0:
          apps = applications['result'][0]['data']
          for billing in apps:
            dimensions = billing['dimensions']
            if syn == 0:
              if dimensions[1] == "Billed":
                consumption_details[dimensions[0]] = billing['values'][0]
            elif syn >= 0:
                consumption_details[dimensions[0]] = billing['values'][0]
       
          for key in consumption_details.keys():
            for mgmt_zone_name in app_mgmt_zone.keys():
              for i in range(len(app_mgmt_zone[mgmt_zone_name])):

                if key == app_mgmt_zone[mgmt_zone_name][i].entityId:
                  app_mgmt_zone[mgmt_zone_name][i].consumption = app_mgmt_zone[mgmt_zone_name][i].consumption + consumption_details[key]
                  app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * multiplying_factor)
                  break

      except Exception as e:
        logger.exception("Exception while running populate_consumption ", str(e), exc_info=True)
        
      finally:
        logger.info("Execution completed populate_consumption")
        return app_mgmt_zone
   
    #------------------------------------------------------------------------
    # Author: Nikhil Goenka
    # Function to categorize the applications as per management zone 
    #------------------------------------------------------------------------
    def populate_ddu_consumption(self, ddu_mgmt_zone, availability_mgmt_zone):
      try:
          logger.info("In populate_ddu_consumption")
          ddu_consumption_mgmt_zone = {}
          ddu_consumption = self.dtApiV2GetQuery(DDU_ENTITY_CONSUMPTION)

          try:
            if (len(ddu_consumption['result'])) > 0:
              entity_list = ddu_consumption['result'][0]['data']

              for item in entity_list:
                  entity = item['dimensions'][0]

                  try:
                      mz = ddu_mgmt_zone[entity] 
                  except KeyError:
                      ddu_mgmt_zone, availability_mgmt_zone = self.push_entity(ddu_mgmt_zone, availability_mgmt_zone, entity)

                  try:
                      ddu_consumption_mgmt_zone[mz] = ddu_consumption_mgmt_zone[mz] + item['values'][0]

                  except KeyError:
                      ddu_consumption_mgmt_zone[mz] = 0.0
                      ddu_consumption_mgmt_zone[mz] = ddu_consumption_mgmt_zone[mz] + item['values'][0]

          except KeyError:
             logger.info("Found no records in DDU consumption") 
             pass 
         
      except Exception as e:
          logger.exception("Exception while running populate_ddu_consumption  " ,str(e))

      finally:
          logger.info("Successful execution: populate_ddu_consumption")
          return ddu_mgmt_zone, availability_mgmt_zone, ddu_consumption_mgmt_zone 
  
    # ********************************************************************************************************
    #        Function to populate host_consumption, dem and ddu as per management zones, host groups
    # ********************************************************************************************************

    def populate_management_zone_consumption(self, entityID, split_data, split_host_group_data, availability_mgmt_zone, ddu_mgmt_zone, app_mgmt_zone):
        try: 
          logger.info("In populate_management_zone_consumption")
          
          ###
          total_host_group_units = 0.0
          hosts = self.dtApiQuery(INFRA_API)

          for host in hosts:
            logger.info(host)
            try:
              key = split_data[host['entityId']]
            except KeyError:
              logger.info("New host added : calling populate_host_cache", host['entityId'])
              split_data, split_host_group_data = self.populate_host_cache(split_data, split_host_group_data, host)

          """
           Fetching applications
          """
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  DEM_UNITS_CONSUMPTION, 1)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  DEM_UNITS_CONSUMPTION_WO_REPLAY, 0.25)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  DEM_USR_PROP, 0.01)

          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  MOBILE_APP_REPLAY, 1)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  MOBILE_APP_WO_REPLAY, 0.25)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  MOBILE_USR_PROP, 0.01)

          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  CUSTOM_UNITS_CONSUMPTION, 0.25)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  CUSTOM_USR_PROP, 0.01)

          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  SYN_BILLING_API, 1, 1)
          app_mgmt_zone = self.populate_consumption(self.app_mgmt_zone,  HTTP_BILLING_API, 0.1, 2)

          """
            Fetching DDU Consumption
          """
          #Commenting this as enabling DDUs to split per management zone results in multiple API calls which potentially 
          #can impact any automation suites that use API calls as there is a limit of number of API calls/min. So, uncomment it accordingly. 
          #if self.get_mgmt_zone_data == True:
          #  ddu_mgmt_zone, availability_mgmt_zone, ddu_consumption_mgmt_zone = self.populate_ddu_consumption(ddu_mgmt_zone, availability_mgmt_zone)

          # Pushing the data per management zone
          if (self.get_mgmt_zone_data == "Yes"):
            metric=""

            for key in self.app_mgmt_zone.keys():
                metric += "consumption.demUnits,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(self.app_mgmt_zone[key][0].consumption) + "\n" 
            self.dtApiIngestMetrics(INGEST_METRICS,metric)

            tmp_dic = {}
            metric = ""
            for key in split_data.keys():
                mgmt_zone = split_data[key].mgmt_zone

                for val in split_data.keys():
                  if split_data[val].mgmt_zone == mgmt_zone:
                    try:  
                      tmp_dic[mgmt_zone] = tmp_dic[mgmt_zone] + split_data[key].host_units 
                    except KeyError:
                      tmp_dic[mgmt_zone] = split_data[val].host_units
                    break 

            ## Pushing metrics in database
            for key in tmp_dic.keys():
                metric += "consumption.hostUnits,mgmt_zone=\"" + key + "\",dt.entity.custom_device=" + entityID + " " + str(tmp_dic[key]) + "\n"
            self.dtApiIngestMetrics(INGEST_METRICS,metric)

            ### Pushing ddu metrics in database
            #Commenting this as enabling DDUs to split per management zone results in multiple API calls which potentially 
            #can impact any automation suites that use API calls as there is a limit of number of API calls/min. So, uncomment it accordingly. 
            #metric = ""
            #for key in ddu_consumption_mgmt_zone.keys():
            #    metric += "consumption.ddus,mgmt_zone=\"" + key + "\",dt.entity.custom_device=" + entityID + " "  + str(ddu_consumption_mgmt_zone[key]) + "\n"
            #self.dtApiIngestMetrics(INGEST_METRICS,metric)

          # Pushing the data per host group
          if (self.get_hu_hostgroup_data == "Yes"):
            metric=""

            tmp_dic = {}
            for key in split_host_group_data.keys():
                mgmt_zone = split_host_group_data[key].mgmt_zone

                for val in split_host_group_data.keys():
                  if split_host_group_data[val].mgmt_zone == mgmt_zone:
                    try: 
                      tmp_dic[mgmt_zone] = tmp_dic[mgmt_zone] + split_host_group_data[key].host_units
                    except KeyError:
                      tmp_dic[mgmt_zone] = split_host_group_data[val].host_units     
                    break 

            ## Pushing metrics in database
            for key in tmp_dic.keys():
                metric += "consumption.hostUnits,host_group=\"" + key + "\",dt.entity.custom_device=" + entityID + " " + str(tmp_dic[key]) + "\n"
  
            self.dtApiIngestMetrics(INGEST_METRICS,metric)

        except Exception as e:
          logger.exception("Exception encountered in populate_management_zone_consumption: ", str(e))  

        finally:
          logger.info("Succesfully executed populate_management_zone_consumption")  
          return ddu_mgmt_zone

    # ********************************************************************************************************
    #        Function to initialize the csv file which will be dumped as logs 
    # ********************************************************************************************************
    def initialize_csv_header(self):
        try:
          logger.info("In initialize_csv_header")  

          csv_data = ""
          csv_data="dt.entity.custom_device,Endpoint Name,status,management.zone,Problem ID,Problem Link,problem.title,impact.level,severity.level,RCA or no RCA, MTTR(in hours)\n"

        except Exception as e:
          logger.exception("Exception encountered in initialize_csv_header: ", str(e))  

        finally:
          logger.info("Succesfully executed initialize_csv_header")  
          return csv_data 

    # ********************************************************************************************************
    #        Function to slice and dice problem trend and push metrics 
    # ********************************************************************************************************
    def slice_and_dice_problem_trend(self, logger, csv_data):
       try:
           logger.info("In slice_and_dice_problem_trend")
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
               key = (timestamp.year, timestamp.month, row["problem.title"], row["management.zone"],row["dt.entity.custom_device"])
               if key not in result:
                   result[key] = {"count": 0, "downtime": []}
               result[key]["count"] += 1
               result[key]["downtime"].append(float(row["mttr"]))
           
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

           for item in result_data:
               metric += "incidents.seen,dt.entity.custom_device=\"" + item['entityId'] + "\"" + ",year="+ str(item['year']) + ",month=" + str(item['month']) + ",problem_title=\"" + str(item['column_value']) + "\",mgmt_zone=\"" + str(item['zone']) + "\" " + str(item['count']) + "\n"
               metric_downtime += "downtime,dt.entity.custom_device=\"" + item['entityId'] + "\"" + ",year="+ str(item['year']) + ",month=" + str(item['month']) + ",problem_title=\"" + str(item['column_value']) + "\",downtime=" + str(item['downtime']) + ",mgmt_zone=\"" + str(item['zone']) + "\" " + str(item['downtime']) + "\n"

           self.dtApiIngestMetrics(INGEST_METRICS,metric)

           logger.info(metric_downtime)
           self.dtApiIngestMetrics(INGEST_METRICS,metric_downtime)

       except Exception as e:
          logger.exception("Exception encountered slice_and_dice_problem_trend" + str(e))

       finally:
          logger.info("Successful execution: slice_and_dice_problem_trend")

    # ********************************************************************************************************
    #        Function to populate problem metrics
    # ********************************************************************************************************
    def populate_problem_data(self, entityID, data, detailed_prb_data, problems_mgmt_zone, ag_endpoint, endpoint):
        try:
          logger.info("In populate_problem_data")  

          mean_rsp_time=[]
          median_rsp_time = 0
          total_prb_resolved = 0
          total_number_of_prb = 0 
          detailed_prb_data.total_prb = len(data)
          csv_data = self.initialize_csv_header()
          csv_data_list = []
          #Data that we will dump to log file so it can be retrieved (where logV2 is disabled)
          logger_csv_data = ""
          logger_csv_data="dt.entity.custom_device,Endpoint Name,status,management.zone,Problem ID,Problem Link,starttime,endtime,problem.title,impact.level,severity.level,RCA or no RCA,mttr\n"


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
              total_prb_resolved = total_prb_resolved + 1
              resolution_time = end_time - start_time
              
              if int(resolution_time) >= int(self.converted_to_incident_duration): 
                total_incident_reported = total_incident_reported + 1
                #Management Zone
                key = ""

                try:
                  zones = data[i]['managementZones']

                  if len(zones) is not 0:
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
                    obj = RemoteInsightifyExtension.problem_mgmt_zone()
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

                   csv_data = csv_data + entityID + "," + endpoint + ",INFO,\"" + key + "\"," + data[i]["displayId"] + "," + self.url[:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",rca," + str(resolution_time/3600000) + "\n"
                   logger_csv_data = logger_csv_data + entityID + "," + endpoint + ",INFO,\"" + key + "\"," + data[i]["displayId"] + "," + self.url[:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + str(int(start_time/1000)) + "," + str(end_time/1000) + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",rca," + str(resolution_time/3600000) + "\n"

                else:   
                   total_mttr_wo_rca.append(resolution_time)
                   incidents_wo_rca = incidents_wo_rca + 1 
                   problems_mgmt_zone[key].mttr_wo_rca_list.append(resolution_time)

                   #Check the length of csv_data since we have a limitation of allowing a string of only 5000 characters
                   if (csv_data.count('\n') >= 400):
                     csv_data_list.append(csv_data)
                     csv_data = self.initialize_csv_header()

                   csv_data = csv_data + entityID + "," + endpoint + ",INFO,\"" +  key + "\"," + data[i]["displayId"] + "," + self.url[:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",no_rca,"+str(resolution_time/3600000)+"\n"
                   logger_csv_data = logger_csv_data + entityID + "," + endpoint + ",INFO,\"" +  key + "\"," + data[i]["displayId"] + "," + self.url[:-7] + "#problems/problemdetails;gf=all;pid=" + data[i]["problemId"] + "," + str(int(start_time/1000)) + "," + str(end_time/1000) + "," + data[i]["title"] + "," + data[i]["impactLevel"] + "," + data[i]["severityLevel"] + ",no_rca,"+str(resolution_time/3600000)+"\n"
                mean_rsp_time.append(resolution_time)
                severity = data[i]["severityLevel"]

                if severity == "AVAILABILITY":
                  detailed_prb_data.availability = detailed_prb_data.availability + 1
                  problems_mgmt_zone[key].availability += 1

                elif severity == "PERFORMANCE":
                  detailed_prb_data.performance = detailed_prb_data.performance + 1
                  problems_mgmt_zone[key].performance += 1

                elif severity == "ERROR":
                 detailed_prb_data.error_event = detailed_prb_data.error_event + 1
                 problems_mgmt_zone[key].error += 1

                elif severity == "RESOURCE_CONTENTION":
                  detailed_prb_data.resource = detailed_prb_data.resource + 1
                  problems_mgmt_zone[key].resource += 1

                elif severity == "CUSTOM_ALERT":
                  detailed_prb_data.custom_alert = detailed_prb_data.custom_alert + 1
                  problems_mgmt_zone[key].custom += 1

                impact_level = data[i]["impactLevel"]
                if impact_level == "SERVICES":
                  detailed_prb_data.service = detailed_prb_data.service + 1 
                  problems_mgmt_zone[key].service += 1

                elif impact_level == "APPLICATION":
                  detailed_prb_data.application = detailed_prb_data.application + 1
                  problems_mgmt_zone[key].application += 1

                elif impact_level == "INFRASTRUCTURE":
                 detailed_prb_data.infrastructure = detailed_prb_data.infrastructure + 1
                 problems_mgmt_zone[key].infrastructure += 1

                elif impact_level == "ENVIRONMENT":
                  detailed_prb_data.environment = detailed_prb_data.environment + 1

          for key in problems_mgmt_zone.keys():
              metric = ""
              logger.info("populating metrics for -> {}".format(key))
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
              if self.get_problem_data_mgmt_zone == "Yes":
                metric += "total_reported_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].problems) + "\n"
                metric += "root_cause,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].rootCause) + "\n"
                metric += "reported_availability_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].availability) + "\n"
                metric += "reported_performance_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].performance) + "\n"
                metric += "reported_resource_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].resource) + "\n"
                metric += "reported_custom_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].custom) + "\n"
                metric += "reported_service_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].service) + "\n"
                metric += "reported_infra_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].infrastructure) + "\n"
                metric += "reported_application_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].application) + "\n"
                metric += "reported_error_problems,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].error) + "\n"
                metric += "mttr_with_rca,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].mttr_rca) + "\n"
                metric += "mttr_wo_rca,mgmt_zone=\"" + key + "\"" + ",dt.entity.custom_device=" + entityID + " " + str(problems_mgmt_zone[key].mttr_wo_rca) + "\n"

                self.dtApiIngestMetrics(INGEST_METRICS,metric)

          if (self.get_problem_data_mgmt_zone == "Yes"):
              metric = ""
              import time
              now = time.time()

              #Insert epoch time at the time of last record being inserted
              metric += "record_insertion_time" + ",dt.entity.custom_device=" + entityID + " " + str(now) + "\n"
             
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

              #Insert the total incidents reported 
              metric += "total_incident_reported" + ",dt.entity.custom_device=" + entityID + " " + str(total_incident_reported) + "\n"
              metric += "total_incidents_with_rca" + ",dt.entity.custom_device=" + entityID + " " + str(incidents_with_rca) + "\n"
              metric += "total_incidents_wo_rca" + ",dt.entity.custom_device=" + entityID + " " + str(incidents_wo_rca) + "\n"
              metric += "total_mttr_rca" + ",dt.entity.custom_device=" + entityID + " " + str(mttr_rca) + "\n"
              metric += "total_mttr_wo_rca" + ",dt.entity.custom_device=" + entityID + " " + str(mttr_wo_rca) + "\n"

              self.dtApiIngestMetrics(INGEST_METRICS,metric)

              #Once data is pushed, set next collection interval accordingly
              if self.prb_report_date == "Last 30 days":
                self.problem_time_interval = (30*1440) - 1
              elif self.prb_report_date == "Last 60 days":
                self.problem_time_interval = (60*1440) - 1
              elif self.prb_report_date == "Last 90 days":
                self.problem_time_interval  = (90*1440) - 1
              else:
                self.problem_time_interval  = (365*1440) - 1
              
          #Find the median response time and convert it to minutes (from microseconds)
          try:
            median_rsp_time = ((sum(mean_rsp_time)/len(mean_rsp_time)))/60000
          except ZeroDivisionError:
            median_rsp_time = 0

        except Exception as e:
          logger.exception("Exception encountered populate_problem_data" + str(e))

        finally:
          logger.info("Successful execution: populate_problem_data")
          logger.info("Pushing the problem data in logs")
          logger.info(logger_csv_data)

          self.slice_and_dice_problem_trend(logger,logger_csv_data)

          # Get the endpoint from ag_enpoint
          if ag_endpoint != "":
            #Push the latest csv_data   
            csv_data_list.append(csv_data)  

            for csv_data in csv_data_list:
              reader = csv.DictReader(io.StringIO(csv_data))
              json_data = json.dumps(list(reader))

              query = ag_endpoint + "/logs/ingest"
              self.dtApiV2PushLogs(query,json_data)

          return detailed_prb_data, median_rsp_time, problems_mgmt_zone

    # ********************************************************************************************************
    #        Function to create PG for the extension 
    # ********************************************************************************************************
    def get_group_name(self):
        return "Insightify"

    # ********************************************************************************************************
    #        Function to check if the extension is running 
    # ********************************************************************************************************
    def get_state_metric(self):
        if self.state_iterations >= self.state_interval * 3:
            self.state_iterations = 0
        state = RemoteInsightifyExtension.State(int(self.state_iterations / self.state_interval))
        self.state_iterations = self.state_iterations + 1
        return state.name

    # *******************************************************************************    
    #           Function to post data using API v2 endpoint
    # *******************************************************************************    
              
    def dtApiV2PushLogs(self, query, payload):
      try:    
        logger.info("In dtApiV2PushLogs")
                
        data = {}
        post_param = {'Accept':'application/json','Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = payload, verify=False)
        logger.info(query)
                
        if populate_data.status_code == 401:
          msg = "Auth Error"
          logger.exception("Auth Error dtApiV2PushLogs: ")
              
      except Exception as e:
        logger.exception("Exception in dtApiV2PushLogs" + str(e))
                
      finally:  
        logger.info(populate_data)
        logger.info("Succesfully completed dtApiV2PushLogs")

    # *******************************************************************************    
    #           Function to get data using API v1 endpoint
    # *******************************************************************************    
    def dtApiQuery(self, endpoint):
      try:
        logger.info("In dtApiQuery")
        data = {}
    
        query = str(self.url) + endpoint 
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json() 
    
        elif populate_data.status_code == 401:
          msg = "Auth Error" 
    
      except Exception as e:
        logger.exception("Exception encountered dtApiQuery", str(e))  
    
      finally:
        logger.info("Successful execution: dtApiQuery")
        return data

    # *******************************************************************************
    #           Function for configuration API for publish tenant
    # *******************************************************************************
    def dtConfApiv1(self, endpoint):
      try:
        logger.info("In dtConfApiv1")
        data = {}

        url = self.confurl
        url = url.replace("v1","config/v1")
        url = url.replace("v2","config/v1")

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)
        logger.info(populate_data.status_code)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception encountered in dtConfApiv1 ", str(e))

      finally:
        logger.info("Execution completed dtConfApiv1 ")
        return data

    # *******************************************************************************    
    #           Function for configuration API for pulling data
    # *******************************************************************************    
    def dtConfApi(self, endpoint):
      try:
        logger.info("In dtConfApi")  
        data = {}

        url = self.url
        url = url.replace("v1","config/v1")

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception encountered in dtConfApi ", str(e))  

      finally:
        logger.info("Execution completed dtConfApi ")  
        return data

    # *******************************************************************************    
    #           Function to get data using API v2 endpoint
    # *******************************************************************************    
    def dtApiV2Query(self, logger, endpoint):
      try:
        logger.info("In dtApiV2Query")
        data = {}
        v2_url = self.url

        v2_url = v2_url.replace("v1","v2")
        query = v2_url + "metrics/query?metricSelector=" + endpoint + DEM_RELATIVE_TIMESTAMP 
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}

        populate_data = requests.get(query, headers = get_param, verify=False)
        logger.info(query)
        logger.info(str(populate_data.status_code))

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.info("Encountered exception:", str(e))

      finally:
        logger.info("Execution completed dtApiV2Query")  
        return data

    # **********************************************************************************    
    #           Function to extract billed DEM consumption
    # **********************************************************************************    
    def extract_billed_consumption(self, logger, data, multiplying_fac):
      try:
          logger.info("In extract_billed_consumption")
          consumption = 0

          if data is not None:
            if len(data) > 0:
              apps = data['result'][0]['data']
              consumption = 0

              for billing in apps:
                dimensions = billing['dimensions']
                if dimensions[1] == "Billed":
                  consumption = consumption + billing['values'][0]

          consumption = float(consumption * multiplying_fac)

      except Exception as e:
        logger.exception("Exception encountered in extract_billed_consumption",str(e))

      finally:
        logger.info("Completed execution in extract_billed_consumption")
        return consumption

    # **********************************************************************************    
    #           Function to pull data ad categorize consumption data as per mgmt zone
    # **********************************************************************************    
    def pull_consumption_data(self, logger, host_consumption, consumed_dem_units, ddu_units, mgmt_zone_sliced_data):
      try:
          logger.info("In pull_consumption_data")
          data = self.dtApiV2Query(logger, DDU_CONSUMPTION)
          logger.info(data) 

          if data is not None:
            consumed_ddu_units = 0.0
            consumed_dem_units = 0.0

            if len(data) > 0:
             if len(data['result'][0]['data']) > 0:
               ddu_units = (data['result'][0]['data'][0]['values'][0] * 0.1)

          data = self.dtApiV2Query(logger, DEM_UNITS_CONSUMPTION)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 1.0))
          logger.info("consumed_dem_units(DEM_WITH_REPLAY): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, DEM_USR_PROP)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.01))
          logger.info("consumed_dem_units(DEM_USR_PROP): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, MOBILE_APP_REPLAY)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 1.0))
          logger.info("consumed_dem_units(MOBILE_APP_REPLAY): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, MOBILE_APP_WO_REPLAY)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.25))
          logger.info("consumed_dem_units(MOBILE_APP_WO_REPLAY): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, MOBILE_USR_PROP)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.01))
          logger.info("consumed_dem_units(MOBILE_USR_PROP): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, CUSTOM_USR_PROP)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.01))
          logger.info("consumed_dem_units(DEM_WITH_REPLAY): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, DEM_UNITS_CONSUMPTION_WO_REPLAY)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.25))
          logger.info("After consumed_dem_units(DEM_UNITS_CONSUMPTION_WO_REPLAY): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, SYN_BILLING_API)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 1.0))
          logger.info("After consumed_dem_units(SYN_BILLING_API): " + str(consumed_dem_units))

          data = self.dtApiV2Query(logger, HTTP_BILLING_API)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.1))
          logger.info("After consumed_dem_units(HTTP_BILLING_API): " + str(consumed_dem_units))
               
          data = self.dtApiV2Query(logger, CUSTOM_UNITS_CONSUMPTION)
          consumed_dem_units = consumed_dem_units + float(self.extract_billed_consumption(logger, data, 0.25))
          logger.info("After consumed_dem_units(CUSTOM_UNITS_CONSUMPTION): " + str(consumed_dem_units))
    
          data = self.dtApiV2Query(logger ,HOST_CONNECTED_CONSUMPTION)
          if len(data) > 0:
           if len(data['result'][0]['data']) > 0:
             host_consumption = data['result'][0]['data'][0]['values'][0]

      except Exception as e:
        logger.exception("Exception encountered in pull_consumption_data",str(e))

      finally:
        logger.info("Completed execution in pull_consumption_data")  
        return  host_consumption, consumed_dem_units, ddu_units, mgmt_zone_sliced_data 

    # **********************************************************************************    
    #           Function to pull data ad categorize consumption data as per mgmt zone
    # **********************************************************************************    
    def pull_ff_data(self, logger, topology_device, mgmt_zone_sliced_data):
      try:
          logger.info("In pull_ff_data")
          data = self.dtConfApi(ALERTING_PRF_API)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.alerting_profile = len(data['values'])
          logger.info("Alerting Profile: "+ str(mgmt_zone_sliced_data.alerting_profile))

          data = self.dtApiQuery(PROCESS_GROUP)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.process_group = len(data)
          logger.info("Process-Group: " + str(len(data)))

          data = self.dtConfApi(TAGS)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.tag = len(data['values'])
          logger.info("Tags: "+ str(mgmt_zone_sliced_data.tag))

          data = self.dtConfApi(MGMT_ZONES_API)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.configured_mgmt_zones = len(data['values'])
          logger.info("Mgmt Zone: "+ str(mgmt_zone_sliced_data.configured_mgmt_zones))

          data = self.dtConfApi(PROBLEM_NOTIFICATIONS)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.problem_notification = len(data['values'])
          logger.info("Problem Notification: "+ str(mgmt_zone_sliced_data.problem_notification))

          data = self.dtConfApi(REQ_ATTRIBUTES)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.request_attribute = len(data['values'])
          logger.info("Request Attribute: "+ str(mgmt_zone_sliced_data.request_attribute))

          data=self.dtApiQuery(KEY_REQUESTS)
          if data is not None:
           if len(data) > 0:
              mgmt_zone_sliced_data.key_requests = (data['values'][0][0])
          logger.info("Key Requests: "+ str(mgmt_zone_sliced_data.key_requests))

          data=self.dtApiQuery(SESS_PROP)
          if data is not None:
           if len(data) > 0:
              mgmt_zone_sliced_data.session_properties = (data['values'][0][0])
          logger.info("Session Property: "+ str(mgmt_zone_sliced_data.session_properties))

          data = self.dtApiQuery(CONVERSION_GOALS)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.conversion_goals = (data['values'][0][0])
          logger.info("Conversion Goals: "+ str(mgmt_zone_sliced_data.conversion_goals))

          data = self.dtApiQuery(SESSION_REPLAY)
          if data is not None:
           if len(data) > 0:
             mgmt_zone_sliced_data.session_replay = (data['values'][0][0])
          logger.info("Session Replay: "+ str(mgmt_zone_sliced_data.session_replay))

          mgmt_zone_sliced_data = self.push_ff_data(logger, topology_device, mgmt_zone_sliced_data)

      except Exception as e:
        logger.exception("Exception encountered in pull_ff_data ",str(e))

      finally:
        logger.info("Completed execution in pull_ff_data")  
        return mgmt_zone_sliced_data

