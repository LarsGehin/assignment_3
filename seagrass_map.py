"""
Created on Tuesday 30-01-2024
@author: Lars Gehin, S4082338
@email: l.m.gehin@student.rug.nl

This script generates a visual representation of seagrass mapping using Folium and GeoPandas.
The process involves generating random coordinate data within a specified geographical area,
creating GeoDataFrames, and mapping seagrass data onto a grid. The resulting map includes
layers for seagrass quantity, method categorization, hover data, and a legend.

This script maps the number of seagrass plants and their planting method per plot. It can generate
random example data to use the script if there is no data available. The script first generates a plots
based on the coordinates of the measurements provided in the data. It does this by converting the coordinates
to their corresponding UTM coordinates to create the plots and then converts them back to the original coordinates
so they can be used for the map. The script the creates a interactive map of the data. It colors the plots according
to the number of plants present in that plot and colors the border according to the planting method used in that
plot. It then creates the map in html format and opens it in your browser.

Functions:
- generate_random_data: Generates random coordinate data with associated seagrass quantity and method categorization.
- style_function: Defines a style function for GeoJSON features based on the 'method' property.
- create_grid_df: Reads coordinate data, converts it into GeoDataFrame, and creates a grid around the points.
- create_empty_map: Creates an empty Folium map centered at a specified latitude and longitude.
- create_seagrass_map: Adds the number of seagrass plants to the grid plots and colors them accordingly.
- create_methods_map: Adds a colored border to the grid plots according to the method used in that plot.
- create_hover_data: Adds hover data to the existing Folium map, showing plot number, method, and number of plants.
- create_legend: Adds a legend to an existing Folium map.

"""
import random
import pandas as pd
import geopandas as gpd
from shapely.geometry import box, Point
import folium
import webbrowser

def generate_random_data(min_lat, max_lat, min_lon, max_lon, num_rows, file_name, seed=None):
    """
    Generates a text file containing random coordinate data within a specified geographical area.
    The area is defined by the minimum and maximum latitudes and longitudes.

    min_lat: The minimum latitude of the geographical area
    max_lat: The maximum latitude of the geographical area
    min_lon: The minimum longitude of the geographical area
    max_lon: The maximum longitude of the geographical area
    num_rows: The number of data points to generate
    file_name: The name of the file to write the generated data to

    The generated file contains columns: cell, latitude, longitude, n_seagrass_plants, method
    - cell: Unique identifier for each data point
    - latitude: Randomly generated latitude within the specified geographical area
    - longitude: Randomly generated longitude within the specified geographical area
    - n_seagrass_plants: Randomly generated number of seagrass plants (0 to 100)
    - method: Categorization of data points into four methods based on their order (1 to 4)
    """
    random.seed(seed)

    with open(file_name, 'w') as output:
        output.write(f"cell\tlatitude\tlongitude\tn_seagrass_plants\tmethod\n")
        for i in range(num_rows):
            cell = (i + 1)
            n_plants = random.randint(0, 100)
            lat = min_lat + random.random() * (max_lat - min_lat)
            lon = min_lon + random.random() * (max_lon - min_lon)

            if i < 25:
                method = str('1')
            elif i < 50:
                method = str('2')
            elif i < 75:
                method = str('3')
            else:
                method = str('4')

            output.write('%d\t%.6f\t%.6f\t%d\t%s\n' % (cell, lat, lon, n_plants, method))


def style_function(feature):
    """
        Defines a style function for GeoJSON features based on the 'method' property.
        Assigns colors and line weights to GeoJSON features depending on their 'method' values.
        This can then be used to plot these colors on the map.

        Parameters:
        feature: A GeoJSON feature with properties, including 'method'

        Method-color mappings:
        - Method 1: Orange with a line weight of 4
        - Method 2: Red with a line weight of 4
        - Method 3: Blue with a line weight of 4
        - Method 4: Yellow with a line weight of 4

        """
    if feature['properties']['method'] == 1:
        return {'color': 'orange', 'weight': 4}

    elif feature['properties']['method'] == 2:
        return {'color': 'red', 'weight': 4}

    elif feature['properties']['method'] == 3:
        return {'color': 'blue', 'weight': 4}

    elif feature['properties']['method'] == 4:  # Add styles for other treatments or default case
        return {'color': 'Yellow', 'weight': 4}


def create_grid_df(file_name, utm, grid_size):
    """
        Reads coordinate data from a file, converts it into GeoDataFrame, and creates a grid around the points
    	with the points as center of the grid. The gridsize is in meters. The grid size is the total width/height of the plot.

        Parameters:
        - file_name: Name of the file containing the coordinate data
        - utm: UTM zone for coordinate conversion (enter appropriate UTM for your coordinates)
        - grid_size: Size of the grid in meters around the center points

        """
    df = pd.read_csv(file_name, sep='\t', header=0)

    # Convert DataFrame to GeoDataFrame
    points = df.apply(lambda row: Point(row.longitude, row.latitude), axis=1)
    seagrass = gpd.GeoDataFrame(df, geometry=points)
    seagrass.crs = {'init': 'epsg:4326'}

    # Convert GeoDataFrame to UTM coordinates
    gdf = seagrass.to_crs(epsg=utm)  # Replace 32633 with the appropriate UTM zone for your location

    # Create a grid with the specified size around the center points
    grid_geometries = [box(point.x - grid_size / 2, point.y - grid_size / 2,
                           point.x + grid_size / 2, point.y + grid_size / 2)
                       for point in gdf['geometry']]

    grid_df = gpd.GeoDataFrame(geometry=grid_geometries, crs=gdf.crs)

    # Convert grid GeoDataFrame back to WGS84
    grid_df = grid_df.to_crs(epsg=4326)

    # Add columns from the original DataFrame
    grid_df['n_plants'] = seagrass['n_seagrass_plants']
    grid_df['cell'] = seagrass['cell']
    grid_df['method'] = seagrass['method']

    return gdf, grid_df


def create_empty_map(lat, lon):
    """
        Creates an empty Folium map centered at a specified latitude and longitude.

        Parameters:
        - lat: Latitude for the center of the map
        - lon: Longitude for the center of the map

        """
    m = folium.Map([lat, lon], zoom_start=15)

    return m


def create_seagrass_map(grid_df, gdf, m):
    """
        Adds the number of plants to the grid plots and colors them accordingly.
    	This layer is then added to the previously created map.

        Parameters:
        - grid_df: GeoDataFrame representing the grid
        - gdf: GeoDataFrame with original coordinate data
        - m: Folium map object

        """

    folium.Choropleth(
        geo_data=grid_df.to_json(),
        name="choropleth",
        data=gdf,
        key_on="feature.properties.cell",
        columns=["cell", "n_seagrass_plants"],
        fill_color="YlGn",
        fill_opacity=1,
        legend_name="Number of plants in plot",
    ).add_to(m)

    return m


def create_methods_map(grid_df, m):
    """
        Adds a colored border to the grid plots according to the method used in that plot.
        This layer is then added to the previously created map.

        Parameters:
        - grid_df: GeoDataFrame representing the grid
        - m: Folium map object

        """
    folium.GeoJson(
        grid_df,
        name='Methods',
        style_function=style_function
    ).add_to(m)


def create_hover_data(grid_df, style_f, highlight_f, m):
    """
      Adds hover data to the existing Folium map. When you hover over the plots with your cursor
      you can see the data of the plot: the plot number, the method and the number of plants in that plot.

      Parameters:
      - grid_df: GeoDataFrame representing the grid
      - style_f: Style function for GeoJSON features
      - highlight_f: Highlight function for GeoJSON features
      - m: Folium map object

      """

    hd = folium.features.GeoJson(
        grid_df,
        style_function=style_f,
        control=False,
        highlight_function=highlight_f,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['cell', 'method', 'n_plants'],  # use fields from the json file
            aliases=['Plot number: ', 'Method: ', 'Number of plants: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    m.add_child(hd)
    m.keep_in_front(hd)


def create_legend(m):
    """
        Adds a legend to an existing Folium map.

        Parameters:
        - m: Folium map object

        """
    legend_html = '''
         <div style="position: fixed; 
                     bottom: 50px; right: 50px; width: 120px; height: 130px; 
                     border:2px solid grey; z-index:9999; font-size:14px;
                     background-color:rgba(255, 255, 255, 0.8);
                     border-radius: 8px;
                     ">
         &nbsp; <strong>Legend</strong> <br>
         &nbsp; Method 1 &nbsp; <i style="background:orange; width:20px; height:10px; display:inline-block; border:1px solid black; border-radius: 4px;"></i><br>
         &nbsp; Method 2 &nbsp; <i style="background:red; width:20px; height:10px; display:inline-block; border:1px solid black; border-radius: 4px;"></i><br>
         &nbsp; Method 3 &nbsp; <i style="background:blue; width:20px; height:10px; display:inline-block; border:1px solid black; border-radius: 4px;"></i><br>
         &nbsp; Method 4 &nbsp; <i style="background:yellow; width:20px; height:10px; display:inline-block; border:1px solid black; border-radius: 4px;"></i><br>
         </div>
         '''
    m.get_root().html.add_child(folium.Element(legend_html))
    # Add layer control
    folium.LayerControl().add_to(m)


if __name__ == '__main__':
    # variable needed in the functions
    min_lat, max_lat, min_lon, max_lon = 51.4459, 51.4521, 4.1828, 4.2032
    num_rows = 100
    file_name = 'random_lat_lon.txt'
    utm = 32631
    grid_size = 20
    lat = 51.4501
    lon = 4.1901

    # Generate random data

    #print(f"Generating random latitude, longitude, plant count and method data")
    #Setting a seed to keep the data reproducible
    #generate_random_data(min_lat, max_lat, min_lon, max_lon, num_rows, file_name, seed=100)

    # Create GeoDataFrames and location grid dataframe
    print(f"Creating GeoDataFrame and grid data frame from {file_name}")
    gdf, grid_df = create_grid_df(file_name, utm, grid_size)

    # Create an empty folium map
    print(f"Generating an empty folium map")
    m = create_empty_map(lat, lon)

    # Add a location grid with corresponding method colors to the map
    print(f"Adding methods to the folium map")
    create_methods_map(grid_df, m)

    # Add a location grid with corresponding plant counts to the map
    print(f"Adding plant counts to the map")
    create_seagrass_map(grid_df, gdf, m)

    # Styling for the hover data
    style_f = lambda x: {'fillColor': '#ffffff',
                         'color': '#000000',
                         'fillOpacity': 0.1,
                         'weight': 0.1}
    highlight_f = lambda x: {'fillColor': '#000000',
                             'color': '#000000',
                             'fillOpacity': 0.50,
                             'weight': 0.1}

    print(f"Adding hover marks to the map")
    create_hover_data(grid_df, style_f, highlight_f, m)

    # Add legend to the map
    print(f"Adding a legend to the map")
    create_legend(m)

    # Save or display the map
    print(f"Saving the map as seagrass_map.html and opening the map in your browser")
    m.save("seagrass_map.html")
    webbrowser.open("seagrass_map.html")

    print(f"Script complete!")
    print(f"ALL DONE!")
