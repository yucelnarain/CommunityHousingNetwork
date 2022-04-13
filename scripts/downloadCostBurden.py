import argparse
import pandas as pd
import json
import requests
import os                       

def createPredicatesCostBurden(county, token):
    '''
    create predicates/headers for the CHAS data API
    county - County id for which we want to download the cost burden
    token - API token to access the CHAS API, CHN needs to register for CHAS API and get this token 
    '''
    predicates = {}
    predicates['type'] = 3
    predicates['stateId'] = 26
    predicates['entityId'] = county
    auth_token_string = "Bearer "+ token
    headers = {"Authorization": auth_token_string}
    return(predicates, headers)

# Download Cost Burden data
def download_dataCostBurden(base_uri, token, path, filename):
    '''
    downloads data for costBurden Metric
    base_uri - HUD API URI (https://www.huduser.gov/hudapi/public/chas)
    token - API token to access the API, user needs to register for the API to get the token
    path - system path, where downloaded needs to be written
    filename - filename, which would be used to write the downloaded data
    '''
    filepath = path + filename
    if os.path.isfile(filepath):
        print(filepath)
        print('file already exists, no need to download')
    else:
        for county in range(1, 166, 2):
          predicates, headers = createPredicatesCostBurden(county, token)
          result = requests.get(base_uri, params=predicates, headers=headers) 
          if result.status_code == 200:
            if county !=1:
              cost_burden_df = cost_burden_df.append(pd.DataFrame(json.loads(result.content)))
            else:
              cost_burden_df = pd.DataFrame(json.loads(result.content))
              # print(cost_burden_df)
          else:
            print('API returned Error: ', result.status_code, '\n', 'Downloading of data failed.')
        cost_burden_df.to_csv(path + filename)

if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument('BASE_URI', help='base uri of dataset API')
    parser.add_argument('TOKEN', help='API token for HUDUSER (API token)')
    parser.add_argument('ASSETS_PATH', help='input path for datasets')
    parser.add_argument('OUTPUT_FILE', help='GrossRent by BedRooms file (json)')
    
    args = parser.parse_args()    
        
    download_dataCostBurden(args.BASE_URI, args.TOKEN, args.ASSETS_PATH, args.OUTPUT_FILE)
    cost_burden_df = pd.read_csv(args.ASSETS_PATH + args.OUTPUT_FILE)
    cost_burden_df = cost_burden_df.iloc[:, 1:]
    cost_burden_df.to_csv(args.OUTPUT_FILE)
    