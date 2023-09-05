# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
from geopy import GoogleV3 
place="221b Baker Street, London"
location=GoogleV3().geocode(place)
print(place)
print(location.address)
#print(location.location)
