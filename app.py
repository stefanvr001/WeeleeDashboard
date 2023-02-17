import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('matplotlib')

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os
# np.set_printoptions(suppress=True) # Use the full page instead of a narrow central column 
# st.set_page_config(layout="wide") 

st.header('Enter the vehicle details')

@st.cache_data
def load_data(path):
    # path=r'C:\Users\VA5006\Documents\Python\Weelee\New Model\Output\scraped_car_unique.csv'
    dataset=pd.read_csv(path)


    dataset.BestMatchRetail=dataset.BestMatchRetail.astype(float)
    dataset.price=dataset.price.astype(float)
    dataset.mileage=dataset.mileage.astype(float)
    dataset.Appearance=dataset.Appearance.astype(float)

    dataset.price_ave=dataset.price_ave.apply(lambda x: np.round(float(x),0))
    dataset.mileage_ave=dataset.mileage_ave.astype(float).apply(lambda x: np.round(float(x),0))
    dataset.Appearance_ave=dataset.Appearance_ave.astype(float).apply(lambda x: np.round(float(x),0))

    dataset.price_med=dataset.price_med.apply(lambda x: np.round(float(x),0))
    dataset.mileage_med=dataset.mileage_med.astype(float).apply(lambda x: np.round(float(x),0))
    dataset.Appearance_med=dataset.Appearance_med.astype(float).apply(lambda x: np.round(float(x),0))

    dataset.BestMatchRetail=dataset.BestMatchRetail.apply(lambda x: np.round(float(x),0))
    dataset.BestMatchTrade=dataset.BestMatchTrade.apply(lambda x: np.round(float(x),0))

    return dataset


path=os.getcwd()
path2=path+'\\Output\\scraped_car_unique.csv'
# os.chdir(path2)

raw=load_data(path2)
# raw=load_data(r'C:\Users\VA5006\Documents\Python\Weelee\New Model\Output\scraped_car_unique.csv')
# avocado_stats = raw.loc[raw['title']]
# st.dataframe(avocado_stats)


with st.form(key='selections'):

    # raw=dataset.copy()
    veh_values=list(raw['BestMatch'].unique())
    veh_values.sort()
    veh_values_default=veh_values.index(raw['BestMatch'].value_counts().index[0])

    # veh_values=list(raw['title'].unique())
    # veh_values.sort()
    # veh_values_default=veh_values.index(raw['title'].value_counts().index[0])

    ld_values=list(raw['issuedate'].unique())
    ld_values.sort()
    ld_values=[str(i) for i in ld_values]
    ld_values_default=str(raw['issuedate'].min())
    ld_values_default2=str(raw['issuedate'].max())

    selected_veh = st.selectbox(label='Vehicle', options=veh_values, index=veh_values_default)
    # selected_list_date_min = st.selectbox(label='ld_min', options=ld_values, index=ld_values_default)
    # selected_list_date_max = st.selectbox(label='ld_max', options=ld_values, index=ld_values_default2)
    # selected_province = st.selectbox(label='province', options=raw['province'].unique())

    submitted = st.form_submit_button('Submit')

    if submitted:

        # filtered_raw=raw.loc[(raw['title']==raw['title'].value_counts().index[0]),]
        # filtered_raw.sort_values(['price'])['price'].apply(int)

        # filtered_raw=raw.loc[(raw['title']==raw['title'].value_counts().index[0]),]
        filtered_raw=raw.loc[(raw['BestMatch']==selected_veh),]
        # filtered_raw=filtered_raw.loc[(filtered_raw['BestMatchDistance']<=0.5),]
        filtered_raw=filtered_raw.loc[(filtered_raw['BestMatchDistance']<=0.1),]
        filtered_raw=filtered_raw.loc[(filtered_raw['used'].apply(str)=='True'),]

        # filtered_raw=raw.loc[(raw['title']==selected_veh),]
        # filtered_raw = raw.loc[(raw['title']==selected_veh) & (raw['issuedate']>=int(selected_list_date_min)) & (raw['issuedate']<=int(selected_list_date_max)),]

        last_3m=list(filtered_raw['issuedate'].unique())
        last_3m.sort(reverse=True)
        last_3m=last_3m[0:3]

        site_col={'cars.co.za':'red',
                    'WeBuyCars':'orange',
                    'AutoTrader':'lightblue'
                    }

        filtered_raw['site_col']=filtered_raw.site_name.apply(lambda x: site_col[x] if x in site_col.keys() else 'black')

        # st.header("M&M Code: "+str(filtered_raw['']))
        st.header("Summary Statistics")
        filtered_raw_agg=filtered_raw.groupby(['issuedate','price_ave','price_med','mileage_ave','mileage_med'],as_index=False)['car_id'].count()
        filtered_raw_agg.columns=['Listing Period','Ave Price','Median Price','Ave Mileage','Med Mileage','Sample']
        filtered_raw_agg['Listing Period']=filtered_raw_agg['Listing Period'].apply(str)
        st.dataframe(filtered_raw_agg)

        st.header("Market vs TransUnion")
        filtered_raw_agg2=filtered_raw.groupby(['issuedate','price_ave','price_med'],as_index=False)['BestMatchRetail','BestMatchTrade'].mean()
        filtered_raw_agg2.columns=['Listing Period','Ave Price','Median Price','TU Retail','TU Trade']
        filtered_raw_agg2['Listing Period']=filtered_raw_agg2['Listing Period'].apply(str)
        st.dataframe(filtered_raw_agg2)

        filtered_raw2=filtered_raw.loc[filtered_raw.mileage>10,]

        # LAST 3 MONTH SUBSET
        filtered_raw_agg_3m=filtered_raw_agg.loc[filtered_raw_agg['Listing Period'].apply(int).isin(last_3m),]
        filtered_raw_agg2_3m=filtered_raw_agg2.loc[filtered_raw_agg2['Listing Period'].apply(int).isin(last_3m),]
        filtered_raw2_3m=filtered_raw2.loc[filtered_raw2['issuedate'].apply(int).isin(last_3m),]

        global_ave=(filtered_raw_agg_3m['Ave Price']*filtered_raw_agg_3m['Sample']).sum()/filtered_raw_agg_3m['Sample'].sum()
        global_ave2=(filtered_raw_agg_3m['Ave Mileage']*filtered_raw_agg_3m['Sample']).sum()/filtered_raw_agg_3m['Sample'].sum()

        global_ave_TUR=filtered_raw_agg2_3m['TU Retail'].mean()
        global_ave_TUT=filtered_raw_agg2_3m['TU Trade'].mean()


        import matplotlib.ticker as ticker

        st.header("Price by Mileage Plot")
        sns.set(rc={'figure.figsize':(12,12)})
        filtered_raw2_3m_fix=filtered_raw2_3m.copy()
        filtered_raw2_3m_fix['R Value (Thousands)']=filtered_raw2_3m_fix.price//1000
        filtered_raw2_3m_fix.Mileage=filtered_raw2_3m_fix.mileage
        g=sns.jointplot(x="R Value (Thousands)",y="mileage",data=filtered_raw2_3m_fix,kind='reg',scatter=True)
        g.ax_joint.scatter(x="R Value (Thousands)",y="mileage",data=filtered_raw2_3m_fix,c=filtered_raw2_3m_fix.site_col)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave//1000, color='black', ls='--', lw=3)
        for ax in (g.ax_joint, g.ax_marg_y):
            ax.axhline(global_ave2, color='black', ls='--', lw=3)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave_TUR//1000, color='olive', ls='--', lw=3)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave_TUT//1000, color='olive', ls='--', lw=3)        
        # plt.show()
        st.pyplot(g)

        # st.header("Price by Mileage Plot")
        # sns.set(rc={'figure.figsize':(12,12)})
        # g=sns.jointplot(y="price",x="mileage",data=filtered_raw2_3m,kind='reg',scatter=True)
        # g.ax_joint.scatter(y="price",x="mileage",data=filtered_raw2_3m,c=filtered_raw2_3m.site_col)
        # g.set_xticklabels(g.get_xticklabels(), rotation=45, horizontalalignment='right')
        # for ax in (g.ax_joint, g.ax_marg_y):
        #     ax.axhline(global_ave, color='black', ls='--', lw=3)
        # for ax in (g.ax_joint, g.ax_marg_x):
        #     ax.axvline(global_ave2, color='black', ls='--', lw=3)
        # for ax in (g.ax_joint, g.ax_marg_y):
        #     ax.axhline(global_ave_TUR, color='olive', ls='--', lw=3)
        # for ax in (g.ax_joint, g.ax_marg_y):
        #     ax.axhline(global_ave_TUT, color='olive', ls='--', lw=3)        
        # st.pyplot(g)

        filtered_raw2_3m_sorted=filtered_raw2_3m.sort_values(['price'])
        filtered_raw2_3m_sorted=filtered_raw2_3m_sorted.reset_index()
        del filtered_raw2_3m_sorted['index']
        filtered_raw2_3m_sorted['Rank']=filtered_raw2_3m_sorted.index
        filtered_raw2_3m_sorted['Percentile']=filtered_raw2_3m_sorted.index/filtered_raw2_3m_sorted.shape[0]*100

        filtered_raw2_3m_sorted_fix=filtered_raw2_3m_sorted.copy()
        filtered_raw2_3m_sorted_fix['R Value (Thousands)']=filtered_raw2_3m_sorted_fix.price//1000
        filtered_raw2_3m_sorted_fix.Mileage=filtered_raw2_3m_sorted_fix.mileage

        st.header("Ranking Plot")
        sns.set(rc={'figure.figsize':(12,12)})
        g=sns.jointplot(x="R Value (Thousands)",y="Percentile",data=filtered_raw2_3m_sorted_fix)
        g.ax_joint.scatter(x="R Value (Thousands)",y="Percentile",data=filtered_raw2_3m_sorted_fix,c=filtered_raw2_3m_sorted_fix.site_col)
        g.ax_marg_y.set_ylim(0, 100)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave//1000, color='black', ls='--', lw=3)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave_TUR//1000, color='olive', ls='--', lw=3)
        for ax in (g.ax_joint, g.ax_marg_x):
            ax.axvline(global_ave_TUT//1000, color='olive', ls='--', lw=3)        
        # plt.show()
        st.pyplot(g)

        st.header("Ranking Table")
        filtered_raw2_3m_sorted['Decile']=(filtered_raw2_3m_sorted['Percentile']//10)+1
        filtered_raw2_3m_sorted_agg=filtered_raw2_3m_sorted.groupby(['Decile'],as_index=False)['price'].mean()
        filtered_raw2_3m_sorted_agg['price']=filtered_raw2_3m_sorted_agg['price'].apply(lambda x: np.round(x,0))
        filtered_raw2_3m_sorted_agg.columns=['Decile','Ave Price']
        # filtered_raw2_3m_sorted_agg['Ave Price']=filtered_raw2_3m_sorted_agg['Ave Price']//1000
        st.dataframe(filtered_raw2_3m_sorted_agg)


        # TIME LISTED
        filtered_raw3_sorted=filtered_raw.copy()
        filtered_raw3_sorted['TimeOnline']=(pd.to_datetime(filtered_raw3_sorted['ScrapeDate'])-pd.to_datetime(filtered_raw3_sorted['date_listing'])).dt.days
        filtered_raw3_sorted['Sold']=(pd.to_datetime(filtered_raw3_sorted['ScrapeDate'])<pd.to_datetime(datetime.today()-timedelta(2))).apply(int)
        filtered_raw3_sorted=filtered_raw3_sorted.loc[filtered_raw3_sorted['Sold']==1,]

        filtered_raw3_sorted=filtered_raw3_sorted.sort_values(['price'])
        filtered_raw3_sorted=filtered_raw3_sorted.reset_index()
        del filtered_raw3_sorted['index']
        filtered_raw3_sorted['Rank']=filtered_raw3_sorted.index
        filtered_raw3_sorted['Percentile']=filtered_raw3_sorted.index/filtered_raw3_sorted.shape[0]*100
        filtered_raw3_sorted['Decile']=(filtered_raw3_sorted['Percentile']//10)+1

        # filtered_raw3_sorted_agg=filtered_raw3_sorted.groupby(['Decile'],as_index=False)['TimeOnline'].median()
        filtered_raw3_sorted_agg=filtered_raw3_sorted.groupby(['Decile'],as_index=False)['TimeOnline','price'].mean()
        filtered_raw3_sorted_agg['Decile']=filtered_raw3_sorted_agg['Decile'].apply(int)
        filtered_raw3_sorted_agg['TimeOnline']=filtered_raw3_sorted_agg['TimeOnline'].apply(int)
        filtered_raw3_sorted_agg['price']=filtered_raw3_sorted_agg['price']//1000*1000
        filtered_raw3_sorted_agg.columns=['Decile','TimeOnline','Ave Price']

        st.header("Days Online by Price Decile Plot")
        g2,ax=plt.subplots()
        ax=sns.regplot(x="Decile",y="TimeOnline",data=filtered_raw3_sorted_agg)
        st.pyplot(g2)

        st.header("Days Online by Price Decile Table")
        st.dataframe(filtered_raw3_sorted_agg)

        st.header("Raw Data Table")
        filtered_raw2['issuedate']=pd.to_datetime(filtered_raw2['issuedate'])
        filtered_raw4=filtered_raw2.sort_values(['issuedate','price'],ascending=[False,False])
        filtered_raw4=filtered_raw4[['car_id','date_listing','price','mileage','site_name','province','dealer_name','title','BestMatchDistance']]
        filtered_raw4.columns=['Car ID','List Date','Price','Mileage','Site','Province','Dealer','Title','BestMatchDistance']
        st.dataframe(filtered_raw4)









### END