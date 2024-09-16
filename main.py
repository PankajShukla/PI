# Product Intelligence Application

import pandas as pd
import streamlit as st
import os
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px

def streamlit_setup(_title, _description):
    # -------------------------------------------------
    # Set up for streamlit
    # -------------------------------------------------
    st.set_page_config(page_title="Home", page_icon="👋", layout="wide")
    st.markdown(f'<p style="color:#9bdaf1;font-size:50px;border-radius:2%;"> '+_title+'</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#d6d7d9;font-size:20px;border-radius:2%;"> '+_description+'</p>', unsafe_allow_html=True)


def display_chart(df1, _description, x, y, z, w, v):
    if df1.empty is False:
        st.markdown(f'<p style="color:#9bdaf1;font-size:20px;border-radius:2%;"> ' + _description + '</p>', unsafe_allow_html=True)
        fig = px.scatter(df1, x=x, y=y, size=z, color=v, size_max=40,
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(autosize=False, height=650)
        fig.update_traces(marker=dict(symbol=w))
        st.plotly_chart(fig, use_container_width=True)
        add_line()


def get_selection_list(tempdf, col):
    select_list = tempdf[col].unique()
    return select_list

def filter_data(tempdf, filter_col, filter_val):
    filtered_data = tempdf[tempdf[filter_col]==filter_val]
    return filtered_data

def transform_data(tempdf, group_by_col_list, measure_col1, measure_col2, _func, derived_field=None):
    if _func == 'sum':
        transformed_data = tempdf.groupby(group_by_col_list)[measure_col1].sum().reset_index()
    elif _func == 'distinct count':
        transformed_data = tempdf.groupby(group_by_col_list)[measure_col1].nunique().reset_index()
    elif _func == 'weighted_mean':
        mean_price_field = 'Mean Price'
        tempdf[mean_price_field] = tempdf[measure_col1]*tempdf[measure_col2]
        transformed_data = tempdf.groupby(group_by_col_list)[measure_col1, mean_price_field].sum().reset_index()
        transformed_data[mean_price_field] = transformed_data[mean_price_field]/transformed_data[measure_col1]
        derived_field = mean_price_field
    else:
        pass

    return transformed_data, derived_field

def add_line():
    st.write("---")

def brand_comparison():
    print("None")


def upload_data():

    c3, c4 = st.columns(2)
    with c3:
        try:
            uploaded_file = st.file_uploader("Upload data ", type=["xlsx"])
            df1 = pd.read_excel(uploaded_file, sheet_name='Sheet1')
            df2 = pd.read_excel(uploaded_file, sheet_name='Sheet2')
            df3 = pd.read_excel(uploaded_file, sheet_name='Sheet3')
        except:
            df1 = pd.DataFrame()
            df2 = pd.DataFrame()
            df3 = pd.DataFrame()

    with c4:
        st.empty()

    # if df1.empty is False or df2.empty is False or df3.empty is False:
    #     st.dataframe(df1.head(3))
    #     st.dataframe(df2.head(3))
    #     st.dataframe(df3.head(3))

    return df1, df2, df3


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    streamlit_setup(_title="Product Intelligence",
                    _description="Learn Brands assortment and Product Differentiation Factors")
    add_line()

    df1, df2, df3 = upload_data()
    add_line()

    # SECTION 1
    display_chart(df1, _description="A. Brand Assortment Comparison", x='Brand', y='sub_category', z='product_count', w='circle', v='Brand')



    # SECTION 2
    try:
        select_column1 = "sub_category"
        select_column1_list = get_selection_list(df2, select_column1)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_column1 = st.selectbox(label='Select Sub Category', options=select_column1_list)

        dft2 = filter_data(df2, filter_col=select_column1, filter_val=selected_column1)
        display_chart(dft2, _description="B. Brand Differentiation Comparison", x='Brand', y='differentiation_factor',
                      z='product_count', w='circle-open-dot', v='Brand')
    except:
        pass



    # SECTION 3

    try:
        select_column1 = "sub_category"
        select_column2 = "differentiation_factor"
        select_column1_list = get_selection_list(df3, select_column1)
        select_column2_list = get_selection_list(df3, select_column2)

        col1a, col2a, col3a, col4a = st.columns(4)
        with col1a:
            selected_column1 = st.selectbox(label='Select Sub Category', options=select_column1_list)
        with col2a:
            selected_column2 = st.selectbox(label='Select differentiation factor', options=select_column2_list)

        dft3 = filter_data(df3, filter_col=select_column1, filter_val=selected_column1)
        dft3 = filter_data(dft3, filter_col=select_column2, filter_val=selected_column2)

        derived_field_input = 'Mean Price (USD)'
        dft3, derived_field_output = transform_data(dft3, group_by_col_list=[select_column1, select_column2, 'Brand'],
                                             measure_col1='product_count' ,measure_col2='Price (usd)', _func='weighted_mean',
                                             derived_field = derived_field_input
                                             )
        display_chart(dft3, _description="C. Sub Category and Differentiation : Brand Pricing Comparison", x=derived_field_output, y='Brand',
                      z='product_count', w='circle-dot', v='Brand')
    except:
        pass



