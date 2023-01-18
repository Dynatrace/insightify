"use strict";(self.webpackChunkdt_adoptionoverview_extension=self.webpackChunkdt_adoptionoverview_extension||[]).push([[852],{3905:(e,t,n)=>{n.d(t,{Zo:()=>d,kt:()=>h});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},i=Object.keys(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var p=a.createContext({}),l=function(e){var t=a.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},d=function(e){var t=l(e.components);return a.createElement(p.Provider,{value:t},e.children)},m="mdxType",c={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},u=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,i=e.originalType,p=e.parentName,d=s(e,["components","mdxType","originalType","parentName"]),m=l(n),u=r,h=m["".concat(p,".").concat(u)]||m[u]||c[u]||i;return n?a.createElement(h,o(o({ref:t},d),{},{components:n})):a.createElement(h,o({ref:t},d))}));function h(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=n.length,o=new Array(i);o[0]=u;var s={};for(var p in t)hasOwnProperty.call(t,p)&&(s[p]=t[p]);s.originalType=e,s[m]="string"==typeof e?e:r,o[1]=s;for(var l=2;l<i;l++)o[l]=n[l];return a.createElement.apply(null,o)}return a.createElement.apply(null,n)}u.displayName="MDXCreateElement"},2018:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>o,default:()=>m,frontMatter:()=>i,metadata:()=>s,toc:()=>l});var a=n(7462),r=(n(7294),n(3905));const i={sidebar_position:2},o="Get Started",s={unversionedId:"get-started",id:"get-started",title:"Get Started",description:"What is Insightify Extension?",source:"@site/docs/get-started.md",sourceDirName:".",slug:"/get-started",permalink:"/insightify/docs/get-started",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/get-started.md",tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"tutorialSidebar",previous:{title:"Introduction",permalink:"/insightify/docs/intro"},next:{title:"Guides",permalink:"/insightify/docs/Guides"}},p={},l=[{value:"What is Insightify Extension?",id:"what-is-insightify-extension",level:3},{value:"How does it work?",id:"how-does-it-work",level:3},{value:"Features?",id:"features",level:3},{value:"Extension installation and configuration",id:"extension-installation-and-configuration",level:2}],d={toc:l};function m(e){let{components:t,...i}=e;return(0,r.kt)("wrapper",(0,a.Z)({},d,i,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"get-started"},"Get Started"),(0,r.kt)("h3",{id:"what-is-insightify-extension"},"What is Insightify Extension?"),(0,r.kt)("p",null,"Insightify Extension is an activeGate extension that is developed to pull and report key metrics. It leverages Dynatrace APIs to pull the metrics from the configured tenant. It will enable your customer to get a single pane of all the different health metrics in the tenant itself highlighting some of the usage and adoption features in Dynatrace."),(0,r.kt)("h3",{id:"how-does-it-work"},"How does it work?"),(0,r.kt)("p",null,"End-user uploads the extension on an activeGate and configure the endpoint. Once configured, they will start receiving the data and the data would be available a dashboard for that endpoint.",(0,r.kt)("br",{parentName:"p"}),"\n",(0,r.kt)("img",{alt:"extension-workflow",src:n(7073).Z,width:"2372",height:"1330"})),(0,r.kt)("h3",{id:"features"},"Features?"),(0,r.kt)("p",null,"The extension reports the following set of metrics:",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"License Consumption Insight:")," highlighting the current usage of DEM, DDUs, Host Units, Host Units.",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"Environment Feature flags:")," The extension would report on the different feature flags that are currently being used in the environment (like Request attributes, Alerting\nprofiles. etc.)",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"Problem Details:")," this section would report on the MTTR, and the total number of problems received in the environment in the past month.",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"Problem by Severity and Impacted Entities"),": Dynatrace received problems classified by different severity along with the different entities (like Environment, Services, etc.)",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"License consumption by management zone:")," This section will highlight the license utilization by management zone (once enabled).",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"License consumption by host group:")," This section will highlight the license utilization by host groups (once enabled).",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"Problem by management zones:")," This section, if enabled, will report problem data like MTTR, RCA availability, etc. sliced per management zone.",(0,r.kt)("br",{parentName:"p"}),"\n","\xb7 ",(0,r.kt)("strong",{parentName:"p"},"Benefit Value Realisation:")," This section will generate a report on the time spent on problems generated by Dynatrace, the cost spent towards it and the potential savings (once enabled).  "),(0,r.kt)("h2",{id:"extension-installation-and-configuration"},"Extension installation and configuration"),(0,r.kt)("ol",null,(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Find the extension from ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/Dynatrace/insightify/blob/main/extension/custom.remote.python.insightify.zip"},"here"),"  ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Download to get the extension ZIP file. ",(0,r.kt)("strong",{parentName:"p"},"Don't rename the file."),"  ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Unzip the ZIP file to the ",(0,r.kt)("inlineCode",{parentName:"p"},"plugin_deployment")," (found at ",(0,r.kt)("inlineCode",{parentName:"p"},"/opt/dynatrace/remotepluginmodule/plugin_deployment/"),") directory of your ActiveGate host.  ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"In the Dynatrace menu, go to ",(0,r.kt)("strong",{parentName:"p"},"Settings > Monitored technologies > Custom extensions and select Upload Extension."),"  ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Upload the ZIP file.  ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Upload the zip file to the activeGate where you plan to run the extension from at ``. ")),(0,r.kt)("li",{parentName:"ol"},(0,r.kt)("p",{parentName:"li"},"Enter the following endpoint information for pulling data:  "),(0,r.kt)("p",{parentName:"li"},"   ",(0,r.kt)("strong",{parentName:"p"},"Endpoint name"),": Any label to identify this connection. It is used for identification purposes.\n",(0,r.kt)("strong",{parentName:"p"},"Tenant URL"),":    Tenant endpoint that you'd like to pull data from. Configure it as ",(0,r.kt)("inlineCode",{parentName:"p"},"https://abc.live.dynatrace.com/api/v1/"),(0,r.kt)("br",{parentName:"p"}),"\n","Replace abc with the tenant UUID for SaaS while for managed, configure the endpoint as ",(0,r.kt)("inlineCode",{parentName:"p"},"https://managed-server/e/environment-endpoint/api/v1"),(0,r.kt)("br",{parentName:"p"}),"\n","",(0,r.kt)("strong",{parentName:"p"},"Tenant Token"),": Token that will be used to pull the data from the configured tenant. Make sure your token has the following permissions:  "),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},"                 1. Read problems (API v1)  \n                 2. Read problems (API v2)  \n                 3. User session query language (API v1)  \n                 4. CaptureRequestData (API v1)  \n                 5. Read metrics (API v2)  \n")),(0,r.kt)("p",{parentName:"li"},(0,r.kt)("strong",{parentName:"p"},"Publish URL"),":     Tenant where you would like to push the pulled metrics. Configure it as ",(0,r.kt)("inlineCode",{parentName:"p"},"http://xyz.live.dynatrace.com/api/v2/"),(0,r.kt)("br",{parentName:"p"}),"\n","Replace abc with the tenant UUID for SaaS while for managed, configure the endpoint as ",(0,r.kt)("inlineCode",{parentName:"p"},"https://managed-server/e/environment-endpoint/api/v1"),(0,r.kt)("br",{parentName:"p"}),"\n",(0,r.kt)("strong",{parentName:"p"},"Publish Token"),":   Token that will be used to push the metrics. Make sure your token has the following permissions:  "),(0,r.kt)("pre",{parentName:"li"},(0,r.kt)("code",{parentName:"pre"},"                 1. Write config (Configuration API v1): To create a dashboard with the captured metrics.  \n                 2. Read config (Configuration API v1) : Permission to access to verify if the dashboard is already created.  \n                 3. Ingest Metrics (API v2): Permissions to push the host units, DEM units into Dynatrace.  \n                 4. Read Metrics (API v2): Permissions to read the metrics.  \n                 5. Ingest Logs (API v2): An Optional field to allow pushing the problem data retrieved as logs.  \n")),(0,r.kt)("p",{parentName:"li"},(0,r.kt)("strong",{parentName:"p"},"Capture consumption data per management zone"),":        Set the flag to ",(0,r.kt)("strong",{parentName:"p"},"Yes")," in order to pull host units/DEM consumption metrics and slice it as per management zones.",(0,r.kt)("br",{parentName:"p"}),"\n",(0,r.kt)("strong",{parentName:"p"},"Capture host units consumption data per host groups"),": Set the flag to ",(0,r.kt)("strong",{parentName:"p"},"Yes")," in order to pull host units consumption metrics and slice it as per host groups.",(0,r.kt)("br",{parentName:"p"}),"\n",(0,r.kt)("strong",{parentName:"p"},"Capture and report problem data"),":                     Set the configuration to ",(0,r.kt)("strong",{parentName:"p"},"Yes")," to pull problem data like MTTR, problem details, etc.",(0,r.kt)("br",{parentName:"p"}),"\n",(0,r.kt)("strong",{parentName:"p"},"Capture and report adoption data"),":                    Set the configuration to ",(0,r.kt)("strong",{parentName:"p"},"Yes")," to pull adoption data.  "))),(0,r.kt)("p",null,"`"))}m.isMDXComponent=!0},7073:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/Health-extension-5c75b324b5400755cb82254009faaeed.png"}}]);