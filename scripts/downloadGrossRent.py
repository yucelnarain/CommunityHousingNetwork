import argparse
import pandas as pd
import requests
import os                       

def createPredicatesGrossRent(tableId, var_cnt):
  '''
  create predicates for the census data API
  base_uri - This is the base uri for the census API
  tableId - table name, which we want to download
  var_cnt - Number of variables the table has 
  '''
  county = "*"
  state= "26"
  estimate = []
  moe = []
  for i in range(2, var_cnt+1):
    estimate.append(tableId + '_00' + str(i) + 'E')
    moe.append(tableId + '_00' + str(i) + 'M')

  get_vars = ['NAME'] + estimate + moe
  predicates = {}
  predicates["get"] = ','.join(get_vars)
  predicates["in"] = "state:" + state
  predicates["for"] = "county:" + county
  return(predicates)

def download_data(base_uri,predicates, path, filename, headers=''):
    '''
    downloads data for costBurden Metric
    base_uri - HUD API URI (https://www.huduser.gov/hudapi/public/chas)
    predicates - parameters used to connect to API
    path - system path, where downloaded needs to be written
    filename - filename, which would be used to write the downloaded data
    '''    
    filepath = path + filename
    if os.path.isfile(filepath):
        print(filepath)
        print('file already exists, no need to download')
    else:
        result = requests.get(base_uri, params=predicates, headers=headers) 
        if result.status_code == 200:
          with open(filepath, 'wb') as f:
              f.write(result.content)
        else:
          print('API returned Erro: ', result.status_code, '\n', 'Downloading of data failed.',  \
                'Please check the API')

        
if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument('BASE_URI', help='base uri of dataset API')
    parser.add_argument('ASSET_PATH', help='path for datasets (input)')
    parser.add_argument('OUTPUT_FILE', help='GrossRent by BedRooms output dataset file (json)')
    
    args = parser.parse_args()
    GROSS_RENT_BY_BEDROOMS  = 'GrossRentByBedRooms.json'
    
    # GrossRentByBedrooms
    tableId = 'B25031'
    var_cnt = 7
    predicates = createPredicatesGrossRent(tableId, var_cnt)
    download_data(args.BASE_URI, predicates, args.ASSET_PATH, args.OUTPUT_FILE)     