import streamlit as st
import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
import math




title_html = """
<div style="background-color: #f63366; padding: 10px; border-radius: 10px;">
    <h1 style="color: white; text-align: center;">Phone Number Location Finder</h1>
</div>
"""

st.markdown(title_html, unsafe_allow_html=True)


# Adding an introduction with Markdown
st.markdown("""
Welcome to the **Phone Number Location Finder**! This tool helps you find the general location of a phone number, including the country and the city or region where the phone number is currentl in use. 

Please enter a phone number including the country code (for example, +1 234 567 8900) in the input field below and see where the number is in use currently. 

### How It Works
1. **Enter Phone Number:** Input the full phone number with the country code in the text box.
2. **View Location:** The app will display the phone number's location based on its prefix.
3. **See on Map:** A map view will show the approximate location for the phone number.

_Note: This tool does not track real-time locations but provides an estimate based on the phone number's prefix._

**Service Provider Info:** The app also attempts to identify the service provider associated with the number.

Ready to get started? Enter a phone number below!
""", unsafe_allow_html=False)


# Function to convert lat/lon to Web Mercator format
def lat_lon_to_web_mercator(lat, lon):
    k = 6378137
    x = lon * (k * math.pi/180.0)
    y = math.log(math.tan((90 + lat) * math.pi/360.0)) * k
    return x, y

# Get phone number from user input
number = st.text_input("Enter phone number (with country code):")
# Optional: Let the user specify a more precise location
user_location = st.text_input("Optionally, enter a more specific location (e.g., city, country):")

if number:
    pepnumber = phonenumbers.parse(number)
    location = geocoder.description_for_number(pepnumber, "en")
    service_pro = phonenumbers.parse(number)
    provider = carrier.name_for_number(service_pro, "en")

    st.write("Phone Number Location:", location)
    st.write("Service Provider:", provider)

    key = '3229ea51ebed4311924d0dc704876aca'  # Use your OpenCage API key
    geocoder = OpenCageGeocode(key)
    
    # Use the user-specified location if provided, otherwise fall back to the phone number's location
    query = f"{user_location}, {location}" if user_location else str(location)
    
    results = geocoder.geocode(query)

    if results:
        lat = results[0]['geometry']['lat']
        lng = results[0]['geometry']['lng']

        st.write("Latitude:", lat)
        st.write("Longitude:", lng)

        # Convert lat/lon to Web Mercator
        wm_x, wm_y = lat_lon_to_web_mercator(lat, lng)

        # Create Bokeh plot
        p = figure(x_range=(wm_x - 5000, wm_x + 5000), y_range=(wm_y - 5000, wm_y + 5000),
                   x_axis_type="mercator", y_axis_type="mercator")
        tile_provider = get_provider(Vendors.CARTODBPOSITRON)
        p.add_tile(tile_provider)

        # Plot marker at the location
        p.circle(x=[wm_x], y=[wm_y], size=10, fill_color="blue", fill_alpha=0.8)

        # Display the plot
        st.bokeh_chart(p, use_container_width=True)
    else:
        st.error("No results found for the location.")