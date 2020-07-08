# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import folium
import pandas as pd

# %%
# define the world map
world_map = folium.Map()

# display world map
world_map

# %%
# San Francisco latitude and longitude values
latitude = 37.77
longitude = -122.42

# Create map and display it
san_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# Display the map of San Francisco
san_map

# %%
# San Francisco latitude and longitude values
latitude = 30.583877
longitude = 114.36599

# Create map and display it
san_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# Display the map of San Francisco
san_map

# %%
