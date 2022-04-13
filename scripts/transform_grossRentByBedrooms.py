import argparse
import pandas as pd

cols_rooms = ['No Rooms', '1 Room', '2 Rooms', '3 Rooms', '4 Rooms', '5 or more Rooms']

def cleanGrossRent(ASSETS_PATH, GROSS_RENT_BY_BEDROOMS):
    '''
    takes datasets path and gross_rent_by_bedrooms dataset and transforms the dataset to be used for visualization
    ASSETS_PATH - input dataset path
    GROSS_RENT_BY_BEDROOMS - downlowaded gross rent by bedrooms filename
    '''
    df = pd.read_json(ASSETS_PATH + GROSS_RENT_BY_BEDROOMS)
    df.columns = df.iloc[0, :]
    df = df.drop(columns=['state','county']).iloc[1:, :]
    df['NAME'] = df['NAME'].str.split(',', expand=True).iloc[:, 0]
    df = df.set_index('NAME')
    return(df)  

def cleanGrossRentEst(df, cols_rooms):
#     values of -222222222 and -666666666 indicative of 'Values not available'
    df = df.iloc[:, :6]
    df.columns = cols_rooms
    df.reset_index(inplace=True)
    df = df.melt(id_vars='NAME', var_name='No_of_Rooms', value_name='Rent')
    df['Rent'] = df['Rent'].astype('int32')
#     replacing values not available with ZERO for viz purpose.
    df['Rent'] = df['Rent'].apply(lambda x: x if x > -222222222 else 0)
    df = df.sort_values(by=['NAME', 'No_of_Rooms']).reset_index(drop=True)
    return(df)

def cleanGrossRentMoe(df, cols_rooms):
    gross_rent_moe_df = df.iloc[:, 6:]
    gross_rent_moe_df.columns = cols_rooms
    gross_rent_moe_df.reset_index(inplace=True)  
    return(gross_rent_moe_df)


if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument('ASSETS_PATH', help='input path for datasets')
    parser.add_argument('GROSS_RENT_BY_BEDROOMS', help='downloaded gross_rent_by_bedromms input file (json)')        
    parser.add_argument('OUTPUT_FILE', help='transformed GrossRent by BedRooms file (csv)')
    
    args = parser.parse_args()
        
    gross_rent_df = cleanGrossRent(args.ASSETS_PATH, args.GROSS_RENT_BY_BEDROOMS)  
    gross_rent_est_df  = cleanGrossRentEst(gross_rent_df, cols_rooms)
    
    gross_rent_est_df.to_csv(args.ASSETS_PATH + args.OUTPUT_FILE, index=False)