import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def get_top_payment_methods(df):
    result = df.groupby('payment_type')['order_id'].nunique().reset_index(name='jumlah_transaksi')
    top_payment_methods = result.sort_values('jumlah_transaksi', ascending=False)
    return top_payment_methods

def get_top_selling_categories(df):
    result = df.groupby('product_category_name')['product_id'].nunique().reset_index(name='jumlah_penjualan')
    top_categories = result.sort_values('jumlah_penjualan', ascending=False).head(5)
    return top_categories

def get_review_distribution(df):
    result = df.groupby('review_score')['review_id'].nunique().reset_index(name='jumlah_ulasan')
    return result.sort_values('review_score', ascending=True)

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_byzipcode_df(df):
    byzipcode_df = df.groupby(by="customer_zip_code_prefix").customer_id.nunique().reset_index()
    byzipcode_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

def create_rfm_metrics(df):
    rfm_df = df.groupby('customer_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
    recent_date = df['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].dt.date.apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    return rfm_df

def plot_review_distribution(df):
    result = get_review_distribution(df)
    sns.barplot(x='review_score', y='jumlah_ulasan', data=result, palette='viridis')
    plt.title('Distribusi Ulasan Berdasarkan Skor')
    plt.xlabel('Skor Ulasan')
    plt.ylabel('Jumlah Ulasan')
    plt.xticks(rotation=45)
    plt.show()

all_df = pd.read_csv("./all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]
    

daily_orders_df = create_daily_orders_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)
byzipcode_df = create_byzipcode_df(main_df)
rfm_df = create_rfm_metrics(main_df)
top_payment = get_top_payment_methods(main_df)
top_selling = get_top_selling_categories(main_df)
top_rating = get_review_distribution(main_df)
rate_graph = plot_review_distribution(main_df)

st.header('Marketplace Dashboard :sparkles:')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='en_US') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

#---------------------------------------Soal 2----------------------------------------------------#
st.subheader("Top Payment Method")

result = all_df.groupby('payment_type')['order_id'].nunique().reset_index(name='jumlah_transaksi')

method_payment = result.sort_values(by='jumlah_transaksi', ascending=False).head(5)
fig, ax = plt.subplots(figsize=(16, 8))

top_payment = method_payment.iloc[0]['payment_type']
colors = ['red' if x == top_payment else 'gray' for x in method_payment['payment_type']]
 
sns.barplot(x='payment_type', y='jumlah_transaksi', data=method_payment, palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("count", fontsize=20)
ax.set_title("Best Payment Method", loc="center", fontsize=25)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
 
st.pyplot(fig)

#---------------------------------------Soal 3-------------------------------------------#
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 20))
 
result = all_df.groupby('product_category_name')['product_id'].nunique().reset_index(name='jumlah_penjualan')

top_5 = result.sort_values(by='jumlah_penjualan', ascending=False).head(5)

top_product = top_5.iloc[0]['product_category_name']

colors = ['red' if x == top_product else 'gray' for x in top_5['product_category_name']]

sns.barplot(x='jumlah_penjualan', y='product_category_name', data=top_5, palette=colors, ax=ax[0])
ax[0].set_xlabel("Number of Sales", fontsize=45)
ax[0].set_ylabel(None) 
ax[0].set_title("Best Performing Product", loc="center", fontsize=65)
ax[0].tick_params(axis='y', labelsize=45)
ax[0].tick_params(axis='x', labelsize=45)


worst_5 = result.sort_values(by="jumlah_penjualan", ascending=True).head(5) 

sns.barplot(x='jumlah_penjualan', y='product_category_name', data=worst_5, ax=ax[1], palette=colors) 
ax[1].set_xlabel("Number of Sales", fontsize=45) 
ax[1].set_ylabel(None) 
ax[1].invert_xaxis() 
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=65)
ax[1].tick_params(axis='y', labelsize=45)
ax[1].tick_params(axis='x', labelsize=45)

st.pyplot(fig)

#------------------------------------------Soal 4--------------------------------------------#
st.subheader("Customer Demographics")
 
col1, col2 = st.columns(2)
 
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    city = all_df.groupby('customer_city')['customer_id'].nunique().reset_index(name='jumlah_pelanggan')

    top = city.sort_values('jumlah_pelanggan', ascending=False).head(5)

    top_city = top.iloc[0]['customer_city']

    colors = ['red' if x == top_city else 'gray' for x in top['customer_city']]
 
    sns.barplot(
        y="jumlah_pelanggan", 
        x="customer_city",
        data=top,
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by City", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    zip_code = all_df.groupby('customer_zip_code_prefix')['customer_id'].nunique().reset_index(name='jumlah_pelanggan')

    top = zip_code.sort_values('jumlah_pelanggan', ascending=False).head(5)

    top_zip_code = top.loc[top['jumlah_pelanggan'].idxmax(), 'customer_zip_code_prefix']

    top['customer_zip_code_prefix'] = top['customer_zip_code_prefix'].astype(str)
    top_zip_code = str(top_zip_code)

    colors = ['red' if str(x) == top_zip_code else 'gray' for x in top['customer_zip_code_prefix']]
 
    sns.barplot(
        y="jumlah_pelanggan", 
        x="customer_zip_code_prefix",
        data=top,
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Zip Code", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
 
fig, ax = plt.subplots(figsize=(20, 10))

state = all_df.groupby('customer_state')['customer_id'].nunique().reset_index(name='jumlah_pelanggan')

top = state.sort_values('jumlah_pelanggan', ascending=False).head(10)

top_state = top.iloc[0]['customer_state']

colors = ['red' if x == top_state else 'gray' for x in top['customer_state']]

sns.barplot(
    x="jumlah_pelanggan", 
    y="customer_state",
    data=top,
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#-----------------------------------------Soal  5----------------------------------------------#
st.subheader("Top Rated")

result = all_df.groupby('review_score')['review_id'].nunique().reset_index(name='jumlah_ulasan')

rated = result.sort_values('jumlah_ulasan', ascending=True)

top_rated_scores = rated[rated['jumlah_ulasan'] == rated['jumlah_ulasan'].max()]['review_score'].tolist()

colors = ['red' if x in top_rated_scores else 'gray' for x in rated['review_score']]

fig, ax = plt.subplots(figsize=(16, 8))
 
sns.barplot(x='review_score', y='jumlah_ulasan', data=rated, palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("count", fontsize=20)
ax.set_title("Top Rated", loc="center", fontsize=25)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
 
st.pyplot(fig)

#-----------------------------------------------RFM---------------------------------------------#
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "USD", locale='en_US') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.nlargest(5, 'recency'), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=90)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Raihan Dwi Win Cahya 2025')