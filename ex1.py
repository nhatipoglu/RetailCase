import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

# Veriyi yükleyelim
df = pd.read_csv('data/year_2009_2010.csv',encoding='latin1')

# Veri ön işleme
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Customer ID'] = df['Customer ID'].astype('str')

# RFM metriklerini hesaplamak için bugünkü tarihi belirleyelim
today_date = df['InvoiceDate'].max() + dt.timedelta(days=1)

# RFM metriklerini hesaplayalım
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda date: (today_date - date.max()).days,
    'Invoice': 'nunique',
    'Price': 'sum'
})

# Kolon isimlerini değiştirelim
rfm.columns = ['Recency', 'Frequency', 'Monetary']

# RFM puanlarını hesaplayalım
rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

# RFM skoru hesaplayalım
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

# Segmentlere ayıralım
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[3-4][1-2]': 'At Risk',
    r'[4-5][4-5]': 'Champions',
    r'[3-4][3-4]': 'Loyal Customers',
    r'[1-2][4-5]': 'New Customers'
}

rfm['Segment'] = rfm['R'].astype(str) + rfm['F'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

# Segment dağılımını görselleştirelim
plt.figure(figsize=(12,8))
sns.countplot(x='Segment', data=rfm, order=rfm['Segment'].value_counts().index)
plt.title('Customer Segments')
plt.xlabel('Segment')
plt.ylabel('Number of Customers')
plt.show()

# Segment bazında ortalama RFM metriklerini hesaplayalım
segment_metrics = rfm.groupby('Segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': ['mean', 'count']
}).round(1)

segment_metrics.columns = ['RecencyMean', 'FrequencyMean', 'MonetaryMean', 'Count']
print(segment_metrics)
