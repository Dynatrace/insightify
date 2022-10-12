COMMENTCOLLECT_CONSUMPTION_DATA=60
COMMENTCOLLECT_PROBLEM_DATA=1440
COMMENTCOLLECT_FF_DATA=10080
COLLECT_CONSUMPTION_DATA=1
COLLECT_PROBLEM_DATA=1
COLLECT_FF_DATA=1
HOST_CONNECTED_CONSUMPTION="dsfm%3Abilling.hostunit.connected%3Afold%28%29"
HOST_UNITS_CONSUMPTION="entity/infrastructure/hosts?includeDetails=true%28%29"
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
ALERTING_PRF_API = "alertingProfiles"
DDU_CONSUMPTION ="builtin%3Abilling.ddu.metrics.total:fold%28%29"
DDU_ENTITY_DETAILS="entities"
DDU_ENTITY_CONSUMPTION ="metrics/query?metricSelector=builtin%3Abilling.ddu.metrics.byEntity:fold%28%29&entitySelector=type%28%22custom_device%22%29"
PROCESS_GROUP="entity/infrastructure/process-groups?includeDetails=true"
TAGS="autoTags"
NAMING_RULES="service/requestNaming"
MGMT_ZONES_API="managementZones"
PROBLEM_NOTIFICATIONS="notifications"
SPECIFIC_PROBLEM_NOTIFICATION="notifications/ID"
TOKENS="tokens"
REQ_ATTRIBUTES="service/requestAttributes"
PROBLEMS="problem/feed?relativeTime=day"
ANOMALY_DETECTION="anomalyDetection/metricEvents"
NOTIFICATIONS="notifications"
DASHBOARDS="dashboards"
GET_EXISTING_DASHBOARD="dashboards?owner=dynatraceone%40dynatrace.com"
KEY_REQUESTS="userSessionQueryLanguage/table?query=SELECT count(DISTINCT(useraction.name)) FROM useraction where useraction.internalKeyUserActionId IS NOT NULL and startTime >= $NOW - DURATION(\"7d\")"
CONVERSION_GOALS="userSessionQueryLanguage/table?query=SELECT count(distinct(usersessionId)) FROM usersession WHERE ((matchingConversionGoals IS NOT NULL OR useraction.matchingConversionGoals IS NOT NULL)) and startTime >= $NOW - DURATION(\"7d\")"
SESSION_REPLAY="userSessionQueryLanguage/table?query=SELECT count(DISTINCT(userSessionId)) FROM usersession WHERE (hasSessionReplay=true) and startTime >= $NOW - DURATION(\"7d\")"
SESS_PROP="userSessionQueryLanguage/table?query=select COUNT(DISTINCT(useraction.name)) from useraction where userActionPropertyCount > 1 and startTime >= $NOW - DURATION(\"7d\")"
INFRA_API = 'entity/infrastructure/hosts?relativeTime=hour&includeDetails=true'
TIMESERIES_API="timeseries/com.dynatrace.builtin:host.availability?includeData=true&&relativeTime=60mins"
FETCH_APPLICATIONS = "entity/applications?includeDetails=true"
FETCH_SYN_APPLICATIONS = "synthetic/monitors"
INGEST_METRICS = "metrics/ingest"
POST_SLO="slo"
GET_SLO="slo?sloSelector=name%28%22Host%20Units%20Consumption%20-%20Health%20Device%22%29&sort=name&timeFrame=CURRENT&pageIdx=1&demo=false&evaluate=false&enabledSlos=true"
PAYLOAD_SLO_HU={"enabled": "true", "name": "Host Units Consumption - Health Device", "customDescription": "Host consumption per day", "metricExpression": "(100) * (tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,host_units))):splitBy():sum:auto:sort(value(sum,descending)))/(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,host_allocation))):splitBy():avg:auto:sort(value(avg,descending)))", "evaluationType": "AGGREGATE", "filter": "type(\"CUSTOM_DEVICE\")", "target": 95, "warning": 97.5, "timeframe": "-1d", "useRateMetric": "true", "metricNumerator": "tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,host_units))):splitBy():sum:auto:sort(value(sum,descending))", "metricDenominator": "(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,host_allocation))):splitBy():avg:auto:sort(value(avg,descending)))" }
PAYLOAD_SLO_DEM={"enabled": "true", "name": "DEM Units Consumption - Health Device", "customDescription": "DEM consumption per day", "metricExpression": "(100) * (tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,dem_units))):splitBy():sum:auto:sort(value(sum,descending)))/(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,dem_allocation))):splitBy():avg:auto:sort(value(avg,descending)))", "evaluationType": "AGGREGATE", "filter": "type(\"CUSTOM_DEVICE\")", "target": 95, "warning": 97.5, "timeframe": "-1d", "useRateMetric": "true", "metricNumerator": "tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,dem_units))):splitBy():sum:auto:sort(value(sum,descending))", "metricDenominator": "(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,dem_allocation))):splitBy():avg:auto:sort(value(avg,descending)))" }
PAYLOAD_SLO_DDU={"enabled": "true", "name": "David Data Units Consumption - Health Device", "customDescription": "DDU consumption per day", "metricExpression": "(100) * (tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,ddu_units))):splitBy():sum:auto:sort(value(sum,descending)))/(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,ddu_allocation))):splitBy():avg:auto:sort(value(avg,descending)))", "evaluationType": "AGGREGATE", "filter": "type(\"CUSTOM_DEVICE\")", "target": 95, "warning": 97.5, "timeframe": "-1d", "useRateMetric": "true", "metricNumerator": "tech.dt_health_check_extn.databases.license_consumption:filter(and(eq(table_name,ddu_units))):splitBy():sum:auto:sort(value(sum,descending))", "metricDenominator": "(tech.dt_health_check_extn.databases.allocated_data:filter(and(eq(table_name,ddu_allocation))):splitBy():avg:auto:sort(value(avg,descending)))" }
PAYLOAD_CUSTOM_METRIC_HU={
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "Mock-version"
  },
  "metricId": "tech.dt_health_check_extn.host_units",
  "name": "Host-unit consumption SLO breach",
  "description": "Host-Unit consumption has exceeded the SLO.",
  "aggregationType": "AVG",
  "severity": "CUSTOM_ALERT",
  "enabled": "true",
  "disabledReason": "NONE",
  "warningReason": "NONE",
  "alertingScope": [
    {
      "filterType": "CUSTOM_DEVICE_GROUP_NAME",
      "nameFilter": {
        "value": "Dynatrace Health Metrics",
        "operator": "EQUALS"
      }
    }
  ],
  "monitoringStrategy": {
    "type": "STATIC_THRESHOLD",
    "samples": 60,
    "violatingSamples": 1,
    "dealertingSamples": 60,
    "alertCondition": "ABOVE",
    "alertingOnMissingData": "false",
    "threshold": 80,
    "unit": "COUNT"
  },
  "alertCondition": "ABOVE",
  "samples": 60,
  "violatingSamples": 1,
  "dealertingSamples": 60,
  "threshold": 80,
  "unit": "COUNT",
  "eventType": "CUSTOM_ALERT"
}
PAYLOAD_CUSTOM_METRIC_DEM={
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "Mock-version"
  },
  "metricId": "tech.dt_health_check_extn.dem_units",
  "name": "DEM units consumption SLO breach",
  "description": "DEM-Unit consumption has exceeded the targetted SLO.",
  "aggregationType": "AVG",
  "severity": "CUSTOM_ALERT",
  "enabled": "true",
  "disabledReason": "NONE",
  "warningReason": "NONE",
  "alertingScope": [
    {
      "filterType": "CUSTOM_DEVICE_GROUP_NAME",
      "nameFilter": {
        "value": "Dynatrace Health Metrics",
        "operator": "EQUALS"
      }
    }
  ],
  "monitoringStrategy": {
    "type": "STATIC_THRESHOLD",
    "samples": 60,
    "violatingSamples": 1,
    "dealertingSamples": 60,
    "alertCondition": "ABOVE",
    "alertingOnMissingData": "false",
    "threshold": 80,
    "unit": "COUNT"
  },
  "alertCondition": "ABOVE",
  "samples": 60,
  "violatingSamples": 1,
  "dealertingSamples": 60,
  "threshold": 80,
  "unit": "COUNT",
  "eventType": "CUSTOM_ALERT"
}
PAYLOAD_CUSTOM_METRIC_DDU={
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "Mock-version"
  },
  "metricId": "tech.dt_health_check_extn.ddu_units",
  "name": "DDUs consumption SLO breach",
  "description": "DDU consumption has exceeded the SLO.",
  "aggregationType": "AVG",
  "severity": "CUSTOM_ALERT",
  "enabled": "true",
  "disabledReason": "NONE",
  "warningReason": "NONE",
  "alertingScope": [
    {
      "filterType": "CUSTOM_DEVICE_GROUP_NAME",
      "nameFilter": {
        "value": "Dynatrace Health Metrics",
        "operator": "EQUALS"
      }
    }
  ],
  "monitoringStrategy": {
    "type": "STATIC_THRESHOLD",
    "samples": 60,
    "violatingSamples": 1,
    "dealertingSamples": 60,
    "alertCondition": "ABOVE",
    "alertingOnMissingData": "false",
    "threshold": 80,
    "unit": "COUNT"
  },
  "alertCondition": "ABOVE",
  "samples": 60,
  "violatingSamples": 1,
  "dealertingSamples": 60,
  "threshold": 80,
  "unit": "COUNT",
  "eventType": "CUSTOM_ALERT"
}
POST_ALERTING_PROFILE="alertingProfiles"
PAYLOAD_ALERTING_PROFILE= {
  "metadata": {
    "currentConfigurationVersions": [
      "7.0.3"
    ],
    "configurationVersions": [],
    "clusterVersion": "Current-version"
  },
  "displayName": "Health-device Custom Alert",
  "rules": [
    {
      "severityLevel": "CUSTOM_ALERT",
      "tagFilter": {
        "includeMode": "NONE",
        "tagFilters": []
      },
      "delayInMinutes": 0
    }
  ],
  "managementZoneId": "null",
  "eventTypeFilters": [
    {
      "customEventFilter": {
        "customTitleFilter": {
          "enabled": "true",
          "value": "Health-Device",
          "operator": "CONTAINS",
          "negate": "false",
          "caseInsensitive": "true"
        }
      }
    }
  ]
}
PAYLOAD_NOTIFICATIONS={ "type": "EMAIL", "name": "Health-device Emailing List", "alertingProfile": "", "active": "true", "subject": "{State} Problem {ProblemID}: {ImpactedEntity}", "body": "{ProblemDetailsHTML}", "receivers": [ "cusotmer@company.com" ], "ccReceivers": [ "csm.email@dynatrace.com", "ps.email@dynatrace.com" ], "bccReceivers": [] } 
