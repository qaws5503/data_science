# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
# %%
df1 = pd.read_csv("A_lvr_land_A.csv")
df2 = pd.read_csv("B_lvr_land_A.csv")
df3 = pd.read_csv("E_lvr_land_A.csv")
df4 = pd.read_csv("F_lvr_land_A.csv")
# %%
df1["地區"]=["Taipei"] * len(df1)
df2["地區"]=["Taichung"] * len(df2)
df3["地區"]=["Kaohsiung"] * len(df3)
df4["地區"]=["New_Taipei"] * len(df4)
# %%
df = pd.concat([df1.drop(0), df2.drop(0), df3.drop(0), df4.drop(0)])
# %%
df.info()
# %%
columns_mapping = {'鄉鎮市區':'towns',
'交易標的':'transaction_sign',
'土地區段位置建物區段門牌':'house_number',
'土地移轉總面積平方公尺':'land_area_square_meter', 
'都市土地使用分區':'use_zoning', 
'非都市土地使用分區':'land_use_district',
'非都市土地使用編定':'land_use',
'交易年月日':'tx_dt', 
 '交易筆棟數':'transaction_pen_number', 
 '移轉層次':'shifting_level', 
 '總樓層數':'total_floor_number', 
 '建物型態':'building_state', 
 '主要用途':'main_use', 
 '主要建材':'main_materials',
 '建築完成年月':'complete_date', 
 '建物移轉總面積平方公尺':'building_area_square_meter', 
 '建物現況格局-房':'room_number', 
 '建物現況格局-廳':'hall_number', 
 '建物現況格局-衛':'health_number', 
'建物現況格局-隔間':'compartmented_number', 
 '有無管理組織':'manages', 
 '總價元':'total_price', 
 '單價元平方公尺':'unit_price', 
 '車位類別':'berth_category', 
 '車位移轉總面積(平方公尺)':'berth_area_square_meter',
'車位總價元':'berth_price', 
 '備註':'note', 
 '編號':'serial_number', 
 '主建物面積':'main_building_area', 
 '附屬建物面積':'auxiliary_building_area', 
 '陽台面積':'balcony_area', 
 '電梯':'elevator',
 '地區':'city'
                  }
analysis_columns = ['city','towns','main_use','use_zoning','total_price','building_area_square_meter',
                                     'main_building_area',
                                     'tx_dt','unit_price','room_number','hall_number','health_number']
columns_type = {'total_price': 'int','unit_price':'float','building_area_square_meter':'float',
                                      'main_building_area': 'float',
                                      'room_number': 'int','hall_number': 'int','health_number': 'int'}
df.rename(columns=columns_mapping, inplace=True)
# %%
## find the house for resident
data = df[(df['use_zoning']=='住') & (df['main_use']=='住家用')]
data = data.loc[:,analysis_columns]
data.info()
data.isna().sum()
# %%
data.dropna()
# %%
data = data.astype(columns_type)
data.info()
# %%
#4. 做資料切片將
#     新增欄位交易年月日(tx_year)，從交易年月日(tx_dt)萃取出年份
#     1.交易年月日(tx_year)，限制在109年
#     2.建物現況格局-房(room_number)，限制在1到5間
#     3.建物現況格局-廳(hall_number)，限制在1到2廳
#     4.最後運用.reset_index()重新定義索引
y = []
for i in range(len(data)):
    y.append(data.iloc[i,data.columns.get_loc('tx_dt')][:3])
data['tx_year'] = y
data['tx_year'] = data['tx_year'].astype(int)
# %%
analysis_data = data[(data['tx_year']==109) & (data['room_number']>0)
        & (data['hall_number']>0)].reset_index()
# %%
# 建立新特徵
# 1. 建物移轉總面積坪(building_area_square_feet) : 建物移轉總面積平方公尺*0.3025
# 2. 主建物面積坪(main_building_area_square_feet) : 主建物面積*0.3025
# 3. 單價元坪(unit_price_square_feet) : 單價元平方公尺/0.3025

analysis_data['building_area_square_feet'] = analysis_data['building_area_square_meter']*0.3025
analysis_data['main_building_area_square_feet'] = analysis_data['main_building_area']*0.3025
analysis_data['unit_price_square_feet'] = analysis_data['unit_price']/0.3025
analysis_data.describe()
# %%
## total_price and main_building_area has 0
analysis_data = analysis_data.loc[(analysis_data.total_price!=0)&(analysis_data.main_building_area!=0)]
analysis_data.describe()
# %%
# 阿宏我是台北人他想找出影響台北市總價、單價元坪的因子
# 1. 資料切片切出city欄位為台北市的資料，並找出時價登入總價(total_price)高度相關的變數
# 建物移轉總面積平方公尺、主建物面積、建物移轉總面積坪、主建物面積坪
# 2. 資料切片切出city欄位為台北市的資料，找出單價元坪(unit_price_square_feet)高度相關的變數
# 單價元平方公尺
analysis_data.loc[analysis_data.city=='Taipei'].corr()[['total_price','unit_price_square_feet']]
# %%
city_data = pd.DataFrame()
city_data["sum"] = analysis_data.groupby("city")["index"].sum()
pd.concat([city_data,pd.DataFrame(analysis_data.groupby("city")["total_price", "unit_price"].mean())],axis=1)
# %%
d = go.Bar(x=city_data.index,y=city_data["sum"])
fig = go.Figure(data=d)
fig.update_layout(title="民國109年四都房屋總成交數")
fig.show()
# %%
analysis_data.boxplot(column=['unit_price_square_feet'],by='city',figsize=(16,6))
# %%
analysis_data.boxplot(column=['total_price'],by='city',figsize=(16,6))
# %%
