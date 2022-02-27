import io
import sys
import folium
from folium.plugins import MousePosition, Draw
import urllib.request
import json
import time

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QListWidget, QVBoxLayout, QListWidgetItem
from PyQt5.QtGui import QCursor, QIcon, QPixmap

from geopy.geocoders import Nominatim

# Define user_agent to legally use geolocater

geolocator = Nominatim(user_agent="ISS_app", timeout=1)


# GUI 

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.map()
        self.information_panel()
        self.buttons_ISS()
        self.location()
        self.buttons_location()

    # Build main window

    def initWindow(self):
        
        self.setWindowTitle(self.tr("ISS TRACKER"))
        self.setFixedSize(1440, 900)
        self.setWindowIcon(QIcon('Icon_ISS.png'))
        self.setStyleSheet('background-color: #85C285;')
        

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.lay_central_widget = QtWidgets.QHBoxLayout(central_widget)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(20, 50, 20, 50)

        self.navigation_container = QtWidgets.QWidget() 
        self.navigation_container.setMaximumHeight(770)
        self.navigation_container.setMaximumWidth(330)
        self.navigation_container.setStyleSheet(
            'background-color: #E8E8E8;' +
            'border: 2px solid #D0D0D0;' 
        )
        self.vlay_navigation = QtWidgets.QVBoxLayout(self.navigation_container)

        self.lay_central_widget.addWidget(self.navigation_container)
        self.lay_central_widget.addWidget(self.view, stretch=1)
        
    # Build and show map

    def map(self):     

        self.m = folium.Map(
            location=[43.507351, 5.127758], 
            tiles="Stamen Toner", 
            zoom_start=2,
            zoom_control=False,
            scrollWheelZoom=False,
            dragging=False
        )

        formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

        MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=False,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
        ).add_to(self.m)

        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
    
    # Build and show information panel

    def information_panel(self):

        self.infopanel_container = QtWidgets.QWidget()
        self.vlay_infopanel = QtWidgets.QVBoxLayout(self.infopanel_container)

        self.vlay_navigation.addStretch()
        self.vlay_navigation.addWidget(self.infopanel_container)
        self.vlay_navigation.addStretch()

        title_infopanel = QtWidgets.QLabel("DATA PANEL")
        title_infopanel.setFont(QtGui.QFont('Lucida Console', 28))
        title_infopanel.setAlignment(QtCore.Qt.AlignCenter)
        title_infopanel.setStyleSheet(
            'background-color: #D0D0D0;' +
            'color: slategrey;'
        )

        self.entry_infopanel = QtWidgets.QListWidget(self)
        self.entry_infopanel.setFont(QtGui.QFont('Courier', 8))
        self.entry_infopanel.setStyleSheet(
            'background-color: black;' + 
            'color: lightgreen;' +
            'border: 5px solid 	#202020;' +
            'border-radius: 10px;'
        )

        self.vlay_infopanel.addStretch()
        self.vlay_infopanel.addWidget(title_infopanel)
        self.vlay_infopanel.addWidget(self.entry_infopanel)
        self.vlay_infopanel.addStretch()

    # Build and show buttons to display pilots and plot location ISS

    def buttons_ISS(self):

        self.buttons_ISS_container = QtWidgets.QWidget()
        self.hlay_buttons_ISS = QtWidgets.QHBoxLayout(self.buttons_ISS_container)

        self.vlay_navigation.addStretch()
        self.vlay_navigation.addWidget(self.buttons_ISS_container)
        self.vlay_navigation.addStretch()

        button1 = QtWidgets.QPushButton("GET PILOTS")
        button1.setFont(QtGui.QFont('Courier', 8))
        button1.setFixedSize(120, 50)
        button1.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        button1.clicked.connect(self.get_pilots)
        button1.setStyleSheet(
            '*{background-color: green;' +
            'border: 2px solid black;' +
            'font-weight: bold;}' +

            '*:hover{background: "lightgreen";}' + 

            '*:pressed{background: "green"; border: 2px solid green;}' 
        )

        button2 = QtWidgets.QPushButton("PLOT ISS")
        button2.setFont(QtGui.QFont('Courier', 8))
        button2.setFixedSize(120, 50)
        button2.clicked.connect(self.location_ISS)
        button2.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        button2.setStyleSheet(
            '*{background-color: blue;' +
            'border: 2px solid black;' +
            'font-weight: bold;}' +

            '*:hover{background: "lightskyblue";}' + 

            '*:pressed{background: "blue"; border: 2px solid blue;}' 
        )

        self.hlay_buttons_ISS.addStretch()
        self.hlay_buttons_ISS.addWidget(button1)
        self.hlay_buttons_ISS.addWidget(button2)
        self.hlay_buttons_ISS.addStretch()

    # Build and show location panel to put in coordinates to find time ISS will pass certain location

    def location(self):

        self.location_container = QtWidgets.QWidget()
        self.location_container.setMaximumHeight(400)
        self.vlay_location = QtWidgets.QVBoxLayout(self.location_container)
        self.vlay_location.setSpacing(0)

        self.vlay_navigation.addStretch()
        self.vlay_navigation.addWidget(self.location_container)
        self.vlay_navigation.addStretch()

        title_location = QtWidgets.QLabel("TIME LOCATION")
        title_location.setFont(QtGui.QFont('Lucida Console', 18))
        title_location.setAlignment(QtCore.Qt.AlignCenter)
        title_location.setStyleSheet(
            'background-color: #D0D0D0;' +
            'color: slategrey;'
        )

        self.vlay_location.addStretch()
        self.vlay_location.addWidget(title_location)
        self.vlay_location.addStretch()

        self.latlon_container = QtWidgets.QWidget()
        self.latlon_container.setStyleSheet(
            'border: none'
        )
        self.hlay_latlon = QtWidgets.QHBoxLayout(self.latlon_container)

        self.vlay_location.addStretch()
        self.vlay_location.addWidget(self.latlon_container)
        self.vlay_location.addStretch()

        self.latitude_container = QtWidgets.QWidget()
        self.latitude_container.setStyleSheet(
            'border: 1px solid #D0D0D0;'
        )
        self.vlay_latitude = QtWidgets.QVBoxLayout(self.latitude_container)

        self.hlay_latlon.addStretch()
        self.hlay_latlon.addWidget(self.latitude_container)
        self.hlay_latlon.addStretch()

        text_latitude = QtWidgets.QLabel("Latitude")
        text_latitude.setFont(QtGui.QFont('Courier', 10))
        text_latitude.setStyleSheet(
            'border: none;'
        )
    
        self.entry_latitude = QtWidgets.QLineEdit()
        self.entry_latitude.setReadOnly(True)
        self.entry_latitude.setFont(QtGui.QFont('Courier', 8))
        self.entry_latitude.setStyleSheet(
            'background-color: black;' + 
            'color: lightgreen;' + 
            'border: none;'
        )

        self.numlatitude_container = QtWidgets.QFrame()
        self.numlatitude_container.setStyleSheet(
            'border: none;'
        )

        self.lay_numlatitude = QtWidgets.QGridLayout(self.numlatitude_container)
        self.lay_numlatitude.setSpacing(0)
        self.lay_numlatitude.setContentsMargins(0,0,0,0)

        # Stylesheet for buttons numpads latitude and longitude

        numpad_button = (
            '*{background-color: lightgrey;' +
            'border: 0.5px solid black;' + 
            'margin: 1px;}' +

            '*:hover{color: "lightgreen";}' + 

            '*:pressed{background: "lightgreen"; color: "black";}'
        )

        # Numpad latitude

        num1 = QtWidgets.QPushButton("1", clicked = lambda: self.input_lat("1"))
        num1.setFont(QtGui.QFont('Courier', 8))
        num1.setFixedSize(35, 40)
        num1.setStyleSheet(numpad_button)
        num1.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num2 = QtWidgets.QPushButton("2" , clicked = lambda: self.input_lat("2"))
        num2.setFont(QtGui.QFont('Courier', 8))
        num2.setFixedSize(35, 40)
        num2.setStyleSheet(numpad_button)
        num2.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num3 = QtWidgets.QPushButton("3" , clicked = lambda: self.input_lat("3"))
        num3.setFont(QtGui.QFont('Courier', 8))
        num3.setFixedSize(35, 40)
        num3.setStyleSheet(numpad_button)
        num3.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num4 = QtWidgets.QPushButton("4" , clicked = lambda: self.input_lat("4"))
        num4.setFont(QtGui.QFont('Courier', 8))
        num4.setFixedSize(35, 40)
        num4.setStyleSheet(numpad_button)
        num4.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num5 = QtWidgets.QPushButton("5" , clicked = lambda: self.input_lat("5"))
        num5.setFont(QtGui.QFont('Courier', 8))
        num5.setFixedSize(35, 40)
        num5.setStyleSheet(numpad_button)
        num5.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num6 = QtWidgets.QPushButton("6" , clicked = lambda: self.input_lat("6"))
        num6.setFont(QtGui.QFont('Courier', 8))
        num6.setFixedSize(35, 40)
        num6.setStyleSheet(numpad_button)
        num6.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num7 = QtWidgets.QPushButton("7" , clicked = lambda: self.input_lat("7"))
        num7.setFont(QtGui.QFont('Courier', 8))
        num7.setFixedSize(35, 40)
        num7.setStyleSheet(numpad_button)
        num7.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num8 = QtWidgets.QPushButton("8" , clicked = lambda: self.input_lat("8"))
        num8.setFont(QtGui.QFont('Courier', 8))
        num8.setFixedSize(35, 40)
        num8.setStyleSheet(numpad_button)
        num8.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num9 = QtWidgets.QPushButton("9" , clicked = lambda: self.input_lat("9"))
        num9.setFont(QtGui.QFont('Courier', 8))
        num9.setFixedSize(35, 40)
        num9.setStyleSheet(numpad_button)
        num9.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num0 = QtWidgets.QPushButton("0" , clicked = lambda: self.input_lat("0"))
        num0.setFont(QtGui.QFont('Courier', 8))
        num0.setFixedSize(35, 40)
        num0.setStyleSheet(numpad_button)
        num0.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_min = QtWidgets.QPushButton("-" , clicked = lambda: self.input_lat("-"))
        num_min.setFont(QtGui.QFont('Courier', 8))
        num_min.setFixedSize(18, 40)
        num_min.setStyleSheet(numpad_button)
        num_min.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_dot = QtWidgets.QPushButton("." , clicked = lambda: self.input_lat("."))
        num_dot.setFont(QtGui.QFont('Courier', 8))
        num_dot.setFixedSize(17, 40)
        num_dot.setStyleSheet(numpad_button)
        num_dot.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_reset = QtWidgets.QPushButton("C" , clicked = lambda: self.input_lat("C"))
        num_reset.setFont(QtGui.QFont('Courier', 8))
        num_reset.setFixedSize(35, 40)
        num_reset.setStyleSheet(numpad_button)
        num_reset.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
       
        self.lay_numlatitude.addWidget(num1, 0,0,1,2)
        self.lay_numlatitude.addWidget(num2, 0,2)
        self.lay_numlatitude.addWidget(num3, 0,3)
        self.lay_numlatitude.addWidget(num4, 1,0,1,2)
        self.lay_numlatitude.addWidget(num5, 1,2)
        self.lay_numlatitude.addWidget(num6, 1,3)
        self.lay_numlatitude.addWidget(num7, 2,0,1,2)
        self.lay_numlatitude.addWidget(num8, 2,2)
        self.lay_numlatitude.addWidget(num9, 2,3)
        self.lay_numlatitude.addWidget(num_min, 3,0)
        self.lay_numlatitude.addWidget(num_dot, 3,1)
        self.lay_numlatitude.addWidget(num0, 3,2)
        self.lay_numlatitude.addWidget(num_reset, 3,3)

        self.vlay_latitude.addStretch()
        self.vlay_latitude.addWidget(text_latitude)
        self.vlay_latitude.addWidget(self.entry_latitude)
        self.vlay_latitude.addWidget(self.numlatitude_container)
        self.vlay_latitude.addStretch()

        self.longitude_container = QtWidgets.QWidget()
        self.longitude_container.setStyleSheet(
            'border: 1px solid #D0D0D0;'
        )

        self.vlay_longitude = QtWidgets.QVBoxLayout(self.longitude_container)

        self.hlay_latlon.addStretch()
        self.hlay_latlon.addWidget(self.longitude_container)
        self.hlay_latlon.addStretch()

        text_longitude = QtWidgets.QLabel("Longitude")
        text_longitude.setFont(QtGui.QFont('Courier', 10))
        text_longitude.setStyleSheet(
            'border: none;'
        )
   
        self.entry_longitude = QtWidgets.QLineEdit()
        self.entry_longitude.setFont(QtGui.QFont('Courier', 8))
        self.entry_longitude.setReadOnly(True)
        self.entry_longitude.setStyleSheet(
            'background-color: black;' + 
            'color: lightgreen;' +
            'border: none;'
        ) 

        self.numlongitude_container = QtWidgets.QFrame()
        self.numlongitude_container.setStyleSheet(
            'border: none;'
        )

        self.lay_numlongitude = QtWidgets.QGridLayout(self.numlongitude_container)
        self.lay_numlongitude.setSpacing(0)
        self.lay_numlongitude.setContentsMargins(0,0,0,0)

        # Numpad longitude

        num_1 = QtWidgets.QPushButton("1", clicked = lambda: self.input_lon("1"))
        num_1.setFont(QtGui.QFont('Courier', 8))
        num_1.setFixedSize(35, 40)
        num_1.setStyleSheet(numpad_button)
        num_1.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_2 = QtWidgets.QPushButton("2", clicked = lambda: self.input_lon("2"))
        num_2.setFont(QtGui.QFont('Courier', 8))
        num_2.setFixedSize(35, 40)
        num_2.setStyleSheet(numpad_button)
        num_2.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_3 = QtWidgets.QPushButton("3", clicked = lambda: self.input_lon("3"))
        num_3.setFont(QtGui.QFont('Courier', 8))
        num_3.setFixedSize(35, 40)
        num_3.setStyleSheet(numpad_button)
        num_3.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_4 = QtWidgets.QPushButton("4", clicked = lambda: self.input_lon("4"))
        num_4.setFont(QtGui.QFont('Courier', 8))
        num_4.setFixedSize(35, 40)
        num_4.setStyleSheet(numpad_button)
        num_4.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_5 = QtWidgets.QPushButton("5", clicked = lambda: self.input_lon("5"))
        num_5.setFont(QtGui.QFont('Courier', 8))
        num_5.setFixedSize(35, 40)
        num_5.setStyleSheet(numpad_button)
        num_5.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_6 = QtWidgets.QPushButton("6", clicked = lambda: self.input_lon("6"))
        num_6.setFont(QtGui.QFont('Courier', 8))
        num_6.setFixedSize(35, 40)
        num_6.setStyleSheet(numpad_button)
        num_6.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_7 = QtWidgets.QPushButton("7", clicked = lambda: self.input_lon("7"))
        num_7.setFont(QtGui.QFont('Courier', 8))
        num_7.setFixedSize(35, 40)
        num_7.setStyleSheet(numpad_button)
        num_7.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_8 = QtWidgets.QPushButton("8", clicked = lambda: self.input_lon("8"))
        num_8.setFont(QtGui.QFont('Courier', 8))
        num_8.setFixedSize(35, 40)
        num_8.setStyleSheet(numpad_button)
        num_8.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_9 = QtWidgets.QPushButton("9", clicked = lambda: self.input_lon("9"))
        num_9.setFont(QtGui.QFont('Courier', 8))
        num_9.setFixedSize(35, 40)
        num_9.setStyleSheet(numpad_button)
        num_9.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num_0 = QtWidgets.QPushButton("0", clicked = lambda: self.input_lon("0"))
        num_0.setFont(QtGui.QFont('Courier', 8))
        num_0.setFixedSize(35, 40)
        num_0.setStyleSheet(numpad_button)
        num_0.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num__min = QtWidgets.QPushButton("-", clicked = lambda: self.input_lon("-"))
        num__min.setFont(QtGui.QFont('Courier', 8))
        num__min.setFixedSize(18, 40)
        num__min.setStyleSheet(numpad_button)
        num__min.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num__dot = QtWidgets.QPushButton(".", clicked = lambda: self.input_lon("."))
        num__dot.setFont(QtGui.QFont('Courier', 8))
        num__dot.setFixedSize(17, 40)
        num__dot.setStyleSheet(numpad_button)
        num__dot.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        num__reset = QtWidgets.QPushButton("C", clicked = lambda: self.input_lon("C"))
        num__reset.setFont(QtGui.QFont('Courier', 8))
        num__reset.setFixedSize(35, 40)
        num__reset.setStyleSheet(numpad_button)
        num__reset.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
       
        self.lay_numlongitude.addWidget(num_1, 0,0,1,2)
        self.lay_numlongitude.addWidget(num_2, 0,2)
        self.lay_numlongitude.addWidget(num_3, 0,3)
        self.lay_numlongitude.addWidget(num_4, 1,0,1,2)
        self.lay_numlongitude.addWidget(num_5, 1,2)
        self.lay_numlongitude.addWidget(num_6, 1,3)
        self.lay_numlongitude.addWidget(num_7, 2,0,1,2)
        self.lay_numlongitude.addWidget(num_8, 2,2)
        self.lay_numlongitude.addWidget(num_9, 2,3)
        self.lay_numlongitude.addWidget(num__min, 3,0)
        self.lay_numlongitude.addWidget(num__dot, 3,1)
        self.lay_numlongitude.addWidget(num_0, 3,2)
        self.lay_numlongitude.addWidget(num__reset, 3,3)

        self.vlay_longitude.addStretch()
        self.vlay_longitude.addWidget(text_longitude)
        self.vlay_longitude.addWidget(self.entry_longitude)
        self.vlay_longitude.addWidget(self.numlongitude_container)
        self.vlay_longitude.addStretch()

    # Build and show buttons for getting the time of a location and clear a location

    def buttons_location(self):

        self.buttons_loc_container = QtWidgets.QWidget()
        self.buttons_loc_container.setStyleSheet(
            'border: 1px solid #D0D0D0;'
        )
    
        self.hlay_button_loc = QtWidgets.QHBoxLayout(self.buttons_loc_container)

        self.vlay_location.addStretch()
        self.vlay_location.addWidget(self.buttons_loc_container)
        self.vlay_location.addStretch()

        button3 = QtWidgets.QPushButton("GET TIME")
        button3.setFont(QtGui.QFont('Courier', 8))
        button3.setFixedSize(120, 50)
        button3.clicked.connect(self.get_time_location)
        button3.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        button3.setStyleSheet(
            '*{background-color: green;' +
            'border: 2px solid black;' +
            'font-weight: bold;}' +

            '*:hover{background: "lightgreen";}' + 

            '*:pressed{background: "green"; border: 2px solid green;}' 
        )

        button4 = QtWidgets.QPushButton("CLEAR LOCATION")
        button4.setFont(QtGui.QFont('Courier', 8))
        button4.setFixedSize(120, 50)
        button4.clicked.connect(self.clear_location)
        button4.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        button4.setStyleSheet(
            '*{background-color: darkred;' +
            'border: 2px solid black;' +
            'font-weight: bold;}' +

            '*:hover{background: "salmon";}' + 

            '*:pressed{background: "darkred"; border: 2px solid darkred;}' 
        )

        self.hlay_button_loc.addStretch()
        self.hlay_button_loc.addWidget(button3)
        self.hlay_button_loc.addWidget(button4)
        self.hlay_button_loc.addStretch()
    
    # Function to get pilots by API

    def get_pilots(self):

        # get pilots in space
        url_pilots = 'http://api.open-notify.org/astros.json'
        response = urllib.request.urlopen(url_pilots)

        result_pilots = json.loads(response.read())

        # get pilots in ISS
        people = result_pilots['people']

        people_ISS = [i for i in people if (i['craft'] == "ISS")]

        people_ISS2 = []

        for p in people_ISS:
            people_ISS2.append(p['name'])

        self.entry_infopanel.clear()

        QListWidgetItem("Pilots in ISS", self.entry_infopanel)
        QListWidgetItem("", self.entry_infopanel)

        for name in people_ISS2:
            QListWidgetItem(name, self.entry_infopanel)                                     

    # Function to get location ISS by API

    def location_ISS(self):

        if self.entry_latitude.text() == '' and self.entry_longitude.text() == '':

            #get location ISS

            url_location = 'http://api.open-notify.org/iss-now.json'

            response = urllib.request.urlopen(url_location)
            result_location = json.loads(response.read())

            location = result_location['iss_position']
            lat = location['latitude']
            lon = location['longitude']

            self.m = folium.Map(
                location=[43.507351, 5.127758], 
                tiles="Stamen Toner", 
                zoom_start=2,
                zoom_control=False,
                scrollWheelZoom=False,
                dragging=False
            )

            formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

            MousePosition(
            position="topright",
            separator=" | ",
            empty_string="NaN",
            lng_first=False,
            num_digits=20,
            prefix="Coordinates:",
            lat_formatter=formatter,
            lng_formatter=formatter,
            ).add_to(self.m)

            folium.Marker(
            location = [lat, lon],
            popup = 'ISS',
            icon = folium.Icon(color = 'blue', icon = 'space-shuttle', prefix = 'fa')
            ).add_to(self.m)
            
            data = io.BytesIO()
            self.m.save(data, close_file=False)
            self.view.setHtml(data.getvalue().decode())

            self.entry_infopanel.clear()

            QListWidgetItem("Location ISS:", self.entry_infopanel)
            QListWidgetItem("", self.entry_infopanel)
            QListWidgetItem("latitude: "+ lat, self.entry_infopanel)
            QListWidgetItem("longitude: " + lon, self.entry_infopanel)
        
        else:
            self.get_time_location()
    
    # Function to put in numbers from numpad latitude

    def input_lat(self, pressed):

        if pressed == 'C':
            self.entry_latitude.setText("")
        
        else:
            self.entry_latitude.setText(f'{self.entry_latitude.text()}{pressed}')
    
    # Function to put in numbers from numpad longitude

    def input_lon(self, pressed):

        if pressed == 'C':
            self.entry_longitude.setText("")
        
        else:
            self.entry_longitude.setText(f'{self.entry_longitude.text()}{pressed}')
 
    # Function to get time of a location for ISS to pass by API

    def get_time_location(self):

        if (self.entry_latitude.text()) == "" and (self.entry_longitude.text()) == "":

            QListWidgetItem("No input:", self.entry_infopanel)
            QListWidgetItem("", self.entry_infopanel)
            QListWidgetItem("pass in coordinates", self.entry_infopanel)
            QListWidgetItem("", self.entry_infopanel)

        
        elif (self.entry_latitude.text()) == "":

            if float(self.entry_longitude.text()) < -180 or float(self.entry_longitude.text()) > 180:

                self.entry_infopanel.clear()

                QListWidgetItem("Missing input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in latitude coordinates", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("Wrong input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in right", self.entry_infopanel)
                QListWidgetItem("longitude coordinates", self.entry_infopanel)

                self.entry_latitude.clear()
                self.entry_longitude.clear()
            
            else: 

                self.entry_infopanel.clear()

                QListWidgetItem("Missing input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in latitude coordinates", self.entry_infopanel)
        
        elif (self.entry_longitude.text()) == "":

            if float(self.entry_latitude.text()) < -90 or float(self.entry_latitude.text()) > 90:

                self.entry_infopanel.clear()

                QListWidgetItem("Missing input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in longitude coordinates", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("Wrong input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in right", self.entry_infopanel)
                QListWidgetItem("latitude coordinates", self.entry_infopanel)

                self.entry_latitude.clear()
                self.entry_longitude.clear()
            
            else: 

                self.entry_infopanel.clear()

                QListWidgetItem("Missing input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in longitude coordinates", self.entry_infopanel)

        elif float(self.entry_latitude.text()) < -90 or float(self.entry_latitude.text()) > 90:

            if float(self.entry_longitude.text()) < -180 or float(self.entry_longitude.text()) > 180:
                
                self.entry_infopanel.clear()

                QListWidgetItem("Wrong input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in right", self.entry_infopanel)
                QListWidgetItem("latitude coordinates", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("Wrong input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in right", self.entry_infopanel)
                QListWidgetItem("latitude coordinates", self.entry_infopanel)

                self.entry_latitude.clear()
                self.entry_longitude.clear()

            else: 

                self.entry_infopanel.clear()

                QListWidgetItem("Wrong input:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("pass in right", self.entry_infopanel)
                QListWidgetItem("latitude coordinates", self.entry_infopanel)

                self.entry_latitude.clear()


        elif float(self.entry_longitude.text()) < -180 or float(self.entry_longitude.text()) > 180:

            self.entry_infopanel.clear()

            QListWidgetItem("Wrong input:", self.entry_infopanel)
            QListWidgetItem("", self.entry_infopanel)
            QListWidgetItem("pass in right", self.entry_infopanel)
            QListWidgetItem("longitude coordinates", self.entry_infopanel)

            self.entry_longitude.clear()

        else:

            #get location ISS

            url_location = 'http://api.open-notify.org/iss-now.json'

            response = urllib.request.urlopen(url_location)
            result_location = json.loads(response.read())

            location_ISS = result_location['iss_position']
            lat = location_ISS['latitude']
            lon = location_ISS['longitude']

            # get cityname and country from input coordinates

            try:

                
                location = geolocator.reverse(self.entry_latitude.text() + "," + self.entry_longitude.text(), language='nl')

                loc = location.raw
                loc_dict = location.raw
                loc_dict = loc_dict['address']
                cityname = (loc_dict['city'])
                countryname = (loc_dict['country'])
            
            except:

                cityname = ''
                countryname = ''

            try:

                url_time = 'http://api.open-notify.org/iss-pass.json'
                url_time = url_time + '?lat=' + self.entry_latitude.text() + '&lon=' + self.entry_longitude.text()
                response = urllib.request.urlopen(url_time)
                result = json.loads(response.read())

                over = result['response'][1]['risetime']
                    
                self.entry_infopanel.clear()

                QListWidgetItem("Time ISS will pass over", self.entry_infopanel)
                QListWidgetItem(cityname + " " + countryname, self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("coordinates:", self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem("latitude: "+ self.entry_latitude.text(), self.entry_infopanel)
                QListWidgetItem("longitude: " + self.entry_longitude.text(), self.entry_infopanel)
                QListWidgetItem("", self.entry_infopanel)
                QListWidgetItem(time.ctime(over), self.entry_infopanel)

                self.m = folium.Map(
                location=[43.507351, 5.127758], 
                tiles="Stamen Toner", 
                zoom_start=2,
                zoom_control=False,
                scrollWheelZoom=False,
                dragging=False
                )

                formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

                MousePosition(
                position="topright",
                separator=" | ",
                empty_string="NaN",
                lng_first=False,
                num_digits=20,
                prefix="Coordinates:",
                lat_formatter=formatter,
                lng_formatter=formatter,
                ).add_to(self.m)

                folium.Marker(
                location = [lat, lon],
                popup = 'ISS',
                icon = folium.Icon(color = 'blue', icon = 'space-shuttle', prefix = 'fa')
                ).add_to(self.m)

                folium.Marker(
                location = [self.entry_latitude.text(), self.entry_longitude.text()],
                popup = cityname + ' ' + countryname,
                icon = folium.Icon(color = 'green', icon = 'home', prefix = 'fa')
                ).add_to(self.m)

                data = io.BytesIO()
                self.m.save(data, close_file=False)
                self.view.setHtml(data.getvalue().decode())

            except urllib.error.HTTPError:

                    self.entry_infopanel.clear()

                    QListWidgetItem("Spaceship ISS is", self.entry_infopanel)
                    QListWidgetItem("", self.entry_infopanel)
                    QListWidgetItem("out of range", self.entry_infopanel)
                    QListWidgetItem("", self.entry_infopanel)
                    QListWidgetItem("on this location", self.entry_infopanel)

                    self.m = folium.Map(
                    location=[43.507351, 5.127758], 
                    tiles="Stamen Toner", 
                    zoom_start=2,
                    zoom_control=False,
                    scrollWheelZoom=False,
                    dragging=False
                    )

                    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

                    MousePosition(
                    position="topright",
                    separator=" | ",
                    empty_string="NaN",
                    lng_first=False,
                    num_digits=20,
                    prefix="Coordinates:",
                    lat_formatter=formatter,
                    lng_formatter=formatter,
                    ).add_to(self.m)
                                 
                    folium.Marker(
                    location = [self.entry_latitude.text(), self.entry_longitude.text()],
                    popup = cityname + ' ' + countryname,
                    icon = folium.Icon(color = 'red', icon = 'times', prefix = 'fa')
                    ).add_to(self.m)

                    folium.Marker(
                    location = [lat, lon],
                    popup = 'ISS',
                    icon = folium.Icon(color = 'blue', icon = 'space-shuttle', prefix = 'fa')
                    ).add_to(self.m)

                    data = io.BytesIO()
                    self.m.save(data, close_file=False)
                    self.view.setHtml(data.getvalue().decode())

    # Function to clear the map

    def clear_location(self):
        
        self.entry_infopanel.clear()
        self.entry_latitude.clear()
        self.entry_longitude.clear()

        self.map()


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())