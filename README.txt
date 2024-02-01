Seagrass mapping script:
Seagrass Mapping is a Python script that generates an interactive Folium map visualizing seagrass data. 
The map includes grid plots with information on seagrass plant counts and categorization based on different methods.

Data:
The data is a text(.txt) file that contains cell, latitude, longitude, number of plants and method.

Where:
cell = the ID of the sampled plots
latitude = the latitude of the center of the sampled plot
longitude = the longitude of the center of the sampled plot
number of plants = the number of plants counted in the plot
method = the method that was used to plant the plants in the plot

The data is structured like this: 

cell	latitude	longitude	n_seagrass_plants	method
1	51.448749	4.202215	18	1
2	51.450274	4.197732	22	1
3	51.449043	4.185043	55	1

Code:
This script maps the number of seagrass plants and their planting method per plot. It can generate
random example data to use the script (structured as mentioned above) if there is no data available. The script first generates plots
based on the coordinates of the measurements provided in the data. It does this by converting the coordinates
to their corresponding UTM coordinates to create the plots and then converts them back to the original coordinates
so they can be used for the map. The script the creates a interactive map of the data. It colors the plots according
to the number of plants present in that plot and colors the border according to the planting method used in that
plot. It then creates the map in html format and opens it in your browser.

The user can set the coordinates for the random data generation, set the grid size (in meters), choose the right UTM according to the sample area 
and set the center coordinates of the map.

Github link:
https://github.com/LarsGehin/assignment_3.git

software:
python 3.12

packages used:
random 
pandas
geopandas
shapely
folium
webbrowser