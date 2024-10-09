---
sidebar_position: 3
---

# Quick Links

### License and bill of materials

Extension would lead to DDU consumption. A fully configured endpoint would consume **300 DDUs** a month for about **15 management zones**. For more details on DDU consumption, refer to [help link](https://www.dynatrace.com/support/help/shortlink/metric-cost-calculation).

For Grail-enabled dashboards, the DQL fetching problem data does not incur charges, however, any JS on the dashboard will be charged as per the [rate card](https://www.dynatrace.com/pricing/rate-card/).  

### How long does it take for data to reflect?

#### Problem Data and Application Data

The key feature flags will be pulled once the **Capture problem data per management zone** is set to **Yes**. The problem metrics are updated as per the **Capture and Generate Problem Report Data** To identify last run time of Insightify, use “record_insertion_time” metric. The latest value of that metric would indicate the last time (in epoch) data was inserted in Dynatrace.  
![record-insertion](record_insertion_time.jpg)   

