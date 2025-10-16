#!/usr/bin/env python
# coding: utf-8

# # Update master_df
# 
# <p>
# This script will update the master_df.csv created in the corporatelobbying.ipynb script <br>
# and then overwrite the master_df.csv.
# </p>

# ### Import libraries

# In[1]:


import pandas as pd
import requests
from selenium import webdriver
import lxml
import schedule
import pyautogui
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dateutil import parser
import datetime as dt


# ### Load in master_df.csv

# In[2]:


df_master = pd.read_csv(r'C:\Users\ronan\Projects\master_df.csv', parse_dates=['Date'], dayfirst=True)


# In[3]:


end_date = dt.date.today() - dt.timedelta(days=1)
end_date = pd.to_datetime(end_date)

start_date = pd.to_datetime(df_master['Date'].iloc[0]) + dt.timedelta(days=1)


# In[4]:


print(start_date)
print(end_date)


# ### Get the data

# In[5]:


response = requests.get('https://www.quiverquant.com/lobbying/')

print(response.status_code) #this prints the code (200 is success)

print(response.content) #this prints the raw HTML output


# In[6]:


soup = BeautifulSoup(response.content, 'html.parser')

raw_data=[]
content_div = soup.find('div', class_='table-inner')
if content_div:
    for tds in content_div.find_all('td'):
        raw_data.append(tds.text.strip())
else:
    print("No article content found")


# In[7]:


#create an empty list to store dictionaries
records = []

#loop over raw_data in chunks of 3 at a time
#this is because for one entry it is ticker \n company, amount, date
for i in range(0, len(raw_data), 3):
    #split the first item into ticker and company name
    #it is separated by \n so that is how I can differentiate
    ticker_company = raw_data[i].split('\n', 1)

    #first part is the ticker
    ticker = ticker_company[0].strip()

    #second part is company name
    company = ticker_company[1].strip() if len(ticker_company) > 1 else ""

    #clean up the amount to remove $ and , and then convert to int
    amount = int(raw_data[i+1].replace("$", '').replace(",", "").strip())

    full_date_str = raw_data[i+2].strip()        # this is a STRING now
    parts = full_date_str.split(",")             # safe to split
    date_part = (parts[0] + " " + parts[1]).strip()
    date_obj = parser.parse(date_part)           # flexible parsing
    date_fmt = date_obj.strftime("%d/%m/%Y")

    #append cleaned record as a dictionay to records list
    records.append({
        'Ticker':ticker,
        'Company Name': company.title(),
        'Amount':amount,
        'Date':date_fmt
    })

    df_update = pd.DataFrame(records)
    df_update['Date'] = pd.to_datetime(df_update['Date'], dayfirst=True)


# ### Update the dataframe

# In[8]:


df_update = df_update[(df_update['Date'] >= start_date) & (df_update['Date'] <= end_date)]


# In[10]:


df_update


# ### Concat the old master with new updated data after the date set

# In[11]:


df_new = pd.concat([df_master, df_update], ignore_index=True)
df_new['Date'] = pd.to_datetime(df_new['Date'])
df_new = df_new.sort_values('Date', ascending=False).reset_index(drop=True)


# In[13]:


df_new.head(50)


# ### Save updated master_df.csv

# In[14]:


df_new.to_csv('master_df.csv', index=False)


# In[ ]:




