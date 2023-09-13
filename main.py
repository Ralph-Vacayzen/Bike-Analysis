import streamlit as st
import pandas as pd
import numpy as np

bap = pd.read_csv('data/Bike Analysis - Properties.csv')
ral = pd.read_csv('data/2023_DispatchActivities.csv')

st.title('Bike Analysis')
st.info('An insight on the four, new bike types on Vacayzen\'s House Bike Program.')
st.warning('Analysis is on a sample size of 20 properties per bike type.')

bar                = pd.merge(bap, ral, left_on='ORDER', right_on='RentalAgreementID', how='left')
bar.columns        = ['partner','type','unit','order','remove','date','Service','Office Note','Driver Note']
bar                = bar.drop(columns=['remove'])
bar                = bar[~bar['Service'].str.contains('GART', na=False)]
bar['Office Note'] = bar['Office Note'].str.upper()
bar['Driver Note'] = bar['Driver Note'].str.upper()

bar['date']        = pd.to_datetime(bar['date']).dt.date

left, right = st.columns(2)
start = left.date_input('Start Date', pd.to_datetime('01/01/2023'))
end   = right.date_input('End Date', pd.to_datetime('09/13/2023'))

bar   = bar[(bar['date'] >= start) & (bar['date'] <= end)]

pivot = pd.pivot_table(bar, values='partner', index='Service', columns='type', aggfunc='count')


st.header('Service By Type')
st.dataframe(pivot, use_container_width=True)

left, middle_left, middle_right, right = st.columns(4)
left.metric('2022 Vacayzen TAXI', np.sum(pivot['2022 Vacayzen TAXI']))
middle_left.metric('Generic New Wave', np.sum(pivot['Generic New Wave']))
middle_right.metric('Vacayzen New Wave', np.sum(pivot['Vacayzen New Wave']))
right.metric('Yellow 360 YOLO', np.sum(pivot['Yellow 360 YOLO']))

st.download_button('DOWNLOAD SERVICE BY TYPE',pivot.to_csv(),'ServiceByType.csv',use_container_width=True)

st.header('Service By Type With Keywords')

keywords = ['CHAIN','CHAIN GUARD','CHAINGUARD','TIRE','PEDAL','PEDAL ARM','PEDALARM','HANDLEBAR','HANDLE BAR','AIR']
options = st.multiselect('Look for office notes containing the following terms:',keywords,keywords)

search = '|'.join(options)

def OfficeNoteContainsKeyword(row):
     for option in options:
         if option in str(row['Office Note']):
             return True
         
     return False

bar['hasKeyword'] = bar.apply(OfficeNoteContainsKeyword, axis=1)

key = bar[bar['hasKeyword']]
key = key[['partner','type','unit','order','date','Service','Office Note','Driver Note']]
pivot_key = pd.pivot_table(key, values='partner', index='Service', columns='type', aggfunc='count')

st.dataframe(pivot_key, use_container_width=True)

left, middle_left, middle_right, right = st.columns(4)
left.metric('2022 Vacayzen TAXI', np.sum(pivot_key['2022 Vacayzen TAXI']))
middle_left.metric('Generic New Wave', np.sum(pivot_key['Generic New Wave']))
middle_right.metric('Vacayzen New Wave', np.sum(pivot_key['Vacayzen New Wave']))
right.metric('Yellow 360 YOLO', np.sum(pivot_key['Yellow 360 YOLO']))

st.download_button('DOWNLOAD SERVICE BY TYPE WITH KEYWORDS',pivot_key.to_csv(),'ServiceByTypeWithKeywords.csv',use_container_width=True)

st.header('Dispatches with Keywords in Office Notes')
option_type = st.selectbox('Bike Type',key.type.unique())

key = key[key['type'] == option_type]
key = key[['Service','Office Note','Driver Note','date','partner','unit','order']]
key.columns = ['Service','Office Note','Driver Note','Date','Partner','Unit','Order']

st.dataframe(key, use_container_width=True)
st.download_button('DOWNLOAD DISPATCHES WITH KEYWORDS IN OFFICE NOTES',key.to_csv(),'DispatchesWithKeyWordsInOfficeNotes.csv',use_container_width=True)