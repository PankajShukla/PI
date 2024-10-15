# Assortment Analysis

import pandas as pd
import streamlit as st
import os
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px

from pathlib import Path
from zipfile import ZipFile
from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import requests
from io import BytesIO

from libraries import *
from charts import *
from transformation import *

from st_clickable_images import clickable_images



def streamlit_setup(_title, _description):
    st.set_page_config(page_title="Home", page_icon="👋", layout="wide")
    # st.markdown(f'<p style="color:#8B0000;font-size:50px;border-radius:2%;"> '+_title+'</p>', unsafe_allow_html=True)
    # st.markdown(f'<p style="color:#8B0000;font-size:20px;border-radius:2%;"> '+_description+'</p>', unsafe_allow_html=True)


def add_line():
    st.write("---")


def add_markdowns_side_by_side(dict):
    maxcols = 5
    stcols = st.columns(maxcols)
    i = 0 
    for k in list(dict.keys())[:maxcols]:
        v = dict[k]
        if i<3:
            _text1 = str(k) + " : "
            _text2 = str(v)
        else:
            _text1 = ''
            _text2 = ''
        stcols[i].markdown("""<p style='color:black;font-size:20px;border-radius:2%;text-align: center;'> <span style= 'color: black;'>"""+_text1+"""</span> <span style= 'color: coral;'>"""+_text2+"""</span> </p>  """, unsafe_allow_html=True)
        i=i+1


def data_initialise(filename):

    uploaded_file = st.sidebar.file_uploader("Upload data file (.csv format) ", type=["csv"])
    df_ = pd.read_csv(uploaded_file)
    df_['Category'] = df_['Category'].str.lower()
    df_ = df_[df_['Category'].str.lower()=='footwear']
    df_ = df_[df_['Sub-category']!='-']
    df_, subcat_list = get_sub_category(df_)
    df_ = get_product_type(df_, subcat_list)
    return df_


def pricing_initialise(df_, pricingfields):
    
    pricingfield_inp1 = pricingfields[0]
    pricingfield_oup1 = pricingfields[1]
    
    df_ = transfomLevel3(df_, pricingfield_inp1, pricingfield_oup1)
    df_percentile = get_stats(df_, pricingfield_oup1)

    return df_, df_percentile


def cluster_initialise(df_, df_percentile, clusterName, pricing_cluster_field, _pricerange):

    df_percentile[clusterName] = np.where(df_percentile[pricing_cluster_field].between(_pricerange[0],_pricerange[1]), 'Yes', 'No')
    
    AUR_cluster = list(df_percentile[df_percentile[clusterName]=='Yes']['Brand_D2C'].unique())
    df_[clusterName] = np.where(df_['Brand_D2C'].isin(AUR_cluster), 'Yes', 'No')

    return df_, df_percentile



def streamlit_sidebar_selections_A(df_):

    option0 = st.sidebar.multiselect("Category", options = df_['Category'].unique(), default = df_['Category'].unique())
    df_ = df_[df_['Category'].isin(option0)]
    
    option1 = st.sidebar.multiselect("Sub Category", options = df_['new_Sub-category'].unique(), default = df_['new_Sub-category'].unique())
    df_ = df_[df_['new_Sub-category'].isin(option1)]

    return df_


def streamlit_sidebar_selections_B(df_):

    option1 = st.sidebar.multiselect("AUR cluster", options = df_['AUR_cluster'].unique(), default = df_['AUR_cluster'].unique())
    df_ = df_[df_['AUR_cluster'].isin(option1)]

    option2 = st.sidebar.multiselect("Product Type", options = df_['new_Type'].unique(), default = df_['new_Type'].unique())
    df_ = df_[df_['new_Type'].isin(option2)]
    
    option3 = st.sidebar.multiselect("Brand", options = df_['Brand_D2C'].unique(), default = df_['Brand_D2C'].unique())
    df_ = df_[df_['Brand_D2C'].isin(option3)]

    return df_


def highlight_dataframe_cells(row):
    return ['background-color: #FFDBBB']*len(row) if row["AUR_cluster"]=='Yes' else ['background-color: #F9F9F9']*len(row)



def add_brand_image_to_scatter(fig, chart_df, context, measure_field, clusterName, add_vline='No'):
    
    brandLogo_path = Path.cwd().joinpath("brandLogo")
    jpgLogo_path = []
    for brandName in sorted(chart_df[context].unique()):
        jpgLogo_path.append(os.path.join(brandLogo_path, brandName + '.jpg' ))

    jpgLogo_path = sorted(jpgLogo_path)

    for x,y, jpg in zip(fig.data[0].x, fig.data[0].y, jpgLogo_path):
        fig.add_layout_image( x=x, y=y, source=Image.open(jpg), xref="x", yref="y", 
                             sizex=50, sizey=50, xanchor="center", yanchor="middle")

    if add_vline=='Yes':
        fig.add_vline(x=chart_df[chart_df[clusterName]=='Yes'][measure_field].min(), line_width=1, line_color="coral", line_dash="dash")
        fig.add_vline(x=chart_df[chart_df[clusterName]=='Yes'][measure_field].max(), line_width=1, line_color="coral", line_dash="dash")
        
    return fig



def plot_images_side_by_side(image_paths):
    num_images = len(image_paths)
    fig, axes = plt.subplots(1, num_images, figsize=(20, 6))  # Adjust figsize as needed
    for i, img_path in enumerate(image_paths):
        img = mpimg.imread(img_path)
        axes[i].imshow(img)
        axes[i].axis('off')
    return fig


def plot_image_snapshot(image_urls):

    fig, axes = plt.subplots(6, 5, figsize=(30, 22.5))
    axes = axes.ravel()

    for i, url in enumerate(image_urls):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((500, 500))  # Resize image for better display
        axes[i].imshow(img)
        axes[i].axis('off')
    
    return fig




def show_product_image_and_URL(df_, col1, col2, product_image):
    

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.1.234133065.1727358599; FPID=FPID2.2.7cW3yPvHEDP6McIG5yeYBbffxJX5xrW9RrTSoFTxS28%3D.1727358599; FPAU=1.2.381647108.1727358600; _fbp=fb.1.1727358599333.470456281805687223; _tt_enable_cookie=1; _ttp=GsE9ozb7NjZCVQqljGxi9lnujgl; _hjSessionUser_4982743=eyJpZCI6IjQ0MjRiNGNmLTVmYzAtNWUwNC05NjFmLTVkZGFmYTJlYWNiNSIsImNyZWF0ZWQiOjE3MjczNTg1OTkzOTIsImV4aXN0aW5nIjp0cnVlfQ==; __stripe_mid=61321cf4-3ad4-4e64-b20b-ec5eaee64f0dcd09bc; CookieScriptConsent={"action":"accept","consenttime":1718188349,"categories":"[\\"targeting\\"]"}; cf_clearance=nUXwKjQcYBXOiVjk5pcgeOfZTSxLoFJbG.dHW6FLr7I-1727523934-1.2.1.1-8p5KX747gzS5l.3MJEsE5m6QkBFosjAZDGp5ZMs4OWxupr3.HU_xnjxxXYSkFfqxShwNJqNPU7JZFpQeEy_sBvwq0MkTQNuiTlwpI7P1IXzZ7QBlrw9Jmfn0SVop7XtNvawCqXwZnf.m6tpimNW2TbFqxlbq5gCN2.EvM_36TM8c0EZ5LjeXp8TiTZ1ifzOA9JQz1dHkVBS6aOfb3Lc9u_wDQKmrKQ80C__gV_M8beRV3.2EfIktTgCZkiFKViLx.l3Uy3GZ7sCYRbQ4VpU7IegbkIFQr9JlL288GC7QuF9c_oGuGaS4wwiLKD6kRHVvly7AVtNElpOe.oQOKGuO5KQqmEhDnA5D6ATZiKYDr4VxMH8Ab6qzfRdWLOp0TKvZ; _uetvid=38a161f07c0e11efb54eabde2fc23a4d; cCount=51; _ga_8DC50N5KHH=GS1.1.1727522441.6.1.1727523956.0.0.934915884',
        'if-modified-since': 'Wed, 31 Jan 2024 15:29:35 GMT',
        'if-none-match': '"3ca03-6103f8bd41453"',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }
    
    stcol1,stcol2  = st.columns(2)
    
    with stcol1:
        with st.container(height=800):
            clicked = clickable_images(
                product_image,
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "width": "20%", "height": "20%"},
            )

    with stcol2:
        with st.container(height=800):
            fig, axes = plt.subplots(1, 1, figsize=(10, 10))
    
            image_selected = product_image[clicked]
            URL = df_[df_[col1]==image_selected][col2].unique()[0]
            
            link_text = "Click here to view the product on the website"
            st.markdown(f'<a href="{URL}" target="_blank" style="font-size:15px;">{link_text}</a>', unsafe_allow_html=True)
            
            response = requests.get(image_selected, headers=headers)
            img = Image.open(BytesIO(response.content))
            axes.imshow(img)
            axes.axis('off')
            st.pyplot(fig)










