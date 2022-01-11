# coding: utf-8


def get_names_list(sheet_id, col_name_string, sheet_name=None):
    import pandas as pd
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url, usecols=[col_name_string])
    df = df.dropna(how='all')
    list_of_names = df[col_name_string].to_list()
    list_of_names = [user.replace(' ', '-').lower() for user in list_of_names]
    return list_of_names




def check_duplicates(listOfElems):

    seen = set()
    dupes = []

    for x in listOfElems:
        if x in seen:
            dupes.append(x)
        else:
            seen.add(x)
            
    if len(dupes)>0:
        print("There are dupes: ", dupes)
    else:
        print('No dupes')




def get_responses(list_of_names):

    '''gets the total value locked, includes staked tokens and outstanding collateral'''

    import requests
    import json 

    responses=[]
    for user in list_of_names:
        rr = requests.get('https://api.llama.fi/protocol/{}'.format(user), verify=False)

        if rr.status_code == 200:
            data=rr.json()
            try:
                data['name']
                responses.append(data)
            except KeyError:
                print("400: {}".format(user))
    return responses




def plot_single_tvl_over_time(responses_json, user_index):

    import requests
    import json 
    from datetime import datetime
    import plotly.graph_objects as go
    
    dates = []
    values = []
    for x in responses_json[user_index]['tvl']: 
        dates.append(datetime.fromtimestamp(int(x['date'])))
        values.append(x['totalLiquidityUSD'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=values,
                        mode='lines',
                        name='lines',
                        line_color='blue'))

    fig.update_layout(
        title={'text':'{}'.format(responses_json[user_index]['name']),
               'y':0.9, 'x':0.5,
               'xanchor': 'center','yanchor': 'top'},
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linewidth=2,
            zeroline=True,
            linecolor='#F4F4F4',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=14,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
            gridcolor='#F4F4F4',
            tickfont=dict(
                family='Arial',
                size=14,
                color='blue',
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        autosize=True,

        plot_bgcolor='white'
    )

    '''
    fig.add_layout_image(
        dict(
            source="https://images.plot.ly/language-icons/api-home/python-logo.png",
            xref="x",
            yref="y",
            x=0,
            y=3,
            sizex=2,
            sizey=2,
            sizing="stretch",
            opacity=0.5,
            layer="below")
    )
    '''
    return fig




def plot_total_tvl_over_time(df_users, df_market):
    
    users_tvl_grouped_bydate = df_users.groupby('date')['totalLiquidityUSD'].sum()
    market_tvl_grouped_bydate = df_market.groupby('date')['totalLiquidityUSD'].sum()
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    trace1 = go.Scatter(x=users_tvl_grouped_bydate.index,
                        y=users_tvl_grouped_bydate.values,
                        mode='lines', name='Chainlink TVL',
                        line_color='orange')

    trace2 = go.Scatter(x=market_tvl_grouped_bydate.index, 
                        y=market_tvl_grouped_bydate.values,
                        mode='lines', name='Market  TVL',
                        line_color='green')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(trace1)
    fig.add_trace(trace2) #, secondary_y=True

    fig['layout'].update(
        title={'text':'Chainlink vs market TVL',
               'y':0.9, 'x':0.5,
               'xanchor': 'center','yanchor': 'top'},
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linewidth=2,
            zeroline=True,
            linecolor='#F4F4F4',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=14,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
            gridcolor='#F4F4F4',
            tickfont=dict(
                family='Arial',
                size=14,
    #             color='blue',
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        autosize=True,

        plot_bgcolor='white'
    )

    return fig



def plot_catorchain_tvl(df, cat_or_chain_string, agg_np):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    import pandas as pd

    pivot_df = pd.pivot_table(df, values='totalLiquidityUSD', 
                            index=['date'], columns=cat_or_chain_string, aggfunc=agg_np)
    fig = go.Figure()
    for col in pivot_df.columns:
        fig.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[col].values,
                                 name = col,
                                 mode = 'lines',
                                 line=dict(shape='linear'),
                                 connectgaps=True))
    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linewidth=2,
            zeroline=True,
            linecolor='#F4F4F4',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=14,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
            gridcolor='#F4F4F4',
            tickfont=dict(
                family='Arial',
                size=14,
                # color='blue',
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        autosize=True,

        plot_bgcolor='white'
    )
    return fig


# def get_percentage_per_catorchain(df, catorchain_string):
#     rows_peruser_per_catorchain = df.groupby([catorchain_string,'name']).size()
#     user_per_catorchain = rows_peruser_per_catorchain.reset_index().groupby(catorchain_string).size()
#     total_users = sum(rows_peruser_per_catorchain.reset_index().groupby(catorchain_string).size().values)
#     catorchain_percentage_indf = 100 * user_per_catorchain / total_users
#
#     # # sanity check
#     # sum((100*ser.reset_index().groupby('category').size() / total_users).values)
#
#     return catorchain_percentage_indf




def plot_catorchain_pergroup(df_users, df_nonusers, catorchain_string):
    
    # from chainlink_functions import get_percentage_per_catorchain
    # cat_percentage_inusers = get_percentage_per_catorchain(df_users, catorchain_string)
    # cat_percentage_innonusers = get_percentage_per_catorchain(df_nonusers, catorchain_string)

    total_percat_inusers = df_users.groupby(catorchain_string).size()
    total_percat_innonusers = df_nonusers.groupby(catorchain_string).size()

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    trace1 = go.Bar(x=total_percat_inusers.index,
                    y=total_percat_inusers.values,
                    name='Chainlink users')

    trace2 = go.Bar(x=total_percat_innonusers.index,
                    y=total_percat_innonusers.values,
                    name='Non-Chainlink')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(trace1)
    fig.add_trace(trace2)

    fig['layout'].update(title={'text': 'Breakdown of {}'.format(catorchain_string),
                   'y':0.9, 'x':0.4,
                   'xanchor': 'center','yanchor': 'top'})

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linewidth=2,
            zeroline=True,
            linecolor='#F4F4F4',
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=14,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
            gridcolor='#F4F4F4',
            # ticksuffix='%',
            tickfont=dict(
                family='Arial',
                size=14,
                # color='blue',
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        autosize=True,

        plot_bgcolor='white'
    )

    return fig


