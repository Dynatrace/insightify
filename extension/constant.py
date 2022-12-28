#HOST license APIs
HOST_CONNECTED_CONSUMPTION="dsfm%3Abilling.hostunit.connected%3Afold%28%29"
HOST_UNITS_CONSUMPTION="entity/infrastructure/hosts?includeDetails=true%28%29"
INFRA_API = 'entity/infrastructure/hosts?relativeTime=hour&includeDetails=true'

#DEM License APIs
DEM_UNITS_CONSUMPTION="builtin%3Abilling.apps.web.sessionsWithReplayByApplication:fold%28%29"
CUSTOM_UNITS_CONSUMPTION="builtin%3Abilling.apps.custom.sessionsWithoutReplayByApplication:fold%28%29"
DEM_UNITS_CONSUMPTION_WO_REPLAY="builtin%3Abilling.apps.web.sessionsWithoutReplayByApplication:fold%28%29"
DEM_USR_PROP="builtin%3Abilling.apps.web.userActionPropertiesByApplication:fold%28%29"
CUSTOM_USR_PROP="builtin%3Abilling.apps.custom.userActionPropertiesByDeviceApplication:fold%28%29"
MOBILE_APP_WO_REPLAY="builtin%3Abilling.apps.mobile.sessionsWithoutReplayByApplication:fold%28%29"
MOBILE_APP_REPLAY="builtin%3Abilling.apps.mobile.sessionsWithReplayByApplication:fold%28%29"
MOBILE_USR_PROP="builtin%3Abilling.apps.mobile.userActionPropertiesByMobileApplication:fold%28%29"
SYN_BILLING_API = "builtin%3Abilling.synthetic.actions%3Afold%28%29"
HTTP_BILLING_API = "builtin%3Abilling.synthetic.requests%3Afold%28%29"
DEM_RELATIVE_TIMESTAMP="&from=now-1h"

#DDU License APIs
DDU_CONSUMPTION ="builtin%3Abilling.ddu.metrics.total:fold%28%29"
DDU_ENTITY_DETAILS="entities"
DDU_ENTITY_CONSUMPTION ="metrics/query?metricSelector=builtin%3Abilling.ddu.metrics.byEntity:fold%28%29&entitySelector=type%28%22custom_device%22%29"

#Feature Flag APIs
TAGS="autoTags"
TOKENS="tokens"
ALERTING_PRF_API = "alertingProfiles"
PROCESS_GROUP="entity/infrastructure/process-groups?includeDetails=true"
NAMING_RULES="service/requestNaming"
MGMT_ZONES_API="managementZones"
PROBLEM_NOTIFICATIONS="notifications"
SPECIFIC_PROBLEM_NOTIFICATION="notifications/ID"
REQ_ATTRIBUTES="service/requestAttributes"
NOTIFICATIONS="notifications"
DASHBOARDS="dashboards"
GET_EXISTING_DASHBOARD="dashboards?owner=dynatraceone%40dynatrace.com"
KEY_REQUESTS="userSessionQueryLanguage/table?query=SELECT count(DISTINCT(useraction.name)) FROM useraction where useraction.internalKeyUserActionId IS NOT NULL and startTime >= $NOW - DURATION(\"7d\")"
CONVERSION_GOALS="userSessionQueryLanguage/table?query=SELECT count(distinct(usersessionId)) FROM usersession WHERE ((matchingConversionGoals IS NOT NULL OR useraction.matchingConversionGoals IS NOT NULL)) and startTime >= $NOW - DURATION(\"7d\")"
SESSION_REPLAY="userSessionQueryLanguage/table?query=SELECT count(DISTINCT(userSessionId)) FROM usersession WHERE (hasSessionReplay=true) and startTime >= $NOW - DURATION(\"7d\")"
SESS_PROP="userSessionQueryLanguage/table?query=select COUNT(DISTINCT(useraction.name)) from useraction where userActionPropertyCount > 1 and startTime >= $NOW - DURATION(\"7d\")"
FETCH_APPLICATIONS = "entity/applications?includeDetails=true"
FETCH_SYN_APPLICATIONS = "synthetic/monitors"
INGEST_METRICS = "metrics/ingest"

#PROBLEMS API
PROBLEMS="problems?pageSize=1&from=-2h"
SPECIFIC_PROBLEMS="problems?pageSize=50&from=1661990400000&to=1664582400000&problemSelector=managementZones%28%22Workflow%20%26%20Automation%22%29"
ONLY_PROBLEMS="problems?pageSize=500&from=1661990400000&to=1664582400000"
TEST_PROBLEMS="problems?pageSize=1&from=-2h"
ANOMALY_DETECTION="anomalyDetection/metricEvents"
