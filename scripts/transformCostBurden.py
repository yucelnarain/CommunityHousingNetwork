import pandas as pd

cost_burden_income_cols = ['geoname', 'A3','A6','A9', 'A12', 'A15','H1',	'H2',	'H4',	'H5',	'H7',	'H8',	'H10',	'H11',	'H13',	'H16']
cost_burden_income_cols_display = 	['County', 'Household Income <= 30% HAMFI (Total)','Household Income >30% to <=50% HAMFI (Total)', 'Household Income >50% to <=80% HAMFI (Total)', 'Household Income >80% to <=100% HAMFI (Total)','Household Income >100% HAMFI (Total)', 'Household Income <= 30% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income <= 30% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >30% to <=50% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >30% to <=50% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >50% to <=80% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >50% to <=80% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >80% to <=100% HAMFI (Owners and Renters) and Cost burden > 30%',	'Household Income >80% to <=100% HAMFI (Owners and Renters) and Cost burden > 50%',	'Household Income >100% HAMFI (Owners and Renters) and Cost burden > 30%',	'Total (Owners and Renters) and Cost burden > 30%']
cost_burdens = ['Cost burden > 50%', 'Cost burden > 30%  <=50', 'Cost burden <= 30%']

cost_burden_display = ['Severly Cost Burdened (50% or more)', 'Cost Burdened (30% or more, but less than 50%)','Unburdened (Less than 30%)']

household_incomes = ['Household Income <= 30%', 'Household Income >30% to <=50%', 'Household Income >50% to <=80%',
                     'Household Income >80% to <=100%', 'Household Income >100%']

household_incomes_display = ['Extremely Low Income (0-30% AMI)', 'Very Low Income (31-50% AMI)',  \
                             'Low Income (51-80% AMI)', '80+% AMI', '80+% AMI']  
household_incomes_ord = ['Extremely Low Income (0-30% AMI)', 'Very Low Income (31-50% AMI)',  \
                             'Low Income (51-80% AMI)', '80+% AMI']

def createCostBurdenDict(cost_burdens, cost_burden_display):
  cost_burden_dict = {cost_burdens[i]: cost_burden_display[i] for i in range(len(cost_burdens))}
  return(cost_burden_dict)                  

def costBurdenIncomeClean(cost_burden_df, cost_burden_income_cols, cost_burden_income_cols_display,  \
                            cost_burdens, cost_burden_display, household_incomes):
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
    income_df['cost_burden'] = income_df['cost_burden'].str.replace('and', '').str.replace('\(', '').str.replace('\)', '').str.strip()
    # remove the data for cost_burden > 30% and Total 
    income_df = income_df[~income_df['cost_burden'].isin(['Cost burden > 30%', 'Total'])].reset_index(drop=True)

    # assigning user friendly household_income columns
    household_incomes_dict = {household_incomes[i]: household_incomes_display[i] for i in range(len(household_incomes))}                                  
    income_df.loc[:, 'household_income'] = income_df['household_income'].map(household_incomes_dict)

    cost_burden_dict = createCostBurdenDict(cost_burdens, cost_burden_display)
    income_df.loc[:, 'cost_burden'] = income_df['cost_burden'].map(cost_burden_dict)

    income_df = income_df.melt(id_vars=['cost_burden', 'household_income'])

    income_df = income_df.groupby(['cost_burden', 'household_income', 'variable']).sum().reset_index()
    income_df.loc[:, 'cost_burden'] = pd.Categorical(income_df.cost_burden, cost_burden_display, ordered=True)
    income_df = income_df.sort_values(by='cost_burden')
    return(income_df)

cost_burden_income_df = costBurdenIncomeClean(cost_burden_df, cost_burden_income_cols, cost_burden_income_cols_display,  \
                            cost_burdens, cost_burden_display, household_incomes)
