---
sidebar_position: 1
---

# Get Started

### What is Dynatrace Health Tool Extension?

Dynatrace Health Tool Extension is an activeGate extension that is developed to pull and report key metrics. It leverages Dynatrace APIs to pull the metrics from the configured tenant. It will enable your customer to get a single pane of all the different health metrics in the tenant itself highlighting some of the usage and adoption features in Dynatrace.

### How does it work?

End-user uploads the extension on an activeGate and configure the endpoint. Once configured, they will start receiving the data and the data would be available a dashboard for that endpoint.  
![extension-workflow](Health-extension.png)

### Features?

The extension reports the following set of metrics:  
· **License Consumption Insight:** highlighting the current usage of DEM, DDUs, Host Units, Host Units.  
· **Environment Feature flags:** The extension would report on the different feature flags that are currently being used in the environment (like Request attributes, Alerting
profiles. etc.)  
· **Problem Details:** this section would report on the MTTR, and the total number of problems received in the environment in the past month.  
· **Problem by Severity and Impacted Entities**: Dynatrace received problems classified by different severity along with the different entities (like Environment, Services, etc.)  
· **License consumption by management zone:** This section will highlight the license utilization by management zone (once enabled).  
· **License consumption by host group:** This section will highlight the license utilization by host groups (once enabled).
