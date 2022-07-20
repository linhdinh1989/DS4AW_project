## for data
import numpy as np
import pandas as pd
## for plotting
import matplotlib.pyplot as plt
import seaborn as sns
## for geospatial
import folium
import geopy
## for machine learning
from sklearn import preprocessing, cluster
import scipy

state_geo = "us-states.json"
state_mobility = "Sub_Region_Mobility_Report.csv"
state_data = pd.read_csv(state_mobility)

map_ = folium.Map(location=[48, -102], zoom_start=4)

folium.Choropleth(
    geo_data=state_geo,
    name="choropleth",
    data=state_data,
    columns=["sub_region_1", "workplaces_percent_change_from_baseline"],
    key_on="feature.properties.name",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Workplaces percent change from baseline (%)"
).add_to(map_)
folium.LayerControl().add_to(map_)

coordinates = [(32.900908, -97.040335), (40.768571, -73.861603)]
aline = folium.PolyLine(locations=coordinates, weight=1.5, color='green')
# folium.RegularPolygonMarker(location=(40.768571, -73.861603), fill_color='green', number_of_sides=3, radius=10,
# rotation=0.7).add_to(map_)
map_.add_child(aline)
folium.Marker(location=(40.768571, -73.861603), popup='net flow').add_to(map_)

coordinates = [(32.900908, -97.040335), (36.768571, -120.861603)]
aline = folium.PolyLine(locations=coordinates, weight=1.5, color='green')
map_.add_child(aline)
folium.Marker(location=(36.768571, -120.861603), popup='net flow').add_to(map_)

# I use other data sources to work on the bubble map
# feel free to change the data source and present the property we want, like netflow, income level
dtf = pd.read_csv('data_stores.csv')
filter = "Atlanta"
dtf = dtf[dtf["City"] == filter][["City", "Street Address", "Longitude", "Latitude"]].reset_index(drop=True)
dtf = dtf.reset_index().rename(columns={"index": "id"})

dtf["Potential"] = np.random.randint(low=3, high=10 + 1, size=len(dtf))
dtf["Staff"] = dtf["Potential"].apply(lambda x: int(np.random.rand() * x) + 1)
dtf["Capacity"] = dtf["Potential"] - dtf["Staff"]
dtf["Cost"] = np.random.choice(["high", "medium", "low"], size=len(dtf), p=[0.4, 0.5, 0.1])

x = "Cost"
ax = dtf[x].value_counts().sort_values().plot(kind="barh")
totals = []
for i in ax.patches:
    totals.append(i.get_width())
total = sum(totals)
for i in ax.patches:
    ax.text(i.get_width() + .3, i.get_y() + .20,
            str(round((i.get_width() / total) * 100, 2)) + '%',
            fontsize=10, color='black')
ax.grid(axis="x")
plt.suptitle(x, fontsize=20)
# plt.show()

city = "Atlanta"
## get location
locator = geopy.geocoders.Nominatim(user_agent="MyCoder")
location = locator.geocode(city)
print(location)
## keep latitude and longitude only
location = [location.latitude, location.longitude]
print("[lat, long]:", location)

x, y = "Latitude", "Longitude"
color = "Cost"
size = "Staff"
popup = "Street Address"
data = dtf.copy()

## create color column
lst_colors = ["red", "green", "orange"]
lst_elements = sorted(list(dtf[color].unique()))
data["color"] = data[color].apply(lambda x:
                                  lst_colors[lst_elements.index(x)])
## create size column (scaled)
scaler = preprocessing.MinMaxScaler(feature_range=(3, 15))
data["size"] = scaler.fit_transform(
    data[size].values.reshape(-1, 1)).reshape(-1)

## add points
data.apply(lambda row: folium.CircleMarker(
    location=[row[x], row[y]], popup=row[popup],
    color=row["color"], fill=True,
    radius=row["size"]).add_to(map_), axis=1)
## add html legend
legend_html = """<div style="position:fixed; bottom:10px; left:10px; border:2px solid black; z-index:9999; font-size:14px;">&nbsp;<b>""" + color + """:</b><br>"""
for i in lst_elements:
    legend_html = legend_html + """&nbsp;<i class="fa fa-circle 
     fa-1x" style="color:""" + lst_colors[lst_elements.index(i)] + """">
     </i>&nbsp;""" + str(i) + """<br>"""
legend_html = legend_html + """</div>"""
map_.get_root().html.add_child(folium.Element(legend_html))

map_.save('map.html')
