import requests
from PIL import Image
import math
import io
import json5

# Mapbox API credentials
with open('keys.json5') as f:
    keys = json5.load(f)
    access_token = keys['mapbox']['token']
    map_id = keys['mapbox']['style']

image_width = 272 # bricks
image_height = int(272*9/16) # aspect ratio 16:9

corners = {
    "ne" : {
        "lat" : -33.835,
        "lng" : 151.265
    },
    "sw" : {
        "lat" : -33.895,
        "lng" : 151.145
    }
}
# Define the bounding box (ROI) and the desired image size
# Bounding box: (min_lon, min_lat, max_lon, max_lat)
# Calculate the center of the bounding box
center_lng = (corners['ne']['lng'] + corners['sw']['lng']) / 2
center_lat = (corners['ne']['lat'] + corners['sw']['lat']) / 2

# Calculate the zoom level to cover the bounding box
# You might need to adjust this manually based on your needs.
zoom_level = 10

# Construct the API request URL
static_map_url = (
    f"https://api.mapbox.com/styles/v1/{map_id}/static/"
    f"{center_lng},{center_lat},{zoom_level}/"
    f"{image_width}x{image_height}?access_token={access_token}&logo=false&attribution=false"
)

# Fetch the image
response = requests.get(static_map_url)
if response.status_code == 200:
    image = Image.open(io.BytesIO(response.content))
    image.save('roi_image.png')

    upscaled_image = image.resize((3840, 2160), Image.Resampling.NEAREST)
    upscaled_image.save('roi_image_4k.png')

    print("Image saved as 'roi_image.png'.")
else:
    print(f"Failed to fetch image (status code: {response.status_code}).")