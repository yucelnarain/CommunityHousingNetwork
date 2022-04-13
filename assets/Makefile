#county for which chart needs to be generated
county := 'Wayne County'

#datasets path
datasets_path := '../assets/'

#path for scripts
scripts_path = '../scripts'

# variables declared for GrossRentByBedRooms metric
base_uri_gross_rent := 'https://api.census.gov/data/2020/acs/acs5'

# variables declared for costBurden metric
base_uri_cost_burden := 'https://www.huduser.gov/hudapi/public/chas'
api_token := 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjliODAyYjM0YWY2ZmJlMGUwYjlmZjZkZTMyNWRhM2M0MjNmNTgzZGFjYjcwM2JkZjdjNzAzMGEyZTIyNDRjODUxODlkZDQzNmMxYTY1MmIxIn0.eyJhdWQiOiI2IiwianRpIjoiOWI4MDJiMzRhZjZmYmUwZTBiOWZmNmRlMzI1ZGEzYzQyM2Y1ODNkYWNiNzAzYmRmN2M3MDMwYTJlMjI0NGM4NTE4OWRkNDM2YzFhNjUyYjEiLCJpYXQiOjE2NDMzMDgwNTIsIm5iZiI6MTY0MzMwODA1MiwiZXhwIjoxOTU4ODQwODUyLCJzdWIiOiIyOTM0MCIsInNjb3BlcyI6W119.IR0_v5Z4OrNawpOC3h-m33f1N_PNvKX539pehlrCLrMlCy3eJ5HDL7ddVCViUPiHe3arVJchTmqa7RO-Fc92-A'


# dependencies to run
visualization: transformCostBurden transformGrossRentByBedroom
	python $(scripts_path)/visualization.py $(datasets_path) $(county) cost_burden_income.csv cost_burden_tenure.csv gross_rent_est.csv cost_burden_income.html cost_burden_tenure.html gross_rent_by_bedrooms.html

# creates transformed data from downloaded datasets
transform: transformCostBurden transformGrossRentByBedroom

transformCostBurden: $(datasets_path)/costBurden.csv
	python $(scripts_path)/transform_costBurden.py $(datasets_path) costBurden.csv cost_burden_income.csv cost_burden_tenure.csv
    
transformGrossRentByBedroom: $(datasets_path)/GrossRentByBedRooms.json
	python $(scripts_path)/transform_grossRentByBedrooms.py $(datasets_path) GrossRentByBedRooms.json gross_rent_est.csv   

# downloads required datasets for both the metrics(cost_burden and gross_rent_by_bedrooms)
$(datasets_path)/costBurden.csv:
	python $(scripts_path)/downloadCostBurden.py $(base_uri_cost_burden) $(api_token) $(datasets_path) costBurden.csv

$(datasets_path)/GrossRentByBedRooms.json:
	python $(scripts_path)/downloadGrossRent.py $(base_uri_gross_rent) $(datasets_path) GrossRentByBedRooms.json