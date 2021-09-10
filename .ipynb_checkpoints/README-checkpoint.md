# Description of the Project
---
> *under construction*


This project is a part of an [TÜBİTAK 1501](https://www.tubitak.gov.tr/en/funds/industry/national-support-programmes/content-1501-industrial-rd-projects-grant-programme) project titled "*Konum verisi ile ulaşım analiz, planlama ve modelleme için büyük veri platformu geliştirilmesi*" (EN: Developing a big data platform for transportation analysis, planning and modelling with geodata)

## Contents

- [Raw Data](#raw-data)
- [Scope of the Project](#scope-of-the-project)
- [Processing the Data](#processing-the-data)
  - [Map-Matching](#map-matching)
  - [Transformation and Filtering](#transformation-and-filtering)
- [Finding](#findings)

##  Scope of the Project

For selected time interval and space; gather the data, process it then predict travel times accurately. Since the data streams in real-time, create predictive models such that it can consider real-time data and update itself.
Also, for academic purposes, any valuable research are welcomed. Currently, optimization of network topology (space discretization) for the accurate travel time prediction is being investigated.

For the sake of simplicity, 75km-long corridor between Polatlı and Ankara city center is selected as a study space and raw data extracted for this corridor. Also, for now, research is being conducted with one month data (December, 2019).

## Raw Data

Raw data can be seen from this [toy dataset](https://raw.githubusercontent.com/kkocamaz/GPS_transport/main/input_data/08_00-10_00-non-duplicated.csv). The toy dataset contains data for only 2 hours duration for the selected corridor. Further, raw data for a randomly selected vehicle can see from the following figure.

![Raw Data Figure](figs/readme/raw_data.png)

Also, to be representative, a small portion of the toy dataset is shown in the below as table:

| Vehicle ID | Latitude | Longitude | Timestamp |
| ----------- | ----------- | ----------- | ----------- |
| 53bar9d | 32.539734 | 39.799667 | 2019-11-18 09:51:50
| 53bar9d | 32.539894 | 39.799858 | 2019-11-18 09:51:54
| 53o445 | 32.812416 | 39.91264 | 2019-11-18 08:22:53
| 53o445 | 32.811195 | 39.912209 | 2019-11-18 08:23:01
| 53o445 | 32.811035 | 39.912163 | 2019-11-18 08:23:02
| 53o445 | 32.807163 | 39.911324 | 2019-11-18 08:24:14
| 53s66da | 32.785725 | 39.908211 | 2019-11-18 09:07:01
| 53s66da | 32.785458 | 39.9081 | 2019-11-18 09:07:05


Also, in addition to raw GPS data from the vehicles ([Floating Car Data](https://en.wikipedia.org/wiki/Floating_car_data)), spatial discretization of the studied corridor is adopted from readily avaiable [OpenStreetMap](https://www.openstreetmap.org/) network topology. In this study, spatial discretization of the network topology is mentioned as *segments*.

The corridor space has divided into 655 segments wiwth varying length and segments are consecutive and continuous i.e. end point of a segment has the same latitude and longitude with start point of consecutive segment as shown in the figure for both directions. Segment length are calculated by using [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula).

![Segment Figure](figs/readme/segments.png)



| Segment ID | Start Node | End Node | startLat | startLon | endLat | endLon | dir | calc_length |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| 314 | 1397577716 | 308843810 | 39.5762323 | 32.1447012 | 39.575895 | 32.1439933 | 1 | 71.33302995 |
| 315 | 308843810 | 308843811 | 39.575895 | 32.1439933 | 39.5754417 | 32.1428217 | 1 | 112.3622857 |
| 316 | 308843811 | 308843812 | 39.5754417 | 32.1428217 | 39.5750067 | 32.1414283 | 1 | 128.8568069 |
| 1001 | 2186060059 | 112273426 | 39.5748322 | 32.1414616 | 39.575075 | 32.1422917 | 2 | 76.10133449 |
| 1002 | 112273426 | 27047880 | 39.575075 | 32.1422917 | 39.5758782 | 32.1445942 | 2 | 216.6242102 |
| 1003 | 27047880 | 1397577714 | 39.5758782 | 32.1445942 | 39.5759738 | 32.1448068 | 2 | 21.0967387 |


## Processing the Data

As can be seen from the tables given above, raw data does not contain any *route* information. Raw data only have timestamped and geo-localized data with vehicle ID. Also, it is scattered around the network topology due to the tolerance of GPS track device for location determination. It is needed to *parse* the raw data to determine *routes* for each vehicle ID. In addition, once *routes* has determined, raw data should be projected in to the *routes* so that travel time and speed values can be calculated. This process is called as [Map Matching](https://en.wikipedia.org/wiki/Map_matching).

-  ### Map-Matching

The map-matching of the raw GPS data for vehicle trajectories simply associates the vehicular movement with the selected road network segments, for which speed, travel time or congestion can be estimated. Readily available [open source routing machine (OSRM) algorithm](http://project-osrm.org/docs/v5.24.0/api/#match-service), which employs Multi-level Dijkstra algorithm for route matching is used. The algorithm simply associates each GPS track point with an existing segment of the study corridor, if it satisfies the proximity and continuity conditions embedded.

The final product of the map-matching process adds a projected longitude and latitude value on the matched segment ID (a local value given in the study corridor definition), as a part of a route created based on the raw GPS track data. If, in a given raw GPS track data, there are long gaps or missing data not matched with the study corridor, the algorithm may produce multiple paths for that vehicle ID.

![MM Data Figure](figs/readme/mm_data.png)

| Vehicle ID | Lon | Lat | Timestamp | Route ID | Segment ID |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| 050l3cs | 32.720665 | 39.906138 | 18-Nov-2019 08:42:24 | 100 | 81 |
| 050l3cs | 32.717992 | 39.906021 | 18-Nov-2019 08:42:34 | 100 | 81 |
| 050l3cs | 32.71559 | 39.905915 | 18-Nov-2019 08:42:44 | 100 | 82 |
| 050l3cs | 32.706418 | 39.905558 | 18-Nov-2019 09:25:35 | 201 | 86 |
| 050l3cs | 32.703265 | 39.905444 | 18-Nov-2019 09:25:45 | 201 | 87 |
| 050l3cs | 32.699856 | 39.90529 | 18-Nov-2019 09:25:55 | 201 | 88 |
| 050l3cs | 32.696241 | 39.90483 | 18-Nov-2019 09:26:05 | 201 | 93 |


-  ### Transformation and Filtering