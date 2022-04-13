![CHN_logo](CHN_logo.png) 

This is the dashboard created to provide inputs to CHN team.

### Usage
Note: Run Makefile to download the data required. 

**County for which chart needs to be generated**
<br>county := 'Wayne County'</br>

**Data Sources**
<br>**API URI used for GrossRentByBedRooms metric**
<br>base_uri_gross_rent := 'https://api.census.gov/data/2020/acs/acs5'</br>

**API URI used for costBurden metric**
<br>base_uri_cost_burden := 'https://www.huduser.gov/hudapi/public/chas'</br>

**API token used for costBurdenMetric**
<br>api_token := 'Register for the API at - https://www.huduser.gov/portal/dataset/chas-api.html'</br>

**dependencies to run**
<code>
visualization: transformCostBurden transformGrossRentByBedroom
	python visualization.py assets/ $(county) cost_burden_income.csv cost_burden_tenure.csv cost_burden_income.html cost_burden_tenure.html</code>

**creates transformed data from downloaded datasets**
<code>
transform: transformCostBurden transformGrossRentByBedroom

transformCostBurden: assets/costBurden.csv
	python transform_costBurden.py assets/ costBurden.csv cost_burden_income.csv cost_burden_tenure.csv
    
transformGrossRentByBedroom: assets/GrossRentByBedRooms.json
	python transform_grossRentByBedrooms.py assets/ GrossRentByBedRooms.json gross_rent_est.csv</code>

**downloads required datasets for both the metrics(cost_burden and gross_rent_by_bedrooms)**
<code>
assets/costBurden.csv:
	python downloadCostBurden.py $(base_uri_cost_burden) $(api_token) assets/ costBurden.csv

assets/GrossRentByBedRooms.json:
	python downloadGrossRent.py $(base_uri_gross_rent) assets/ GrossRentByBedRooms.json</code>