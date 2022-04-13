import argparse
import pandas as pd
import numpy as np

cost_burden_income_cols = ['geoname', 'A3','A6','A9', 'A12', 'A15','H1',	'H2',	'H4',	'H5',	'H7',	'H8',	'H10',	'H11',	'H13',	'H16']
cost_burden_income_cols_display = 	['County', 'Household Income <= 30% HAMFI (Total)','Household Income >30% to <=50% HAMFI (Total)', 'Household Income >50% to <=80% HAMFI (Total)', 'Household Income >80% to <=100% HAMFI (Total)','Household Income >100% HAMFI (Total)', 'Household Income <= 30% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income <= 30% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >30% to <=50% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >30% to <=50% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >50% to <=80% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >50% to <=80% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >80% to <=100% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >80% to <=100% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >100% HAMFI (Owners and Renters) and Cost burden > 30%',	'Total (Owners and Renters) and Cost burden > 30%']
cost_burdens_income = ['Cost burden > 50%', 'Cost burden > 30%  <=50', 'Cost burden <= 30%']

cost_burden_display = ['Severly Cost Burdened (50% or more)', 'Cost Burdened (30% or more, but less than 50%)','Unburdened (Less than 30%)']

household_incomes = ['Household Income <= 30%', 'Household Income >30% to <=50%', 'Household Income >50% to <=80%',
                     'Household Income >80% to <=100%', 'Household Income >100%']

household_incomes_display = ['Extremely Low Income (0-30% AMI)', 'Very Low Income (31-50% AMI)',  \
                             'Low Income (51-80% AMI)', '80+% AMI', '80+% AMI']  
household_incomes_ord = ['Extremely Low Income (0-30% AMI)', 'Very Low Income (31-50% AMI)',  \
                             'Low Income (51-80% AMI)', '80+% AMI']

def createCostBurdenDict(cost_burdens, cost_burden_display):
    '''
    creates cost burdesn dictionary for mapping from numerical cost_burden to user friendly cost burden names
    cost_burdens - numerical cost burden variable
    cost_burden_display - user friendly cost burden names
    '''
    cost_burden_dict = {cost_burdens[i]: cost_burden_display[i] for i in range(len(cost_burdens))}
    return(cost_burden_dict)                  

def costBurdenIncomeClean(ASSETS_PATH, COST_BURDEN):
    '''
    takes datasets path and cost_burden dataset and transforms the dataset to be used for visualization
    ASSETS_PATH - input dataset path
    COST_BURDEN - downlowaded cost burden filename
    '''
    cost_burden_df = pd.read_csv(ASSETS_PATH + COST_BURDEN)
    cost_burden_df = cost_burden_df.iloc[:, 1:]
    
    income_df = cost_burden_df.loc[:, cost_burden_income_cols]
    income_df.columns = cost_burden_income_cols_display

    income_df =  income_df.set_index('County').T.reset_index().rename(columns={'index':'household_income'})
    income_df['household_income'] = income_df['household_income'].apply(lambda x: x.replace('(Owners and Renters)', ''))
    income_df[['household_income', 'cost_burden']] = income_df.iloc[:, 0].str.split(' HAMFI ', expand=True)
    # Cleanup the columns - remove the "Michigan" from column name
    cost_burden_cols = list(income_df.columns)
    cost_burden_cols = [col.replace(', Michigan', '') for col in cost_burden_cols]
    income_df.columns = cost_burden_cols

    cost_burden = 'Cost burden <= 30%'
    # create rows for cost_burden less than 30 and less than 50 based on other cost_burden columns
    # approach used is say, we are given data for cost burden > 30% and cost burden total, then
    # by substracting cost_burden > 30% from total we can get cost_burden < 30%
    # similarly, we compute cost_burden > 30 and < 50% by substracting cost burden > 50% from cost burden >30%
    for household_income in household_incomes:
      CostTotal = np.where((income_df['household_income'] == household_income) &\
                    (income_df['cost_burden'] == '(Total)'))
      CostGrater30 = np.where((income_df['household_income'] == household_income) &\
                        (income_df['cost_burden'] == ' and Cost burden > 30%'))

      CostBurdenLess30 =  [household_income]  + \
                          (np.array(income_df.loc[CostTotal].iloc[:, 1:84]) - \
                            np.array(income_df.loc[CostGrater30].iloc[:, 1:84])  \
                              ).flatten().tolist()  + [cost_burden]

      income_df.loc[len(income_df.index)]  = CostBurdenLess30

      if household_income == 'Household Income >100%':
        break
      # computing cost burden > 30% and < 50%
      CostGrater50 = np.where((income_df['household_income'] == household_income) & \
                              (income_df['cost_burden'] == ' and Cost burden > 50%'))
      CostBurden30To50 =  [household_income]  + \
                            (np.array(income_df.loc[CostGrater30].iloc[:, 1:84]) - \
                                np.array(income_df.loc[CostGrater50].iloc[:, 1:84])   \
                                    ).flatten().tolist()  + ['Cost burden > 30% and <=50']

      income_df.loc[len(income_df.index)]  = CostBurden30To50  

    income_df.dropna(inplace=True)
    # cleaning the cost_burden column
    income_df['cost_burden'] = income_df['cost_burden'].str.replace('and', '', regex=False).str.replace('\(', '', regex=False)   \
                                    .str.replace('\)', '', regex=False).str.strip()
    # remove the data for cost_burden > 30% and Total 
    income_df = income_df[~income_df['cost_burden'].isin(['Cost burden > 30%', 'Total'])].reset_index(drop=True)

    # assigning user friendly household_income columns
    household_incomes_dict = {household_incomes[i]: household_incomes_display[i] for i in range(len(household_incomes))}                                  
    income_df.loc[:, 'household_income'] = income_df['household_income'].map(household_incomes_dict)

    cost_burden_dict = createCostBurdenDict(cost_burdens_income, cost_burden_display)
    income_df.loc[:, 'cost_burden'] = income_df['cost_burden'].map(cost_burden_dict)

    income_df = income_df.melt(id_vars=['cost_burden', 'household_income'], var_name='county')

    income_df = income_df.groupby(['cost_burden', 'household_income', 'county']).sum().reset_index()
    income_df.loc[:, 'cost_burden'] = pd.Categorical(income_df.cost_burden, cost_burden_display, ordered=True)
    income_df = income_df.sort_values(by=['county', 'cost_burden']).reset_index(drop=True)
    return(income_df)


# Transformations for cost_burden by tenure
cost_burdens_tenure = ['Cost Burden >50%', 'Cost Burden >30% to <=50%', 'Cost Burden <=30%']

# choosing only cols required for cost burden by tenure metric
cost_burden_tenr_cols = ['geoname', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']  
cost_burden_tenure_cols_desc = 	['County','Cost Burden <=30% (Owner Occupied)', 'Cost Burden <=30% (Renter Occupied)',
                                    'Cost Burden <=30% (Total)', 'Cost Burden >30% to <=50% (Owner Occupied)',
                                    'Cost Burden >30% to <=50% (Renter Occupied)',
                                    'Cost Burden >30% to <=50% (Total)',
                                    'Cost Burden >50% (Owner Occupied)',
                                    'Cost Burden >50% (Renter Occupied)',
                                    'Cost Burden >50% (Total)']



def costBurdenTenureClean(ASSETS_PATH, COST_BURDEN):
    '''
    takes datasets path and cost_burden dataset and transforms the dataset to be used for visualization
    ASSETS_PATH - input dataset path
    COST_BURDEN - downlowaded cost burden filename
    '''
    cost_burden_df = pd.read_csv(ASSETS_PATH + COST_BURDEN)
    cost_burden_df = cost_burden_df.iloc[:, 1:]

    # choosing only cols required for cost burden by tenure metric
    df = cost_burden_df.loc[:, cost_burden_tenr_cols]

    # Assigning corresponding description cols for the metric
    df.columns = 	cost_burden_tenure_cols_desc
    df = df.set_index('County').T.reset_index().rename(columns={'index':'cost_burden'})

    # create seperate columns for cost burden into  cost burden and tenure
    df[['cost_burden', 'tenure']] = df.iloc[:, 0].str.split(' \(', expand=True)
    cost_burden_cols = list(df.columns)

    # cleanup the county column, by removing the state name from county name
    cost_burden_cols = [col.replace(', Michigan', '') for col in cost_burden_cols]
    df.columns = cost_burden_cols                 

    # change the data from long to wide format for viz purpose
    df = df.melt(id_vars=['cost_burden', 'tenure'], var_name='county')
    # cleanup the tenure column
    df['tenure'] = df.iloc[:, 1].str.replace(')', '', regex=False).str.split(expand=True).iloc[:, 0]

    # map the numerical cost burden to user friendly names
    cost_burden_dict = createCostBurdenDict(cost_burdens_tenure, cost_burden_display)
    df['cost_burden'] = df['cost_burden'].map(cost_burden_dict)

    # change the data type of cost_burden from object to categorical(required for arranging the segments in stacked bars) 
    df.loc[:, 'cost_burden'] = pd.Categorical(df.cost_burden, cost_burden_display, ordered=True)
    df = df.sort_values(['county', 'cost_burden']).reset_index(drop=True)
    return(df)                    


if __name__ == '__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument('ASSETS_PATH', help='input path for datasets')
    parser.add_argument('COST_BURDEN', help='downloaded cost burden input file (csv)')    
    parser.add_argument('COST_BURDEN_INCOME', help='transformed cost burden by income output file (csv)')
    parser.add_argument('COST_BURDEN_TENURE', help='transformed cost burden by tenure output file (csv)')    
    
    args = parser.parse_args()    
    cost_burden_income_df = costBurdenIncomeClean(args.ASSETS_PATH, args.COST_BURDEN)
    cost_burden_tenure_df = costBurdenTenureClean(args.ASSETS_PATH, args.COST_BURDEN)  
    
    cost_burden_income_df.to_csv(args.ASSETS_PATH + args.COST_BURDEN_INCOME, index=False)
    cost_burden_tenure_df.to_csv(args.ASSETS_PATH + args.COST_BURDEN_TENURE, index=False)
    