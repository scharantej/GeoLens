
# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import json
import folium
from geopy.geocoders import Nominatim

# Initialize the Flask application
app = Flask(__name__)

# Default GeoJSON data
default_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]
            },
            "properties": {
                "name": "Golden Gate Bridge",
                "description": "The Golden Gate Bridge is a suspension bridge spanning the Golden Gate strait, the strait between San Francisco Bay and the Pacific Ocean."
            }
        }
    ]
}

# Define the root route
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle GeoJSON data upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded file
    geojson_file = request.files['geojson']

    # Validate the file
    if geojson_file.filename.endswith('.geojson'):
        # Read the file contents
        geojson_data = geojson_file.read().decode('utf-8')

        # Try to parse the GeoJSON data
        try:
            geojson_data = json.loads(geojson_data)
        except json.decoder.JSONDecodeError:
            return "Invalid GeoJSON data.", 400
    else:
        return "Invalid file format.", 400

    # Save the GeoJSON data to a suitable location (e.g., a database)

    # Redirect to the map page
    return redirect(url_for('map'))

# Define the route to render the map
@app.route('/map')
def map():
    # Get the GeoJSON data (from the database or the default data)
    geojson_data = default_geojson

    # Create a Leaflet map object
    map = folium.Map(location=[37.7749, -122.4194], zoom_start=12)

    # Add the GeoJSON data to the map
    folium.GeoJson(geojson_data).add_to(map)

    # Add a sidebar to display point information
    sidebar = folium.Html(
        """
        <div id="sidebar">
            <h3 id="point-name"></h3>
            <p id="point-description"></p>
        </div>
        """, script=True)
    map.add_child(sidebar)

    # Add a marker popup to display point information
    for feature in geojson_data['features']:
        folium.Marker(
            location=feature['geometry']['coordinates'],
            popup=feature['properties']['name'],
        ).add_to(map)

    # Add a click event handler to the map
    def on_click(feature, layer):
        sidebar.children[1].children[0].innerHTML = feature['properties']['name']
        sidebar.children[1].children[1].innerHTML = feature['properties']['description']

    map.add_event_handler('click', on_click)

    # Get the HTML representation of the map
    map_html = map._repr_html_()

    # Render the map page
    return render_template('map.html', map_html=map_html)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
