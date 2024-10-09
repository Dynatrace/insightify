---
sidebar_position: 2
---

# Get Started

### What is Insightify?
Insightify is a reference tool designed to assist in optimizing observability practices and achieving the desired outcomes of adopting Dynatrace as an observability platform. Its purpose is to help all stakeholders align and refine implementations, driving continuous improvement in the digital transformation journey.

### Insightify Services

**Extension:**  
Managed customers can leverage Insightify as an ActiveGate extension. The extension can be configured to pull key metrics and generate reports by leveraging Dynatrace APIs to collect metrics from the configured tenant.

**Grail-Enriched Dashboards:**  
SaaS customers can utilize Insightify dashboards. These dashboards can be uploaded to generate actionable reports and identify trends by using DQL to pull data from the Grail Data Lake.

While the reports generated from both the Extension and Grail-Enriched Dashboards are similar, the latter provides smaller granularity and better flexibility.

### How Does It Work?

#### For Extension Users:
- End-users upload the `ca.pem` certificate to an ActiveGate and upload the extension.
- Once configured, Insightify collects data from the tenant and generates reports on the configured dashboard.

![extension-workflow](Health-extension.jpg)

#### For Grail Dashboards Users:
- End-users can upload the provided dashboard JSON files to start viewing data as documented [here](#).


### Features

Insightify provides the following dashboards, catering to both technical personas and application teams. These dashboards are designed to enhance efficiency and spotlight how Dynatrace's Davis AI can drive faster issue resolution, reducing the need for war rooms and enabling cost savings. The three key dashboards are:

- **Incident Report:**  
  This dashboard offers insights into Mean Time to Resolution (MTTR) and the total number of problems received in the environment during a configured interval.

- **MTTR Snapshot and Incident Analysis:**  
  This dashboard delves into incident analysis, identifying areas for optimization by focusing on MTTR, incident counts, or both.

- **Benefit Value Realization:**  
  This dashboard generates a report detailing the time spent on resolving problems detected by Dynatrace, the associated costs, and potential savings.

