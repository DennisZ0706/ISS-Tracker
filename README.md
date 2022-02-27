# ISS Tracker 

## The App

Application to hunt down the International Space Station. Current location of the Space Station can be found and also wich pilots are currently in the ship. 

It's also possibe to check at which time the ISS will pass your location. So with this app you will never miss the Internation Space Station again!  


## Libraries used

* PyQt5
* folium
* urllib.request
* library 3
* json
* time


## Learned skills

* Basics of Building a GUI with PyQt5
* Basics of classes 
* Working with OpenStreetMap and folium
* Working with JSON and API's
* Working with Mouseposition 
* Get location from coordinates with Nominatim module


## How it works

The current location of the International Space Station can be plotted by clicking on the "PLOT ISS" button. The pilots can be retrieved by clicking on "GET PILOTS"

When you want to know when the International Space Station will pass your location then enter the coordinates of your location in the input fields for longitude and latitude and press "GET TIME". The coordinates of your own location can be found by hoovering the mouse over the map to your location. When you have found your location then the coordinates can be found at the top right of the map. 

By clicking on "CLEAR LOCATION" your location will be cleared from the map and you will be able to fill in a new location.


## Preview

![screenshot_get_pilots](Showcase/screenshot_get_pilots.png?raw=true "Get pilots")

![screenshot_plot_ISS](Showcase/screenshot_plot_ISS.png?raw=true "Plot ISS")

![screenshot_time_location](Showcase/screenshot_time_location.png?raw=true "Get time location")