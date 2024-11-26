import pandas as pd
import plotly.express as px

 
data = pd.read_csv('rides_data.csv')

fig = px.density_mapbox(data, lat='destination_lat', lon='destination_lng')

fig.update_layout(mapbox_style="carto-positron")

fig.show()