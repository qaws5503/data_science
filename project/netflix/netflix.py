# %%
import numpy as np
import pandas as pd
import pandas_profiling
import plotly.express as px
import plotly.graph_objects as go

# %%
df = pd.read_csv("netflix_titles.csv")
#profile = pandas_profiling.ProfileReport(df)
#profile.to_file("output.html")
# %%
df.info()
# %%
df.isna().sum()
# %%
df = df.drop(["director","cast"],axis=1)
# %%
df = df[df['rating'].notna()]
df = df[df['date_added'].notna()]
df['country'] = df['country'].fillna(df['country'].mode()[0])
df.info()
df.isna().sum()
# %% Splite date to year, month and date
df['year_added'] = df['date_added'].apply(lambda x: x.split(" ")[-1])
df['year_added'].head()

# %%
df['month_added'] = df['date_added'].apply(lambda x: x.split(" ")[0])
df['month_added'].head()

# %% change rating to ages
ratings_ages = {
    'TV-PG': 'Older Kids',
    'TV-MA': 'Adults',
    'TV-Y7-FV': 'Older Kids',
    'TV-Y7': 'Older Kids',
    'TV-14': 'Teens',
    'R': 'Adults',
    'TV-Y': 'Kids',
    'NR': 'Adults',
    'PG-13': 'Teens',
    'TV-G': 'Kids',
    'PG': 'Older Kids',
    'G': 'Kids',
    'UR': 'Adults',
    'NC-17': 'Adults'
}
df['target_ages'] = df['rating'].replace(ratings_ages)
df['target_ages'].unique()

# %%
# Lets retrieve just the first country
df['principal_country'] = df['country'].apply(lambda x: x.split(",")[0])
df['principal_country'].head()

# %%
# type should be a category
df['type'] = pd.Categorical(df['type'])
# target_ages is another category (4 classes)
df['target_ages'] = pd.Categorical(df['target_ages'], categories=['Kids', 'Older Kids', 'Teens', 'Adults'])

# Year added should be integer so we can compare with `released_year`
df['year_added'] = pd.to_numeric(df['year_added'])
df.info()

# %%
df.head()

# %%
df['genre'] = df['listed_in'].apply(lambda x :  x.replace(' ,',',').replace(', ',',').split(',')) 
df['genre'].head()
# %%
fig = px.pie(df['type'].value_counts().reset_index(), values='type', names='index', title='netflix 作品類別比例')
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()
# %%
def generate_rating_df(df):
    rating_df = df.groupby(['rating', 'target_ages']).agg({'show_id':'count'}).reset_index()
    rating_df = rating_df[rating_df['show_id'] != 0]
    rating_df.columns = ['rating', 'target_ages', 'counts']
    rating_df = rating_df.sort_values('target_ages')
    return rating_df

rating_df = generate_rating_df(df)
fig = px.bar(rating_df, x='rating', y='counts', color='target_ages', title='年齡層分布狀況')
fig.show()
# %%
# country by pie
country_df = df['principal_country'].value_counts().reset_index()
country_df = country_df[country_df['principal_country'] /  country_df['principal_country'].sum() > 0.01]

fig = px.pie(country_df, title='按國別分類 netflix 影視作品', values='principal_country', names='index')
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()
# %%
# country by histogram
fig = px.histogram(df, x='principal_country')
fig.update_xaxes(categoryorder='total descending')
fig.show()
# %%
from wordcloud import WordCloud
import matplotlib.pyplot as plt
movie_df = df[df['type'] == 'Movie']
text = str(list(movie_df['genre'])).replace(',', '').replace('[', '').replace("'", '').replace(']', '')

plt.rcParams['figure.figsize'] = (15, 15)
wordcloud = WordCloud(background_color = 'white', width = 1200,  height = 1200, max_words = 121).generate(text)
plt.imshow(wordcloud)
plt.axis('off')
plt.savefig('wordcloud.png')
plt.show()
# %%
