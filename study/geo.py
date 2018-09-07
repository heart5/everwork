from geopy import GoogleV3 
place="221b Baker Street, London"
location=GoogleV3().geocode(place)
print(place)
print(location.address)
#print(location.location)
