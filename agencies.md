# Agency Submission Documentation


## California

As of 2022, California has two routes to submit data for 303(d) reviews: [CEDEN](http://ceden.org/index.shtml) and the [Integrated Report Upload Portal](https://www.waterboards.ca.gov/water_issues/programs/water_quality_assessment/ir_upload_portal.html). CEDEN is the preferred method in most cases and has a strict excel format that we created a python formatter for using [xlrd](https://pypi.org/project/xlrd/). Continuous data, however, must currently be uploaded to the Integrated Report Upload Portal as a spreadsheet or csv. For both submission routes, a Quality Assurance Project Plan (QAPP) or equivalent document should be submitted throught the Integratd Report Upload Portal. More information on IRUP data requirements and QAPPs is available [here](https://www.waterboards.ca.gov/water_issues/programs/water_quality_assessment/data_requirements.html). Further information from the 2024 Integrated Report: [Notice of Public Solicitation](https://www.waterboards.ca.gov/water_issues/programs/water_quality_assessment/docs/2024_solicitation_notice_final.pdf)

### Submission

| Contact Info | Regional Water Board | Pollutant Categories | Start Time | End Time | Summary | QAPP |
| --- | --- | --- | --- | --- | --- | --- |

### Station
| Station Code | Station Name | Latitude | Longitude | datum |
|-|-|-|-|-|

### Data
| Date | Time | Number of Samples | Analytes | Unit of Measurement | Methods | Detection Limits | Reporting Limits | Supporting analytical data | 
|-|-|-|-|-|-|-|-|-|

## Washington

As of 2022, Washington request environmental monitoring data be uploaded into their Environmental Information Monitoring (EIM) database. They provide [detailed instructions](https://fortress.wa.gov/ecy/eimhelp/HelpDocuments/OpenDocument/13) for continuous monitoring data. The submission process is mainly set up for the submitting party to be the same party that originally collected data. Through contact with Chris Neumiller from WA Department of Ecology, they would consider accepting third party submissions if the data provider agreed. NOAA NERRS data (particularly from Padilla Bay) were flagged as beneficial to be added. 

Basically data should be transferred to their excel spreadsheet template and submitted in batches. One batch should be basically one sensor-deployment (split in two if it spans a daylight savings shift) and should not have more than 150,000 rows. Batches are submitted together as a dataset and must pass an online checker. Once passed, it is submitted to a data coordinator for review. 

[Study Table](https://apps.ecology.wa.gov/eim/help/HelpDocuments/OpenDocument/27)
[Location Table](https://apps.ecology.wa.gov/eim/help/HelpDocuments/OpenDocument/4)
[Results Table](https://apps.ecology.wa.gov/eim/help/HelpDocuments/OpenDocument/30)

## Hawaii

Hawaii intends for submissions to be done by the party conducting the study unless it is a public submission from a reputable source. [2022 Submission Form](https://health.hawaii.gov/cwb/files/2021/03/data-submittal-2022.pdf) and [Data Submission Guidelines](https://health.hawaii.gov/cwb/files/2020/09/Data-Acceptance-Criteria-revised-200904_2.pdf). Data is submitted via email or paper mail. 