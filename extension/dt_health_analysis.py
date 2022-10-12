import math
import json
import logging
import requests
from enum import Enum
from constant import *
from pprint import pprint
from dynatrace import Dynatrace
from pathlib import Path
from random import randrange
from ruxit.api.data import PluginProperty
from ruxit.api.base_plugin import RemoteBasePlugin

logger = logging.getLogger(__name__)

class RemoteDTHealthReportExtension(RemoteBasePlugin):

    class split_consumption:
        def __init__(self):
          self.dem_units = 0
          self.ddu_units = 0
          self.host_units = 0
          self.mgmt_zone = 0

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
              logger.debug(host)

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
                obj = RemoteDTHealthReportExtension.split_consumption()
                obj.mgmt_zone = mgtzone
                obj.host_units = host['consumedHostUnits']
                split_data[host['entityId']] = obj 

              if hostGroup not in hostGroup_splitdata.keys():
                obj = RemoteDTHealthReportExtension.split_consumption()
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
              obj = RemoteDTHealthReportExtension.split_consumption()
              obj.host_units = host['consumedHostUnits']
              obj.mgmt_zone = mgtzone
              split_data[host['entityId']] = obj 

            if hostGroup not in hostGroup_splitdata.keys():
              obj = RemoteDTHealthReportExtension.split_consumption()
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
         logger.debug("In push_entity " + entity)
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
             logger.debug("Found no records in DDU consumption") 
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
          appInfo = RemoteDTHealthReportExtension.app()
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
        traceback.print_exc()
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
          appInfo = RemoteDTHealthReportExtension.app()
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
        traceback.print_exc()
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

            self.get_mgmt_zone_data = self.config.get("get_mgmt_zone_data", "False")
            self.get_hu_hostgroup_data = self.config.get("get_hu_hostgroup_data", "False")
            self.get_problem_data = self.config.get("get_problem_data", "Yes")
            self.get_ff_data = self.config.get("get_ff_data", "Yes")
            self.confurl = self.config.get("confurl","https://push.live.dynatrace.com/api/v2/")
            self.conf_password = self.config.get("conftoken", "Token")
          
            self.consumption_data_iterations = 0
            self.pull_prb_data_iterations = 0
            self.ff_data_iterations = 0
            self.state_iterations = 0
            self.host_consumption = 0
            self.dem_consumption = 0
            self.ddu_consumption = 0

            self.dashboard_created = 0
            #dictionary to maintain mapping of EC2 availability zone with management zones useful for DDUs 
            self.availability_mgmt_zone = {}

            #dictionary to maintain mapping of entities with management zones used for DDUs 
            self.ddu_mgmt_zone={}

            self.split_data={}
            self.hostGroup_splitdata = {}
            self.app_mgmt_zone = {}

            if self.get_mgmt_zone_data == "Yes" or self.get_hu_hostgroup_data == "Yes":
                logger.debug("In initialize")

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
                

            #The section below is for SLOs and sending alerting. Currently, this is commented out because of some corner cases for SLOs

            #self.customer_alerting_profile = self.config.get("user_emailid", "abc@xyz.com")
            #self.ps_alerting_profile = self.config.get("ps_emailid", "abc@dynatrace.com")
            #self.csm_alerting_profile = self.config.get("csm_emailid", "csm@dynatrace.com")

            #self.alert_iterations = 0
            #self.event_iterations = 0
            #self.relative_iterations = 0
            #self.absolute_iterations = 0
            #check if SLO is created already -- will check only for one of the SLOs (can be improved to test each SLO)
            #data = self.dtApiV2GetQuery(GET_SLO)
            #if data is not None:
            #    if len(data) <= 0 and data['totalCount'] == 0:
            #       slo_list = []
            #       self.dtApiV2PostQuery(POST_SLO, PAYLOAD_SLO_HU)
            #       data = self.dtApiV2GetQuery(GET_SLO)
            #       print(data)
            #       slo_list.append(data["id"])

            #       data = self.dtApiV2PostQuery(POST_SLO, PAYLOAD_SLO_DDU)
            #       print(data)
            #       slo_list.append(data["id"])

            #       data = self.dtApiV2PostQuery(POST_SLO, PAYLOAD_SLO_DEM)
            #       print(data)
            #       slo_list.append(data["id"])

            #       ##check if alerting profile
            #       #self.dtApiV1PostQuery(ANOMALY_DETECTION, PAYLOAD_CUSTOM_METRIC_HU)
            #       #self.dtApiV1PostQuery(ANOMALY_DETECTION, PAYLOAD_CUSTOM_METRIC_DEM)
            #       #self.dtApiV1PostQuery(ANOMALY_DETECTION, PAYLOAD_CUSTOM_METRIC_DDU)

            #       #data = self.dtApiV1PostQuery(POST_ALERTING_PROFILE, PAYLOAD_ALERTING_PROFILE)
            #       #PAYLOAD_NOTIFICATIONS['alertingProfile']=data["id"]
            #       #PAYLOAD_NOTIFICATIONS['receivers']=[self.customer_alerting_profile]
            #       #PAYLOAD_NOTIFICATIONS['ccReceivers']=[self.ps_alerting_profile, self.csm_alerting_profile]

            #       data=self.dtApiV1PostQuery(NOTIFICATIONS, PAYLOAD_NOTIFICATIONS)
            #       PAYLOAD_DASHBOARD_D1_HEALTH_TOOL["tiles"][11]["assignedEntities"] = slo_list[1] 
            #       PAYLOAD_DASHBOARD_D1_HEALTH_TOOL["tiles"][12]["assignedEntities"] = slo_list[2] 
            #       PAYLOAD_DASHBOARD_D1_HEALTH_TOOL["tiles"][13]["assignedEntities"] = slo_list[3] 
                    #self.dtApiV1PostQuery(DASHBOARDS, PAYLOAD_DASHBOARD_D1_HEALTH_TOOL)
        except Exception as e:
            logger.exception("Exception while running initialize", str(e), exc_info=True)

        finally:
            logger.info("Successful execution initialize ")

    # *********************************************************************    
    #           Function to get metrics/SLO using API V2 endpoint
    # *********************************************************************    
    def dtApiV2GetQuery(self, endpoint):
      try:
        logger.debug("In dtApiV2GetQuery")  
        data = {}

        config_url = self.url
        config_url = config_url.replace("v1","v2")

        query = str(config_url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.debug("in dtApiV2GetQuery ", str(e))

      finally:
        logger.debug("In dtApiV2GetQuery")  
        return data

    # *******************************************************************************    
    #            Function to push metrics using Ingest Metrics endpoint
    #      This is pushed to ingest host,dem and ddu units per management zone 
    # *******************************************************************************    
    def dtApiIngestMetrics(self, endpoint, payload):
      try:
        logger.debug("In dtApiIngestMetrics ")
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v1","v2")

        query = str(config_url) + endpoint
        post_param = {'Content-Type':'text/plain;charset=utf-8', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = payload)
        logger.info(self.conf_password)
        logger.info(query)
        logger.info(populate_data)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception in dtApiIngestMetrics ", str(e))

      finally:
        logger.debug("Succesfully completed dtApiIngestMetrics")  
        return data

    # *******************************************************************************    
    #           Function to post data using API v2 endpoint
    # *******************************************************************************    

    def dtApiV2PostQuery(self, endpoint, payload):
      try:
        logger.debug("In dtApiV2PostQuery")  
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v1","v2")
        
        query = str(config_url) + endpoint
        post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        
        populate_data = requests.post(query, headers = post_param, data = json.dumps(payload))
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception in dtApiV2PostQuery " + str(e))

      finally:
        logger.debug("Succesfully completed dtApiV2PostQuery")  
        return data

    # *******************************************************************************    
    #           Function to post data using API v1 endpoint
    # *******************************************************************************    
    def dtApiV1PostQuery(self, endpoint, payload):
      try:
        logger.debug("In dtApiV1PostQuery")  
        data = {}

        config_url = self.confurl
        config_url = config_url.replace("v2","config/v1")
        
        query = str(config_url) + endpoint
        post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        populate_data = requests.post(query, headers=post_param, data=json.dumps(payload))
        logger.info(query)
        logger.info(populate_data)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.info("In dtApiV1PostQuery: " + str(e))  

      finally:
        logger.debug("Succesfully completed dtApiV1PostQuery")  

    # *******************************************************************************    
    #           Function to post data using API v1 endpoint
    # *******************************************************************************    
    def query(self, **kwargs):
        try:  
            logger.debug("In query function")
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

            #Pull problem data and other feature flags
            detailed_data = RemoteDTHealthReportExtension.mgmt_zone_data()
            detailed_prb_data = RemoteDTHealthReportExtension.problem_data()

            if self.consumption_data_iterations >= COLLECT_CONSUMPTION_DATA:
                # Collect consumption data after 60 mins
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

            if (self.get_problem_data == "Yes") and self.pull_prb_data_iterations >= COLLECT_PROBLEM_DATA:
                # Collect problem data after 1-day 
                self.pull_prb_data_iterations = 0
                detailed_prb_data = self.pull_prb_data(logger, topology_device, detailed_prb_data)
            else:
              self.pull_prb_data_iterations = self.pull_prb_data_iterations + 1 

            if (self.get_ff_data == "Yes") and self.ff_data_iterations >= COLLECT_FF_DATA:
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

    def pull_prb_data(self, logger, topology_device, detailed_prb_data):
        try:
          logger.debug("In pull_prb_data")
          data = self.dtApiQuery(PROBLEMS)

          if data is not None:
            if len(data) >= 0:
              detail_prb_data, mean_resolution_time = self.populate_metrics(data["result"]["problems"], detailed_prb_data)

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
           logger.debug("In push_ff_data")

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

        print(applications)
        if (len(applications)) > 0:
          apps = applications['result'][0]['data']
          for billing in apps:
            dimensions = billing['dimensions']
            if syn == 0:
              if dimensions[1] == "Billed":
                print(dimensions[0], " ",billing['values'][0])
                consumption_details[dimensions[0]] = billing['values'][0]
            elif syn >= 0:
                consumption_details[dimensions[0]] = billing['values'][0]
       
          for key in consumption_details.keys():
            for mgmt_zone_name in app_mgmt_zone.keys():
              for i in range(len(app_mgmt_zone[mgmt_zone_name])):

                if key == app_mgmt_zone[mgmt_zone_name][i].entityId:
                  app_mgmt_zone[mgmt_zone_name][i].consumption = app_mgmt_zone[mgmt_zone_name][i].consumption + consumption_details[key]
                  app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * multiplying_factor)
                  print(app_mgmt_zone[mgmt_zone_name][i].name, " ",app_mgmt_zone[mgmt_zone_name][i].type, " " ,app_mgmt_zone[mgmt_zone_name][i].consumption, " ", app_mgmt_zone[mgmt_zone_name][i].dem) 
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
             logger.debug("Found no records in DDU consumption") 
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
            logger.debug(host)
            try:
              key = split_data[host['entityId']]
            except KeyError:
              logger.debug("New host added : calling populate_host_cache", host['entityId'])
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
            print(metric)
            logger.debug(metric)
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
            logger.info(metric)

        except Exception as e:
          logger.exception("Exception encountered in populate_management_zone_consumption: ", str(e))  

        finally:
          logger.info("Succesfully executed populate_management_zone_consumption")  
          return ddu_mgmt_zone

    # ********************************************************************************************************
    #        Function to populate problem metrics
    # ********************************************************************************************************
    def populate_metrics(self, data, detailed_prb_data):
        try:
          logger.debug("In populate_metrics")  

          mean_rsp_time=[]
          median_rsp_time = 0
          total_prb_resolved = 0
          detailed_prb_data.total_prb = len(data)
          for i in range(len(data)):
            severity = data[i]["severityLevel"]

            if severity == "AVAILABILITY":
              detailed_prb_data.availability = detailed_prb_data.availability + 1 

            elif severity == "PERFORMANCE":
              detailed_prb_data.performance = detailed_prb_data.performance + 1

            elif severity == "ERROR":
             detailed_prb_data.error_event = detailed_prb_data.error_event + 1

            elif severity == "RESOURCE_CONTENTION":
              detailed_prb_data.resource = detailed_prb_data.resource + 1

            elif severity == "CUSTOM_ALERT":
              detailed_prb_data.custom_alert = detailed_prb_data.custom_alert + 1

            impact_level = data[i]["impactLevel"]
            if impact_level == "SERVICE":
              detailed_prb_data.service = detailed_prb_data.service + 1 
            elif impact_level == "APPLICATION":
              detailed_prb_data.application = detailed_prb_data.application + 1
            elif impact_level == "INFRASTRUCTURE":
             detailed_prb_data.infrastructure = detailed_prb_data.infrastructure + 1
            elif impact_level == "ENVIRONMENT":
              detailed_prb_data.environment = detailed_prb_data.environment + 1
            
            start_time = data[i]["startTime"]
            end_time = data[i]["endTime"]

            if end_time != -1:
              total_prb_resolved = total_prb_resolved + 1
              resolution_time = end_time - start_time
              mean_rsp_time.append(resolution_time)

          #Find the median response time and convert it to minutes (from microseconds)
          try:
            median_rsp_time = ((sum(mean_rsp_time)/len(mean_rsp_time)))/60000
          except ZeroDivisionError:
            median_rsp_time = 0

        except Exception as e:
          logger.exception("Exception encountered populate_metrics" + str(e))

        finally:
          logger.info("Successful execution: populate_metrics")
          return detailed_prb_data, median_rsp_time

    # ********************************************************************************************************
    #        Function to create PG for the extension 
    # ********************************************************************************************************
    def get_group_name(self):
        return "Dynatrace Tenant Health Metrics"

    # ********************************************************************************************************
    #        Function to check if the extension is running 
    # ********************************************************************************************************
    def get_state_metric(self):
        if self.state_iterations >= self.state_interval * 3:
            self.state_iterations = 0
        state = RemoteDTHealthReportExtension.State(int(self.state_iterations / self.state_interval))
        self.state_iterations = self.state_iterations + 1
        return state.name

    # *******************************************************************************    
    #           Function to get data using API v1 endpoint
    # *******************************************************************************    
    def dtApiQuery(self, endpoint):
      try:
        logger.info("In dtApiQuery")
        data = {}
    
        query = str(self.url) + endpoint 
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param)
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
        logger.debug("In dtConfApiv1")
        data = {}

        url = self.confurl
        url = url.replace("v1","config/v1")
        url = url.replace("v2","config/v1")

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.conf_password)}
        populate_data = requests.get(query, headers = get_param)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception encountered in dtConfApiv1 ", str(e))

      finally:
        logger.debug("Execution completed dtConfApiv1 ")
        return data

    # *******************************************************************************    
    #           Function for configuration API for pulling data
    # *******************************************************************************    
    def dtConfApi(self, endpoint):
      try:
        logger.debug("In dtConfApi")  
        data = {}

        url = self.url
        url = url.replace("v1","config/v1")

        query = str(url) + endpoint
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}
        populate_data = requests.get(query, headers = get_param)
        logger.info(query)

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()
        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.exception("Exception encountered in dtConfApi ", str(e))  

      finally:
        logger.debug("Execution completed dtConfApi ")  
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
        query = v2_url + "metrics/query?metricSelector=" + endpoint + "&from=now-1h"
        get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.password)}

        populate_data = requests.get(query, headers = get_param)
        logger.info(query)
        logger.info(str(populate_data.status_code))

        if populate_data.status_code >=200 and populate_data.status_code <= 400:
          data = populate_data.json()

        elif populate_data.status_code == 401:
          msg = "Auth Error"

      except Exception as e:
        logger.debug("Encountered exception:", str(e))

      finally:
        logger.debug("Execution completed dtApiV2Query")  
        return data

    # **********************************************************************************    
    #           Function to extract billed DEM consumption
    # **********************************************************************************    
    def extract_billed_consumption(self, logger, data, multiplying_fac):
      try:
          logger.info("In extract_billed_consumption")

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

