import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title='House Bike Analysis',
    page_icon='🚲',
    initial_sidebar_state='expanded'
)

bp  = pd.read_csv('data/Bike Program.csv')
ral = pd.read_csv('data/2023_DispatchActivities.csv')

with st.sidebar:
    min   = pd.to_datetime(ral.Dispatch).min()
    max   = pd.to_datetime(ral.Dispatch).max()
    start = st.date_input('Start Date', pd.to_datetime(min), min_value=pd.to_datetime(min))
    end   = st.date_input('End Date', pd.to_datetime(max), max_value=pd.to_datetime(max))
    isKeyword = st.toggle('Filter on Keywords',value=True)

    if isKeyword:
        keywords = ['CHAIN','CHAIN GUARD','CHAINGUARD','TIRE','PEDAL','PEDAL ARM','PEDALARM','HANDLEBAR','HANDLE BAR','AIR']
        options = st.multiselect('Look for service instructions containing the following terms:',keywords,keywords)


st.caption('VACAYZEN')
st.title('House Bike Analysis')
st.info('An insight on the bike types on Vacayzen\'s House Bike Program.')
st.warning('Emphasis on the four, newer bike types. See *Bike Types of Interest* sections.')

bp.columns = ['geo','partner','unit','unit_note','vendor_code','name','area','address','order','billing','bikes','type','locks','storage','start_date','end_date']
bp = bp[['partner','type','unit','order','bikes']]
bp = bp[~pd.isna(bp.order)]
bp = bp[~pd.isna(bp.bikes)]

bar                = pd.merge(bp, ral, left_on='order', right_on='RentalAgreementID', how='right')
bar.columns        = ['partner','type','unit','order','bikes','origin','remove','customer','date','Service','Office Note','Driver Note']
bar                = bar.drop(columns=['remove'])
bar                = bar[~bar['Service'].str.contains('GART', na=False)]
bar['Office Note'] = bar['Office Note'].str.upper()
bar['Driver Note'] = bar['Driver Note'].str.upper()
bar['date']        = pd.to_datetime(bar['date']).dt.date
bar                = bar.dropna(subset=['partner','type','unit','order','bikes'])

def GetBikesTouched(row):
    if 'BIKE CHECK' in row.Service: return int(row.bikes)
    return 1

bar['touched']    = bar.apply(GetBikesTouched, axis=1)

def ServiceNoteContainsKeyword(row):
     for option in options:
         if option in str(row['Office Note']):
             return True
         
     return False

if isKeyword:
    bar['hasKeyword'] = bar.apply(ServiceNoteContainsKeyword, axis=1)


bar   = bar[(bar['date'] >= start) & (bar['date'] <= end)]



st.header('Services by Bike Type', help='Service items that occur on house bike agreements by bike type are counted here.')

if isKeyword: key = bar[bar['hasKeyword']]
else:         key = bar

pivot = pd.pivot_table(key, values='partner', index='Service', columns='type', aggfunc='count')
st.dataframe(pivot, use_container_width=True)

st.write('**Bike Types of Interest**')
left, middle_left, middle_right, right = st.columns(4)
left.metric('2022 Vacayzen TAXI', np.sum(pivot['2022 Vacayzen TAXI']))
middle_left.metric('Generic New Wave', np.sum(pivot['Generic New Wave']))
middle_right.metric('Vacayzen New Wave', np.sum(pivot['Vacayzen New Wave']))
right.metric('Yellow 360 YOLO', np.sum(pivot['Yellow 360 YOLO']))

st.download_button('DOWNLOAD SERVICES BY BIKE TYPE',pivot.to_csv(),'Services By Bike Type.csv',use_container_width=True)



st.header('Bike Touches by Service', help='The number of bikes "touched" during service items.')

if isKeyword: touch = bar[bar['hasKeyword']]
else:         touch = bar

touch = touch[['partner','type','unit','bikes','order','date','Service','Office Note','Driver Note','touched']]

st.info('Any **bike check** service assumes a driver touches **each bike at the respective property**.')
st.info('Any **non-bike-check** service assumes a driver touches **one bike**.')

pivot_touch = pd.pivot_table(touch, values='touched', index='Service', columns='type', aggfunc='sum')
st.dataframe(pivot_touch)

st.write('**Bike Types of Interest**')  
left, middle_left, middle_right, right = st.columns(4)
left.metric('2022 Vacayzen TAXI', np.sum(pivot_touch['2022 Vacayzen TAXI']))
middle_left.metric('Generic New Wave', np.sum(pivot_touch['Generic New Wave']))
middle_right.metric('Vacayzen New Wave', np.sum(pivot_touch['Vacayzen New Wave']))
right.metric('Yellow 360 YOLO', np.sum(pivot_touch['Yellow 360 YOLO']))

st.download_button('DOWNLOAD BIKE TOUCHES BY SERVICE',pivot.to_csv(),'Bike Touches By Service.csv',use_container_width=True)



st.header('Dispatches by Bike Type', help='Any dispatch service notes and correlating driver notes for service done on each bike type.')

if isKeyword: key = bar[bar['hasKeyword']]
else:         key = bar

key = key[['partner','type','unit','order','date','Service','Office Note','Driver Note']]
option_type = st.selectbox('Bike Type',key.type.unique())

dispatches = key[key['type'] == option_type]
dispatches = dispatches[['Service','Office Note','Driver Note','date','partner','unit','order']]
dispatches.columns = ['Service','Office Note','Driver Note','Date','Partner','Unit','Order']

st.dataframe(dispatches, use_container_width=True)
st.download_button('DOWNLOAD DISPATCHES BY BIKE TYPE',dispatches.to_csv(),'Dispatches By Bike Type.csv',use_container_width=True)


st.header('Efficiency by Bike Type', help='(All non-check and non-delivery services) over (all check and delivery services).')

st.latex(r'efficiency = \left(1 - \frac{services}{deliveries + checks}\right) * 100')

efficient = bar

pivot_efficient = pd.pivot_table(efficient, values='partner', index='Service', columns='type', aggfunc='count')
pivot_efficient = pivot_efficient.fillna(0)

def GetEfficiency(column):
    numerator   = np.sum(column)
    denominator = column['DELIVERY'] + column['BACKPACK & BIKE CHECK']+ column['BIKE CHECK'] + column['BIKE CHECK - ALAYA'] + column['BIKE CHECK - OWNER ARRIVAL']
    numerator   = numerator - denominator

    return round((1 - (numerator / denominator)) * 100,2)

efficiency = pivot_efficient.apply(GetEfficiency)
efficiency = pd.DataFrame(efficiency)
efficiency.index.names = ['Type']
efficiency.columns = ['Efficiency']
efficiency = efficiency.sort_values(by='Efficiency',ascending=False)

st.dataframe(efficiency, use_container_width=True)
st.download_button('DOWNLOAD EFFICIENCY BY BIKE TYPE',efficiency.to_csv(),'Efficiency By Bike Type.csv',use_container_width=True)