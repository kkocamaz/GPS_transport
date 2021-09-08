# Description of the Project
---
> *under construction*


This project is a part of an [TÜBİTAK 1501](https://www.tubitak.gov.tr/en/funds/industry/national-support-programmes/content-1501-industrial-rd-projects-grant-programme) project titled "*Konum verisi ile ulaşım analiz, planlama ve modelleme için büyük veri platformu geliştirilmesi*" (EN: Developing a big data platform for transportation analysis, planning and modelling with geodata)

## Contents

- [Raw Data](#raw-data)
- [Scope of the Project](#scope-of-the-project)
- [Processing the Data](#process-data)
  - [Map-Matching Algorithm](#map-matching-algo)
  - [Transformation and Filtering the Data](#transformation-and-filtering)
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

--segment figure--

--segment table--