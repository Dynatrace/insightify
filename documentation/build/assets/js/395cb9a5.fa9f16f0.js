"use strict";(self.webpackChunkdt_adoptionoverview_extension=self.webpackChunkdt_adoptionoverview_extension||[]).push([[649],{3905:(e,t,a)=>{a.d(t,{Zo:()=>d,kt:()=>h});var n=a(7294);function i(e,t,a){return t in e?Object.defineProperty(e,t,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[t]=a,e}function r(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,n)}return a}function o(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?r(Object(a),!0).forEach((function(t){i(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):r(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}function l(e,t){if(null==e)return{};var a,n,i=function(e,t){if(null==e)return{};var a,n,i={},r=Object.keys(e);for(n=0;n<r.length;n++)a=r[n],t.indexOf(a)>=0||(i[a]=e[a]);return i}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(n=0;n<r.length;n++)a=r[n],t.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(i[a]=e[a])}return i}var s=n.createContext({}),p=function(e){var t=n.useContext(s),a=t;return e&&(a="function"==typeof e?e(t):o(o({},t),e)),a},d=function(e){var t=p(e.components);return n.createElement(s.Provider,{value:t},e.children)},m="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return n.createElement(n.Fragment,{},t)}},c=n.forwardRef((function(e,t){var a=e.components,i=e.mdxType,r=e.originalType,s=e.parentName,d=l(e,["components","mdxType","originalType","parentName"]),m=p(a),c=i,h=m["".concat(s,".").concat(c)]||m[c]||u[c]||r;return a?n.createElement(h,o(o({ref:t},d),{},{components:a})):n.createElement(h,o({ref:t},d))}));function h(e,t){var a=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var r=a.length,o=new Array(r);o[0]=c;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l[m]="string"==typeof e?e:i,o[1]=l;for(var p=2;p<r;p++)o[p]=a[p];return n.createElement.apply(null,o)}return n.createElement.apply(null,a)}c.displayName="MDXCreateElement"},4315:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>s,contentTitle:()=>o,default:()=>m,frontMatter:()=>r,metadata:()=>l,toc:()=>p});var n=a(7462),i=(a(7294),a(3905));const r={sidebar_position:3},o="Guides",l={unversionedId:"Guides",id:"Guides",title:"Guides",description:"Extension installation and configuration",source:"@site/docs/Guides.md",sourceDirName:".",slug:"/Guides",permalink:"/insightify/docs/Guides",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/Guides.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Get Started",permalink:"/insightify/docs/get-started"},next:{title:"Quick Links",permalink:"/insightify/docs/Quick-Links"}},s={},p=[{value:"Extension installation and configuration",id:"extension-installation-and-configuration",level:2},{value:"Configurables",id:"configurables",level:4},{value:"Look around",id:"look-around",level:3},{value:"Grail enabled Dashboards",id:"grail-enabled-dashboards",level:2}],d={toc:p};function m(e){let{components:t,...r}=e;return(0,i.kt)("wrapper",(0,n.Z)({},d,r,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h1",{id:"guides"},"Guides"),(0,i.kt)("h2",{id:"extension-installation-and-configuration"},"Extension installation and configuration"),(0,i.kt)("ol",null,(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Find the ca.pem certificate for the extension ",(0,i.kt)("a",{parentName:"p",href:"https://github.com/Dynatrace/insightify/blob/main/src/EF2.0/secrets/ca.pem"},"here"),".",(0,i.kt)("br",{parentName:"p"}),"\n","1.1 Upload certificate to tenant by following steps as below \ud83e\ude9c"),(0,i.kt)("pre",{parentName:"li"},(0,i.kt)("code",{parentName:"pre"},"From the navigation menu, select Manage > Credential vault.  \nSelect Add new credential.  \nFor Credential type, select Public Certificate.  \nAdd a meaningful Credential name.  \nUpload the Root certificate file (ca.pem).  \nSelect Save.  \n")),(0,i.kt)("p",{parentName:"li"},"1.2 Uploading certificate on ActiveGate(s):",(0,i.kt)("br",{parentName:"p"}),"\n","Similarly, upload the generated certificate (ca.pem) on all the AGs that you plan to run the extension from. Upload the certificate to location ",(0,i.kt)("inlineCode",{parentName:"p"},"/var/lib/dynatrace/remotepluginmodule/agent/conf/certificates/")," within AG.  ")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Once the certificate has been uploaded, download the extension bundle zip from ",(0,i.kt)("a",{parentName:"p",href:"https://github.com/Dynatrace/insightify/blob/main/releases/EF2.0/1.0/bundle.zip"},"here"),"  ")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Download to get the extension ZIP file. ",(0,i.kt)("strong",{parentName:"p"},"Don't rename the file."),"  ")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Upload the ZIP file on Dynatrace. ")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Enter the following endpoint information for pulling data:"),(0,i.kt)("ul",{parentName:"li"},(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Configuration name:")," A label to identify this connection. It is used for identification purposes."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Tenant URL:")," The tenant endpoint from which you want to pull data. Configure it as ",(0,i.kt)("inlineCode",{parentName:"li"},"https://abc.live.dynatrace.com/api/v1/"),', replacing "abc" with the tenant UUID for SaaS. For managed environments, configure it as ',(0,i.kt)("inlineCode",{parentName:"li"},"https://managed-server/e/environment-endpoint/api/v1/"),"."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Tenant Token:")," The token used to pull data from the configured tenant. Ensure your token has the following scopes:",(0,i.kt)("ul",{parentName:"li"},(0,i.kt)("li",{parentName:"ul"},"Read problems (API v2)"))),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Publish URL:")," The tenant where you'd like to push the pulled metrics. Configure it as ",(0,i.kt)("inlineCode",{parentName:"li"},"http://xyz.live.dynatrace.com/api/v2/"),', replacing "abc" with the tenant UUID for SaaS. For managed environments, configure it as ',(0,i.kt)("inlineCode",{parentName:"li"},"https://managed-server/e/environment-endpoint/api/v2/"),"."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Publish Token:")," The token used to push metrics. Ensure your token has the following permissions:",(0,i.kt)("ul",{parentName:"li"},(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Write config (Configuration API v1):")," To create a dashboard with the captured metrics."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Read config (Configuration API v1):")," Permission to verify if the dashboard is already created."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Ingest Metrics (API v2):")," Permissions to push the host units and DEM units into Dynatrace."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Read Metrics (API v2):")," Permissions to read the metrics."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Ingest Logs (API v2) (Optional):")," Allows pushing the retrieved problem data as logs.")))))),(0,i.kt)("ol",null,(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Within Dynatrace, navigate to ",(0,i.kt)("strong",{parentName:"p"},"Settings >> Monitored technologies >> Custom extensions")," tab",(0,i.kt)("br",{parentName:"p"}),"\n",(0,i.kt)("img",{alt:"upload-extension",src:a(2701).Z,width:"3572",height:"1820"}))),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Open ",(0,i.kt)("inlineCode",{parentName:"p"},"Insightify")," and configure it.",(0,i.kt)("br",{parentName:"p"}),"\n",(0,i.kt)("img",{alt:"configure-extension",src:a(2177).Z,width:"3210",height:"1836"})))),(0,i.kt)("h4",{id:"configurables"},"Configurables"),(0,i.kt)("ul",null,(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Endpoint name:")," The name that you want to refer the endpoint with.  "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Tenant URL:")," The tenant URL you would like to fetch data from.  "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Tenant Token:")," Token generated with access to read metrics, access problems, and events. For details on how to generate the token, refer to ",(0,i.kt)("a",{parentName:"li",href:"https://www.dynatrace.com/support/help/shortlink/token"},"this help link"),".  "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Tenant Config Token:")," Token generated with permissions to ",(0,i.kt)("inlineCode",{parentName:"li"},"ingest metrics, read metrics, ingest logs (optional), and read/write configuration"),".   "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Capture and report problem data per management:")," Flag to pull problem data and report it per management zone in a dashboard named ",(0,i.kt)("inlineCode",{parentName:"li"},"Insightify Incident Report"),". The default value is ",(0,i.kt)("strong",{parentName:"li"},"Yes"),".  "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Push problem details as logs:")," Configure to push problem details as logs. If configured, the endpoint will push problem details via the ",(0,i.kt)("inlineCode",{parentName:"li"},"/ingest/logs")," API. By default, this feature is disabled."),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Duration (in mins) when a problem is treated as an incident:")," The time before a problem is considered an incident. Default value is 30 mins.   "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Capture and Generate Problem Report Data:")," Select the time period for generating problem data from options like every 1 day, 30 days, 60 days, 180 days, or annually. The frequency affects data consumption; more frequent pulls provide better insights, while less frequent pulls reduce data points and consumption.  "),(0,i.kt)("li",{parentName:"ul"},(0,i.kt)("strong",{parentName:"li"},"Management Zone Name:")," Configure the management zone from which you want to pull data. By default, it pulls data from all management zones.  ")),(0,i.kt)("ol",{start:3},(0,i.kt)("li",{parentName:"ol"},'Once configured, the extension will start successfully. It should display an "OK" status.')),(0,i.kt)("blockquote",null,(0,i.kt)("p",{parentName:"blockquote"},"The extension may take a few minutes to initialize on the first run.")),(0,i.kt)("h3",{id:"look-around"},"Look around"),(0,i.kt)("p",null,". Multiple dashboards will be created (depending on your configuration) for each endpoint, offering a quick view of each.",(0,i.kt)("br",{parentName:"p"}),"\n","",(0,i.kt)("img",{alt:"dashboard-view-2",src:a(891).Z,width:"1788",height:"920"}),(0,i.kt)("br",{parentName:"p"}),"\n","",(0,i.kt)("img",{alt:"dashboard-view-3",src:a(1330).Z,width:"1444",height:"947"}),"   "),(0,i.kt)("h2",{id:"grail-enabled-dashboards"},"Grail enabled Dashboards"),(0,i.kt)("p",null,"For Grail dashboards, download the dashboards from ",(0,i.kt)("a",{parentName:"p",href:"https://github.com/Dynatrace/insightify/blob/main/GrailDashboards/1.0/"},"here"),".",(0,i.kt)("br",{parentName:"p"}),"\n","To upload (import) the JSON definition of a dashboard from the Dashboards table  "),(0,i.kt)("ol",null,(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Go to Dashboards. ")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"In the Dashboards panel on the left, select  All dashboards.",(0,i.kt)("br",{parentName:"p"}),"\n","A Dashboards table displays all dashboards by Name and Last modified date.")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"In the upper-left corner of the page, select  Upload.")),(0,i.kt)("li",{parentName:"ol"},(0,i.kt)("p",{parentName:"li"},"Find and open the dashboard JSON definition file."))),(0,i.kt)("p",null,"To upload (import) the JSON definition of a dashboard from the Dashboards side panel\nIn the Dashboards app, in the Dashboards panel on the left, select  Upload.\nOpen the dashboard JSON definition file you downloaded. Repeat for all the dashboards."))}m.isMDXComponent=!0},1330:(e,t,a)=>{a.d(t,{Z:()=>n});const n=a.p+"assets/images/Benefits_Realisation_Report-fe1b850a809582867788d0ba8f8cf36b.gif"},891:(e,t,a)=>{a.d(t,{Z:()=>n});const n=a.p+"assets/images/Incident_Report-28a5d58e0c5e320475d1f6c4fc52d8f6.gif"},2701:(e,t,a)=>{a.d(t,{Z:()=>n});const n=a.p+"assets/images/Upload_health_extension-c9ad9678bc3ec49956d627ad686d4d0c.jpg"},2177:(e,t,a)=>{a.d(t,{Z:()=>n});const n=a.p+"assets/images/extension-config-page-f324142b6241504d40e2cb8d739c628f.jpg"}}]);