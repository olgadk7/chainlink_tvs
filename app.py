from chainlink_functions import get_names_list
from chainlink_functions import get_responses

import pickle
import numpy as np
import pandas as pd
from datetime import datetime

from chainlink_functions import plot_total_tvl_over_time
from chainlink_functions import plot_catorchain_tvl
from chainlink_functions import plot_catorchain_pergroup

import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash
from dash import html
from dash import dcc

# # DATA IMPORT
#
# # read in the users to use (and users not to use)
#
# sheet = "1ayLr5tEUzqjdSkR8n9Q_ylirk-QcXBf87xqmaNAcwYg"
# sources_sheet = "Sources"
#
# users_col="List of Chainlink users"
# nonusers_col="List of Users to exclude form the report/analytics"
#
# users_list = get_names_list(sheet_id=sheet, col_name_string=users_col, sheet_name=sources_sheet)
# nonusers_list = get_names_list(sheet_id=sheet, col_name_string=nonusers_col, sheet_name=sources_sheet)
#
# # print("Users list ({}".format(len(users_list)), "items): ", users_list, "\n"*2,
# #       "Non-users list ({}".format(len(nonusers_list)), "items): ", nonusers_list)
#
# # remove duplicates in the non-users list
# nonusers_list = list(set(nonusers_list))
#
# # market is comprised of all chainlink users and non-users
# market = users_list + nonusers_list
#
# # THIS SHOULDN'T BE HARDCODED. WRITE A FUNCTION TO AUTOMATE
# # remove duplicates
# nonusers_list.remove('bunny')
# users_list.remove('armor')
#
# # define market
# market = users_list + nonusers_list
#
# # pull TVL via DeFi Llama
#
# # use custom function to connect to DeFi Llama API
# users_json = get_responses(users_list)
#
# # get non-users (in order to get the market later by adding to 'users')
# nonusers_json = get_responses(nonusers_list)
#
# # non-users, together with users make up the market
# market_json = users_json + nonusers_json




# OR



# just open the already pulled data

# with open('users_json.pkl', 'wb') as f:
#     pickle.dump(users_json, f)
#     pickle.dump(nonusers_json, f)
#     pickle.dump(market_json, f)

with open('users_json.pkl', 'rb') as f:
    users_json = pickle.load(f)
    nonusers_json = pickle.load(f)
    market_json = pickle.load(f)





# Flatten json in a dataframe for EDA

users_tvl = pd.json_normalize(users_json, record_path="tvl", meta=['name', 'category', 'chain'])

# change timestamp to datetime for readability
users_tvl['date']=users_tvl['date'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

# repeat for market
market_tvl = pd.json_normalize(market_json, record_path="tvl", meta=['name', 'category', 'chain'])
market_tvl['date']=market_tvl['date'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

# and for non-users
nonusers_tvl = pd.json_normalize(nonusers_json, record_path="tvl", meta=['name', 'category', 'chain'])
nonusers_tvl['date']=nonusers_tvl['date'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))




# Plot interactive TVL graph with Plotly

tvl_over_time = plot_total_tvl_over_time(users_tvl, market_tvl)

tvl_cats = plot_catorchain_tvl(users_tvl, 'category', np.sum)

cats_pergroup = plot_catorchain_pergroup(users_tvl, nonusers_tvl, 'category')

tvl_chains = plot_catorchain_tvl(users_tvl, 'chain', np.sum)

chains_pergroup = plot_catorchain_pergroup(users_tvl, nonusers_tvl, 'chain')




# Deploy
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server=app.server

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H3('Chainlink TVL using DeFiLlama API', className='text-center text-primary, mb-3'))),

    dbc.Row([html.H5(
        'Note, plotly graphs are interactive, i.e. have the functionality to zoom in on the area of interest by selecting it.',
        className='text-center text-primary, mb-3')]),

dbc.Row([dcc.Markdown('''
    Why might we want to look at TVL? Popularized by the DeFi Pulse and the Concourse Open Community that developed other DeFi public services, TVL used to represent protocol growth and / or value. It gained traction as it captured something most smart contracts and networks in a very intricate system had in common: collateral. 

    As yield farming and liquidity mining took off, thanks to opportunities in incentive design, we have to take into account some nuances of TVL calculations if we were to make comparisons using it. For example, a big one is double counting, see (this twitter thread)[https://twitter.com/sikiriki12/status/1295089928901140481?s=20] for more info. The other ones are the direction of locking for multichain token migration, and, similarly, “sovereignty” over a native asset of one chain locked on another chain (more no these (here)[https://github.com/DefiLlama/DefiLlama-Adapters/pull/60#issuecomment-807045050])

    DeFi Llama, that is used here, considers any asset that is held in one of the protocol's contracts can be considered as part of TVL, with two exceptions (source https://docs.llama.fi/list-your-project/what-to-include-as-tvl ):
        * Assets on pool2, that is, money that is providing liquidity to an AMM pool where one of the tokens is from the protocol (except on some cases where those assets are performing an active function such as being used as collateral).
        * Non-crypto assets which are external to the blockchain, such as bonds or fiat currency.  
    ''', style={"margin-bottom": "50px"})]),

    dbc.Row([dcc.Graph(figure=tvl_over_time, style={'height': 550})]),

    dbc.Row([dcc.Markdown('''
    Looking at the TVL growth, **denominated in USD**, we're seeing a story of success, overall. Chainlink users' slope is less aggressive, and arguably more stable, than the market's. This could be attributed to some combination of quality of adoption and nature of business models (e.g. less speculative), among other reasons. I’ll dip my toes into breaking it down below, but a rigorous causal analysis is needed to speak with certainty about the directionality of the variables' interplay.  Indeed, TVL as the most common metric of DeFi has been criticized as being a measure of willingness to pay out the most **unsustainable yield farming** returns. As a result, some protocols have been experimenting with different pool ownership models. 

    It’s important to note that if we looked at the chart **denominated in ETH**, we would see a more moderate, albeit still a positive, slope. If we were asking ourselves how much of the TVL is due to **increase in deposits** and how much is due to **asset appreciation**, the TVL in ETH would tell us more about the deposits, than appreciation. 

    Zooming out to the macro level, how many assets deposited and held on among the different **categories** of Chainlink's users' smart contracts?

    ''', style={"margin-bottom": "50px"})]),

    dbc.Row([dbc.Col([
        html.H5("Chainlink's users TVL by category", className='text-center'),
        dcc.Graph(figure=tvl_cats, style={'height': 550})])]),

    dbc.Row([dcc.Markdown('''
    Among the Chainlink's users, most absolute TVL is generated by those in Lending.
    
    Some might argue TVL isn’t really comparable among the different DeFi sectors, or use-cases. For an automated market maker, TVL is the amount of liquidity against which traders can swap, and for a lending and borrowing marketplace, the metric represents the amount of funds available to borrow. Both are useful and can be a good indicator for general adoption. This analyst (argues)[https://cryptobriefing.com/most-popular-metric-tracking-defis-growth-is-critically-flawed-heres-why/], however, that the only cases where TVL depicts growth is for asset aggregators where holders of the aggregator’s native token capture a fee from investors when they exit, so the project’s revenue flow and TVL are directly correlated, and for derivative token holders who are rewarded a fee when more trading volume on the protocol.  

    Let's compare the composition of business categories among Chainlink's users to those in the rest of the market.
    ''', style={"margin-bottom": "50px"})]),

    dbc.Row(dcc.Graph(figure=cats_pergroup, style={'height': 550})),

    dbc.Row([dcc.Markdown('''
    There is definitely an unbalanced composition of the type of businesses among chainlink users and not. Lending dominates in the former group and DEXs in the latter.

    Zooming out to the blockchain level, how many assets deposited and held on Chainlinks' users' smart contracts across the chains?
    ''', style={"margin-bottom": "50px"})]),

    dbc.Row(dcc.Graph(figure=tvl_chains, style={'height': 550})),

    dbc.Row([dcc.Markdown('''
    Chainlink's users hold most assets on Ethereum. 
    
    
    ''', style={"margin-bottom": "50px"})]),

])

if __name__ == "__main__":
    app.run_server(debug=True, mode='external', host='127.0.0.1')