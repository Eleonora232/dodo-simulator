from geopy.geocoders import Nominatim
import math

class Island:
    def __init__(self, lat, lon, area_km2):
        self.lat = lat
        self.lon = lon
        self.area = area_km2
        
        # 1. Reverse Geocode to find the closest Mainland territory
        geolocator = Nominatim(user_agent="dodo_sim")
        location = geolocator.reverse(f"{lat}, {lon}", language='en')
        
        # We extract the country name to use as our "Mainland"
        self.closest_mainland = location.raw.get('address', {}).get('country', "Mainland Pool")
        self.country_code = location.raw.get('address', {}).get('country_code', "US").upper()
        
        # 2. Distance from "Mainland" 
        # (In a full version, we'd calculate distance to the nearest coast)
        self.distance_km = 500 # Default for now
        
        # 3. Foster's Rule & Productivity
        self.m_opt = 1000 * (self.area ** 0.25)
        self.residents = []
        self.predators_present = False