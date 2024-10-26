#tkinter framework used for UI
#PIL for opening images and window backgrounds
#regular expressions for login validation
#sqlite for storing username and password in database
#math for rounding significant figures and using Steinhart–Hart formula
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import re
import sqlite3
from math import log10, floor, exp
import json

#rounds to 3 significant figures which is typically rounded to in physics but also used for display convenience due to fewer numbers
def round_to_3sf(decimal):
    three_sf = floor(log10(abs(decimal)))
    decimal = round(decimal, three_sf)
    return decimal

#ComponentValue class purpose: opens toplevel tkinter window and prompts user to enter ohm/voltage value which then gets passed to circuitmaker class for later calculations.
#inherits TopLevel from tkinter to make child window.
class ComponentValue(Toplevel):
    def __init__(self, component_name):
        #calling superclass constructor
        super().__init__()
        #initialises the value of the component which will later be returned
        self.value = 0
        #creates instance
        self.component_name = component_name
        # Create the input label and entry widget based on the component name
        if component_name == "resistor": #if resistor is the argument, user is required to enter an ohm value.
            self.colour = '#8DB600' #frontend configurations including background colour, making labels and making entry labels.
            self['bg'] = self.colour
            self.input_label = Label(self, text="Enter resistance of resistor (Ω)", font=('Rockwell', 10, 'bold'), bg=self.colour)
            self.input_label.pack()
            self.input_entry = Entry(self, font=('Rockwell', 10, 'bold'))
            self.input_entry.pack()

        elif component_name == "var_resistor": #if var_resistor is the argument, user is required to enter an ohm value.
            self.colour = '#478778' #frontend configurations including background colour, making labels and making entry labels.
            self['bg'] = self.colour
            self.input_label = Label(self, text="Enter resistance of variable resistor (Ω)", font=('Rockwell', 10, 'bold'), bg=self.colour)
            self.input_label.pack()
            self.input_entry = Entry(self, font=('Rockwell', 10, 'bold'))
            self.input_entry.pack()

        elif component_name == "thermistor":#if thermistor is the argument, user is required to scroll the tkinter scale to adjust temperature.
            self.colour = '#8DB600' #frontend configurations including background colour, making labels and making entry labels.
            self.colour = 'black'
            self['bg'] = self.colour
            self.input_label = Label(self, text="Adjust simulated temperature (°C)", font=('Rockwell', 10, 'bold'), fg='#ffffff', bg=self.colour)
            self.input_label.pack()
            # tkinter scale from -100 to 100 which represents °C. Command is update_value, which displays converted value of Kelvins (K) and ohms (Ω)
            self.input_entry = Scale(self, from_=-100, to=100, orient=HORIZONTAL, command=self.update_value)
            self.input_entry.pack()
            self.value_label = Label(self, text="", font=('Rockwell', 10, 'bold'), bg=self.colour)
            self.value_label.pack()

        elif component_name == "battery": #if resistor is the argument, user is required to enter an ohm value.
            self.colour = '#5F8575' #frontend configurations including background colour, making labels and making entry labels.
            self['bg'] = self.colour
            self.input_label = Label(self, text="Enter potential difference (V)", font=('Rockwell', 10, 'bold'), bg=self.colour)
            self.input_label.pack()
            self.input_entry = Entry(self, font=('Rockwell', 10, 'bold'))
            self.input_entry.pack()


        self.output_label = Label(self, text="", font=('Rockwell', 10, 'bold'), bg=self.colour) #displays error messages
        self.output_label.pack()
        # Create the OK button to submit the input
        input_button = Button(self, text="Set value", command=self.value_input, font=('Rockwell', 10, 'bold'), fg='#ffffff', bg=self.colour)
        input_button.pack()

    #this method returns the final value which the user previously inputted
    def value_input(self):
        if self.component_name == "thermistor":
            #conversion method used to convert obtained value from user input for thermistor only
            converted_resistance = self.convert_temp(self.input_entry.get())
            self.value = converted_resistance #final value is stored
        else:
            #gets inputted value if not thermistor
            input_value = int(self.input_entry.get())
            #limits the input range
            if input_value <= 0 or input_value > 500:
                self.output_label.config(text="Invalid input.", bg=self.colour)
                return #exits method and returns to caller
            self.value = input_value #final value is stored
        self.value = round_to_3sf(self.value) #method used to round value to 3sf using math expressions
        self.destroy() #closes toplevel tkinter window

    def update_value(self, temperature):
        #exclusive for thermistor only just for graphics
        temperature_int = int(temperature)
        if temperature_int < -50: #if temperature less than -50, colour of kelvin and ohm value label is light blue
            self.value_label.config(fg="#6bbcd1")
        elif temperature_int < 0: #if temperature less than -50, colour of kelvin and ohm value label is dark blue
            self.value_label.config(fg="#4665d4")
        elif temperature_int < 25: #if temperature less than -50, colour of kelvin and ohm value label is yellow
            self.value_label.config(fg="#ffe561")
        elif temperature_int < 50: #if temperature less than -50, colour of kelvin and ohm value label is orange
            self.value_label.config(fg="#fd9415")
        else: #if temperature less than -50, colour of kelvin and ohm value label is red
            self.value_label.config(fg="#e23201")
        converted_resistance = self.convert_temp(temperature_int) #temperature passed into parameter of convert_temp to be converted to resistance
        kelvin = round((temperature_int + 273.15),2) #formula for conversion of °C to Kelvins (K), rounded to 2dp
        self.value_label.config(text=str(kelvin) + " Kelvins\n" + str(converted_resistance)+"Ω")

        #re-arranged version of Steinhart-Hart equation to convert temperature to resistance
    def convert_temp(self, temperature):
        if self.component_name == "thermistor":
            r0 = 50  # resistance at reference temperature, known as nominal resistance
            t0 = 75.0  # reference temperature in Celsius, known as nominal temperature
            B = 3950.0  # common coefficient value of thermistors
            converted_temperature = temperature + 273.15 #formula for conversion of °C to Kelvins (K)
            r = r0 * exp(B * (1 / (t0 + 273.15) - 1 / converted_temperature)) #rearranged Steinhart-Hart equation to calculate resistance
            r = round(r, 2) #rounding resistance to 2dp
            return r #returns resistance value to caller which will then be stored in value attribute

#Authentication class purpose: First window opened in app, where its purpose is to prompt the user for login details.
class Authentication():
    def __init__(self, authwindow): #parameter is for a tkinter window which will be the first thing to be called in the main level.
        self.window = authwindow #instance stored
        #initializing everything in init function and making frontend
        self.window.geometry(str(800) + "x" + str(600))

        #opening background image from file and setting as background
        self.loginbg = ImageTk.PhotoImage(Image.open("wallpaper/bg1.jpg"))
        background_label = Label(self.window, image=self.loginbg)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.username = ""

        #headings and subheadings
        self.window.title("CircuitSim Login")
        title_text = Label(self.window, text="CircuitSim", font=("Rockwell", 60, 'bold'), fg="white", bg='#000000',
                           borderwidth=4,
                           relief="sunken")
        title_text.pack(pady=80)

        #initializing username label and entry
        username_label = Label(self.window, text="Username", font=('Rockwell', 20, 'bold'), fg="white", bg="#000000")
        username_label.pack()
        #tkinter entrybox where user will enter details
        self.username_entry = Entry(self.window, width=30, font=('Rockwell', 20, 'bold'), bg='#dff7d2')
        self.username_entry.pack()

        #initializing username label and entry
        password_label = Label(self.window, text="Password", font=('Rockwell', 20, 'bold'), fg="white", bg="#000000")
        password_label.pack()
        self.password_entry = Entry(self.window, show="•", width=30, font=('Rockwell', 20, 'bold'), bg='#dff7d2')
        self.password_entry.pack()

        #initializing register and signin buttons
        register_button = Button(self.window, text="Register", font=('Rockwell', 10, 'bold'), fg="white", bg='#0f1c14',
                                 command=self.register)
        register_button.pack(pady=10)

        signin_button = Button(self.window, text="Sign In", font=('Rockwell', 10, 'bold'), fg="white", bg='#0f1c14',
                               command=self.login)
        signin_button.pack()

        #initializing output label for messages to user
        self.output_label = Label(self.window, bg="#000000", font=('Rockwell', 8, 'bold'), fg="white")
        self.output_label.pack(pady=4)

        #connecting to local database
        connect = sqlite3.connect('UserDetails.db')

        #SQL query to create the table 'USERS' if it does not exist in the local files. Table format is (username, password)
        connect.execute('''CREATE TABLE IF NOT EXISTS USERS(USERNAME TEXT, PASSWORD TEXT);''')

        #closing connection with local database
        connect.close()

    #to be accessed once authentication is successful
    def to_circuitpage(self):
        #creates instance of CircuitMaker class and passing tkinter window as argument
        circuitpage = Tk()
        circuitpage.resizable(False, False)
        self.circuitapp = CircuitMaker(circuitpage, self.username)
        #places window roughly in center of screen
        circuitpage.eval('tk::PlaceWindow . center')
        #starts main event loop of tkinter window
        circuitpage.mainloop()

    #input validation with regular expressions
    def validate_password(self, password):
        if len(password) < 8: #if the password is less than 8 characters, validation failed
            return False
        if not re.search("[a-z]", password): #password must have lowercase, else validation failed
            return False
        if not re.search("[A-Z]", password): #password must have uppercase, else validation failed
            return False
        if not re.search("[0-9]", password): #password must have at least 1 number, else validation failed
            return False
        return True #if all validation if statements conditions are satisfied, then validation successful

    #registration method, accessed if user clicks registration button
    def register(self):
        #takes user's input from entry label
        username = self.username_entry.get()
        password = self.password_entry.get()

        #if username and password is empty and this method is accessed, method execution is stopped
        if not username or not password:
            self.output_label.config(text="Missing username or password.")
            return #returns to caller

        #else the password is invalid if any of validate_password's conditions are not met
        elif not self.validate_password(password):
            #configurates output label to display error message
            self.output_label.config(
                text="Invalid password. It should be at least 8 characters long and contain a mix of uppercase and lowercase letters and numbers.")
            return

        else:
            #if all negative if statements are dodged, local SQL database is connected
            connect = sqlite3.connect('UserDetails.db')

            #tries to compare details. if error is encountered, entire program is aborted due to database failure, however this is highly unlikely since the database is local
            try:
                cur = connect.cursor() #allows traversal of database records
                # executes SQL query. ? is a parameter notation, while username is an argument which is passed into it.
                cur.execute("SELECT * FROM USERS WHERE USERNAME = ?;", (username,)) #selects username of the username which the user inputs
                check = cur.fetchall() #fetches the username which the user entered if it exists, otherwise it fetches nothing

                if check: #if check has the user's entered username, they'll have to enter another username.
                    self.output_label.config(text="Username already exists.")
                else:
                    #inserts the new username and the user's password into the local SQL database's table 'USERS'
                    cur.execute("INSERT INTO USERS VALUES (?, ?);", (username, password,))
                    self.username = username
                    connect.commit() #the changes to the database are now committed and permanent
                    self.output_label.config(text=("Welcome, " + str(username)))#delays 3 seconds and welcomes user
                    self.window.destroy() #closes window
                    self.to_circuitpage()#calls to_circuitpage() method which creates an instance of CircuitMaker class, opening its window
            except:
                # if error found, app is closed as well as connection with 3 second delay
                self.output_label.config(text="Error while inserting data. Aborting connection...")
                connect.close()
                exit()

    #login method, accessed if user clicks registration button
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        #similar to registration method, if username and password is empty and this method is accessed, method execution is stopped
        if not username or not password:
            self.output_label.config(text="Missing username or password.")
            return

        else:
            #local SQL database is connected
            connect = sqlite3.connect('UserDetails.db')
            #tries to compare details. if error is encountered, entire program is aborted due to database failure, however this is highly unlikely since the database is local
            try:
                cur = connect.cursor() #allows traversal of database records
                #passes username and password into ? parameters
                cur.execute("SELECT * FROM USERS WHERE (USERNAME, PASSWORD) = (?, ?);", (username, password)) #selects username and password which are the exact copy if they exist
                check = cur.fetchall() #fetches details if it exists in the local SQL database

                if not check: #if check is empty and no details were found, error message displayed
                    self.output_label.config(text="Incorrect username/password or account not found")
                else: #welcomes user and makes 3 second delay before closing window
                    self.output_label.config(text=("Welcome, " + str(username)))
                    self.username = username
                    self.window.destroy() #closes window
                    self.to_circuitpage() #calls to_circuitpage() method which creates an instance of CircuitMaker class, opening its window
            except:
                # if error found, app is closed as well as connection with 3 second delay
                self.output_label.config(text="Error while fetching data. Aborting connection...")
                connect.close()
                exit()

#purpose of JSONCanvas class is to export the entire canvas into JavaScript objectn otation.
#it supports saving all widgets of the tkinter canvas, and also loading all widgets from the canvas
class JSONCanvas:
    def __init__(self, canvas, line_ids, graph, battery_exists, varesistor_exists, switch_exists, thermistor_exists, totalcomponents, voltmeters):
        #making instances of contents passed through parameters
        self.canvas = canvas
        self.line_ids = line_ids
        self.graph = graph
        self.battery_exists = battery_exists
        self.varesistor_exists = varesistor_exists
        self.switch_exists = switch_exists
        self.thermistor_exists = thermistor_exists
        self.totalcomponents = totalcomponents
        self.voltmeters = voltmeters

    #method to save the tkinter canvas into user-specfic JSON file
    def save_to_json(self, filename):
        #makes dictionary with all tkinter widget attributes
        data = {"widgets": [], "line_ids": self.line_ids, "graph": self.graph, "attributes": {
            "battery_exists": self.battery_exists,
            "varesistor_exists": self.varesistor_exists,
            "switch_exists": self.switch_exists,
            "thermistor_exists": self.thermistor_exists,
            "totalcomponents": self.totalcomponents,
            "voltmeters" : self.voltmeters
        }}

        #gets all widgets of the canvas
        for item in self.canvas.find_all():
            #determines widget type
            widget_type = self.canvas.type(item)
            #if it is a text widget, it will obtain the x, y coords as well as the text itself and the font
            if widget_type == "text":
                widget_data = {
                    "type": "text",
                    "x": self.canvas.coords(item)[0],
                    "y": self.canvas.coords(item)[1],
                    "text": self.canvas.itemcget(item, "text"),
                    "font": self.canvas.itemcget(item, "font"),
                }
            #if it is an image, it will obtain the x coords, y coords and the tags of the image
            elif widget_type == "image":
                widget_data = {
                    "type": "image",
                    "x": self.canvas.coords(item)[0],
                    "y": self.canvas.coords(item)[1],
                    "tags": self.canvas.gettags(item),
                }
            #obtains target x,y value pair and source x,y value pair as well as the line width
            elif widget_type == "line":
                widget_data = {
                    "type": "line",
                    "x1": self.canvas.coords(item)[0],
                    "y1": self.canvas.coords(item)[1],
                    "x2": self.canvas.coords(item)[2],
                    "y2": self.canvas.coords(item)[3],
                    "width": self.canvas.itemcget(item, "width"),
                }
            else:
                # Unsupported widget type, so we skip it
                continue
            #assigns value to widget which will be differently assigned based on widget_type
            data["widgets"].append(widget_data)

        #opens file in write mode. Overwrites current content if it exists, otherwise it will make a new JSON file
        with open(filename, "w") as savefile:
            #dumps all contents from data dictionary
            json.dump(data, savefile)

    def load_from_json(self, filename):
        with open(filename, "r") as loadfile:
            #loads JSON contents
            data = json.load(loadfile)
        #slices value from data key and assigns it to attributes
        self.line_ids = data["line_ids"]
        self.graph = data["graph"]
        self.battery_exists = data['attributes']['battery_exists']
        self.varesistor_exists = data['attributes']['varesistor_exists']
        self.switch_exists = data['attributes']['switch_exists']
        self.thermistor_exists = data['attributes']['thermistor_exists']
        self.totalcomponents = data['attributes']['totalcomponents']
        self.voltmeters = data['attributes'].get('voltmeters', [])


        #stores instance of image to prevent it from being erased from canvas instantly
        image_cache = {}
        for widget_data in data["widgets"]:
            #creates_text exactly how it looked before it was saved wit the same coordinates, text and font
            if widget_data["type"] == "text":
                item = self.canvas.create_text(
                    widget_data["x"], widget_data["y"],
                    text=widget_data["text"],
                    font=widget_data["font"],
                )
            #creates image exactly how it looked before saving, keeping all tags of the image
            elif widget_data["type"] == "image":
                #this try-except accesses the 4th or 3rd tag of the image, which contains the direct filepath of the image
                try:
                    image_path = widget_data["tags"][4]
                except:
                    image_path = widget_data["tags"][3]
                #makes the image creatable and stores image instance if it does not exist in image_cache dictionary, otherwise it is loadde
                if image_path not in image_cache:
                    image = ImageTk.PhotoImage(Image.open(image_path))
                    image_cache[image_path] = image
                else:
                    image = image_cache[image_path]

                #same image is created with same coords and tags
                item = self.canvas.create_image(
                    widget_data["x"], widget_data["y"],
                    image=image
                )
                self.canvas.itemconfig(item, tags=widget_data["tags"])
                # Store the image as a property of the canvas widget
                self.canvas.image_cache = image_cache

            #same line is creates with same source and target coordinate pairs as well as same width
            elif widget_data["type"] == "line":
                item = self.canvas.create_line(
                    widget_data["x1"], widget_data["y1"],
                    widget_data["x2"], widget_data["y2"],
                    width=widget_data["width"],
                )
        #returns long one-dimensional list which will be sent to the caller in the CircuitMaker class to then be sliced and stored
        return [self.line_ids,self.graph, self.battery_exists, self.varesistor_exists, self.switch_exists, self.thermistor_exists, self.totalcomponents, self.voltmeters]


#Circuitmaker class purpose: Second window opened in app where entire interactive simulation takes place. It has majority of the frontend of the program.
#User can add componetns to their simulation canvas, drag them around, and open a new window to choose which components to connect.
#A guide is available to guide the user to how to identify components and make their circuit.
#Premade circuits are useable as well. Once the button is pressed, an instance of the Preset class is made which will inherit TopLevel and become a top level window
#To show simulation results, an instance of the Simulate class will be created and will inherit TopLevel.
class CircuitMaker:
    line_ids = [] #stores all line_ids which will be later accessed for animation purposes
    def __init__(self, circuitwindow, username):
        self.window = circuitwindow #stored instance of tkinter window
        #initialization and frontend

        #opening background image from file and setting as background
        self.mainbg = ImageTk.PhotoImage(Image.open("wallpaper/bg1.jpg"))
        self.username = username
        background_label = Label(self.window, image=self.mainbg)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.window.title("Circuit Maker")

        #setting up window and canvas dimensions and colour
        self.window.geometry(str(800) + "x" + str(600))
        self.canvas = Canvas(self.window, width=650, height=550, bg="#ffffff")
        self.canvas.pack(side=RIGHT, anchor=SE)

        #title text Label
        title = Label(self.window, text="CircuitSim", font=('Rockwell', 20, 'bold'), anchor=N, fg='white', bg="black", relief = "solid",
                      borderwidth=4)
        title.place(x=330, y=0)

        welcome = Label(self.window, text="Welcome, " + self.username, font=('Rockwell', 10, 'bold'), fg='white', bg="black", relief = "raised",
                      borderwidth=4)
        welcome.place(x=600, y=0)
        self.component_array = [] #setting up data structure to hold internal component IDs in array
        self.graph = {} #stores graph which represents circuit. The source graph dictionary is in the WireGeneration class, but that will later be stored into this
        self.component_limit = 5 #max number of components in simulation
        self.id = 0 #a counter which the user can use to connect and identify components easier

        #initialization of values
        self.volts = 0
        self.amps = 0
        self.ohms = 0
        self.temperature = 0

        # instance of self.id stored exclusively of variable resistor and thermistor
        self.var_IDinstance = 0
        self.therm_IDinstance = 0
        self.switchIDinsance = 0
        #flags to detect switch status
        self.switched_on = True
        self.total_components = 0
        self.voltmeters = []
        self.json_loaded = False
        #flags to check if these components exist on the canvas
        self.thermistor_exists = False
        self.varesistor_exists = False
        self.switch_exists = False
        self.battery_exists = False

        #flag to detect if Simulate button has been pressed
        self.simbutton_on = False

        #initially false. These are for line creation purposes to represent wires.
        self.vertical_parallel = False
        self.horizontal_parallel = False

        #directories of images passed as arguments into open_img method for better efficiency
        self.battery_path = "component_img/battery.png"
        self.resistor_path = "component_img/resistor.png"
        self.varesistor_path = "component_img/var_resistor.png"
        self.thermistor_path = "component_img/thermistor.png"
        self.switchon_path = "component_img/switch_on.png"
        self.switchoff_path = "component_img/switch_off.png"
        self.voltmeter_path = "component_img/voltmeter.png"
        self.ammeter_path = "component_img/ammeter.png"
        self.lightbulboff_path = "component_img/lightbulb_off.png"
        self.lightbulbon_path = "component_img/lightbulb_on.png"

        self.battery_image = self.open_img(self.battery_path)
        self.cheatsheet = self.open_img("cheatsheet.png")
        self.resistor_image = self.open_img(self.resistor_path)
        self.varesistor_image = self.open_img(self.varesistor_path)
        self.thermistor_image = self.open_img(self.thermistor_path)
        self.switchon_image = self.open_img(self.switchon_path)
        self.switchoff_image = self.open_img(self.switchoff_path)
        self.voltmeter_image = self.open_img(self.voltmeter_path)
        self.ammeter_image = self.open_img(self.ammeter_path)
        self.lightbulboff_image = self.open_img(self.lightbulboff_path)
        self.lightbulbon_image = self.open_img(self.lightbulbon_path)

        self.guide1_img = self.open_img("guide/guide1.png")
        self.guide2_img = self.open_img("guide/guide2.png")

        #setting hotbar with buttons. The commands of these buttons access the methods which add the components onto the canvas
        self.components_heading = Label(self.window, text="Components", font=('Rockwell', 15, 'bold'), fg='white',
                                        bg='#000000', borderwidth=4, relief="raised")
        self.components_heading.place(x=6, y=64)

        self.button_resistor = Button(self.window, text="Resistor", font=('Rockwell', 10, 'bold'), fg='white',
                                      bg='#0f1c14', command=self.add_resistor)
        self.button_resistor.place(x=38, y=100)

        self.button_varesistor = Button(self.window, text="Variable Resistor", font=('Rockwell', 10, 'bold'), fg='white',
                                        bg='#0f1c14', command=self.add_varesistor)
        self.button_varesistor.place(x=10, y=130)

        self.button_thermistor = Button(self.window, text="Thermistor", font=('Rockwell', 10, 'bold'), fg='white',
                                        bg='#0f1c14', command=self.add_thermistor)
        self.button_thermistor.place(x=30, y=160)

        self.button_battery = Button(self.window, text="Battery", font=('Rockwell', 10, 'bold'), fg='white',
                                     bg='#0f1c14', command=self.add_battery)
        self.button_battery.place(x=42, y=190)

        self.button_switch = Button(self.window, text="Switch", font=('Rockwell', 10, 'bold'), fg='white', bg='#0f1c14',
                                    command=self.add_switch)
        self.button_switch.place(x=44, y=220)

        self.button_voltmeter = Button(self.window, text="Voltmeter", font=('Rockwell', 10, 'bold'), fg='white',
                                       bg='#0f1c14', command=self.add_voltmeter)
        self.button_voltmeter.place(x=34, y=250)

        self.button_ammeter = Button(self.window, text="Ammeter", font=('Rockwell', 10, 'bold'), fg='white',
                                     bg='#0f1c14', command=self.add_ammeter)
        self.button_ammeter.place(x=38, y=280)

        self.button_lightbulb = Button(self.window, text="Lightbulb", font=('Rockwell', 10, 'bold'), fg='white',
                                       bg='#0f1c14', command=self.add_lightbulb)
        self.button_lightbulb.place(x=36, y=310)

        self.button_wire = Button(self.window, text="Wire", font=('Rockwell', 10, 'bold'), fg='white',
                                  bg='#0f1c14', command=self.add_line)
        self.button_wire.place(x=48, y=340)

        #button which clears canvas
        self.clear_button = Button(self.window, text="Clear all", font=('Rockwell', 12, 'bold'), fg='white',
                                    bg='#0f1c14', command=self.clear_canvas)
        self.clear_button.place(x=32, y=380)

        self.run_button = Button(self.window, text="Simulate!", font=('Rockwell', 15, 'bold'), fg='white', bg='#420a06', command=self.run_circuit)
        self.run_button.place(x=16, y=420)

        self.preset_button = Button(self.window, text="Load circuit", font=('Rockwell', 12, 'bold'), fg='white',
                                    bg='#0f1c14', command=lambda: self.load_presets)
        self.preset_button.place(x=15, y=470)

        self.save_button = Button(self.window, text="Save Circuit", font=('Rockwell', 12, 'bold'), fg='white', bg='#0f1c14', command = self.save_canvas)
        self.save_button.place(x=15, y=510)

        self.guide_button = Button (self.canvas, text="Guide", font=('Rockwell', 11, 'bold'), fg='white', bg='#bf674d', command=self.display_guide)
        self.guide_button.place(x=0)

        self.cheatsheet_button = Button(self.canvas, text="Cheatsheet", font=('Rockwell', 11, 'bold'), fg='white', bg='#7d2c37',
                                   command=self.show_cheatsheet)
        self.cheatsheet_button.place(x=560)

        self.load_preset_button = Button (self.window, text="Load Preset", font=('Rockwell', 11, 'bold'), fg='white', bg='#0f1c14', command=self.load_presets)
        self.load_preset_button.place(x=18, y=545)

    #method to open image file using PIL library
    def open_img(self,imagefile):
        canvas_img=ImageTk.PhotoImage(Image.open(imagefile))
        return canvas_img

    #method to toggle switch
    def toggle(self):
        #finds internal tkinter ID of switch
        switch = self.canvas.find_withtag("switch")[0]
        self.id = self.switchIDinsance
        self.image_ID = "ID" + str(self.id)
        self.switched_on = not self.switched_on #performs NOT operation on boolean value
        if self.switched_on: #if switched_on is True
            self.switch_button.config(text="ON", bg="#66963b") #configure colour,text and image to represent that it is on
            self.canvas.itemconfig(switch, image=self.switchon_image, tags=(self.id, self.image_ID, 'switch', self.switchon_path) )
        else:
            self.switch_button.config(text="OFF", bg="#a80d22") #configure colour,text and image to represent that it is off
            self.canvas.itemconfig(switch, image=self.switchoff_image, tags=(self.id, self.image_ID, 'switch', self.switchoff_path))

    #basic method to open toplevel window to display guide. This is a straightforward label which only uses labels.
    def display_guide(self):
        guide_window = Toplevel()
        guide_window.title("Guide")
        guide_window["bg"] = "#ffeeb0"
        guide1_text = Label(guide_window, text="Key for component images", font=('Rockwell', 10, 'bold'), fg='white', bg='#bf674d', relief = "groove")
        guide1_text.pack(pady=4)
        guide1_label = Label(guide_window, image=self.guide1_img, bg="#ffeeb0")
        guide1_label.pack(pady=10)
        guide2_text = Label(guide_window, text="Given that B is clockwise of A, enter IDs", font=('Rockwell', 10, 'bold'), fg='white', bg='#bf674d', relief = "groove")
        guide2_text.pack(pady=4)
        guide2_label = Label(guide_window, image=self.guide2_img, bg="#ffeeb0")
        guide2_label.pack()
        close_button = Button(guide_window, text="Close", font=('Rockwell', 11, 'bold'), fg='white', bg='#bf674d', relief = "groove", command=guide_window.destroy)
        close_button.pack()

    # basic method to open toplevel window to display educational cheatsheet to help student
    def show_cheatsheet(self):
        info_window = Toplevel()
        info_window.title("Cheatsheet")
        info_window["bg"] = "#d66b6b"
        cheatsheet_img = Label(info_window, image=self.cheatsheet, bg="#d66b6b")
        cheatsheet_img.pack()
        close_button = Button(info_window, text="Close", font=('Rockwell', 11, 'bold'), fg='white', bg='#2b0000', relief = "groove", command=info_window.destroy)
        close_button.pack()

    #method to add draggable resistor component in the middle of the canvas.
    def add_resistor(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the resistor
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        else:
            window = ComponentValue("resistor") #stores instance of ComponentValue class, passing the argument, "resistor"
            window.wait_window() #prevents further execution of method until window closed
            self.ohms = window.value #assigns the value attribute from the ComponentValue window to the ohms attribute
            if self.ohms: #if a value has been assigned, the following will be executed.
                self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
                self.component_limit -= 1 #decrements the component limit
                self.image_ID = "ID" + str(self.id)

                #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
                self.component = self.canvas.create_image(400, 300, image=self.resistor_image, tags=(self.id, self.ohms, self.image_ID, 'resistor',self.resistor_path))

                #displays resistor ohm value
                self.value_display = self.canvas.create_text(388, 317.5, text=str(self.ohms) + "Ω")

                #displays component ID
                self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

                #appends the image and text which was crated so that they can be dragged together relatively
                self.component_array.append([self.value_display, self.component, self.id_text])

                #binds the left mouse button to the method 'drag_component'
                self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

    def add_varesistor(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the variable resistor
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        elif self.varesistor_exists:
            messagebox.showwarning("Cannot add component","Variable resistor already in simulation.")
        else:
            window = ComponentValue("var_resistor")#stores instance of ComponentValue class, passing the argument, "variable resistor"
            window.wait_window() #prevents further execution of method until window closed
            self.ohms = window.value #assigns the value attribute from the ComponentValue window to the ohms attribute
            if self.ohms: #if a value has been assigned, the following will be executed.
                self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
                self.var_IDinstance = self.id #stores instance of tag in the case of when the user modifies the variable resistor
                self.varesistor_exists = True #flag to show that a variable resistor has been made
                self.component_limit -= 1 #decrements the component limit
                self.image_ID = "ID" + str(self.id)

                #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
                self.component = self.canvas.create_image(400, 300, image=self.varesistor_image,
                                                          tags=(self.id, self.ohms, self.image_ID, 'varesistor',self.varesistor_path))

                #displays variable resistor value
                self.VR_value_display = self.canvas.create_text(388, 317.5, text=str(self.ohms) + "Ω")

                #displays the custom ID
                self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

                #appends the image and text which was crated so that they can be dragged together relatively
                self.component_array.append([self.VR_value_display, self.component, self.id_text])

                #binds the left mouse button to the method 'drag_component'
                self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

                #button which allows user to modify variable resistor
                self.button_varesistor = Button(self.canvas, text="Adjust Variable Resistor", font=('Rockwell', 10, 'bold'), fg='white', bg='#456142', command=self.modify_varesistor)
                self.button_varesistor.place(x=310, y=520)

    def modify_varesistor(self):
        window = ComponentValue("var_resistor") #stores instance of ComponentValue class again to reaccess the window, passing the argument, "variable resistor"
        window.wait_window() #prevents further execution of method until window closed
        if window.value: #if a value has been assigned, the following will be executed.
            self.ohms = window.value #assigns the value attribute from the ComponentValue window to the ohms attribute
            self.image_ID = "ID" + str(self.id)

            #adjusts the tags and display based on the new ohm value
            self.canvas.itemconfig(self.VR_value_display, text=str(self.ohms)+"Ω")
            self.canvas.itemconfigure(self.component, tags=(self.var_IDinstance, self.ohms, self.image_ID, 'varesistor',self.varesistor_path))

    def add_thermistor(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the thermistor
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        elif self.thermistor_exists:
            messagebox.showwarning("Cannot add component", "Variable resistor already in simulation.")
        else:
            window = ComponentValue("thermistor") #stores instance of ComponentValue class, passing the argument, "thermistor"
            window.wait_window() #prevents further execution of method until window closed
            self.ohms = window.value #assigns the value attribute from the ComponentValue window to the ohms attribute
            if self.ohms: #if a value has been assigned, the following will be executed.
                self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
                self.therm_IDinstance = self.id #stores instance of tag in the case of when the user wants to modify the temperature
                self.thermistor_exists = True #flag to show that a thermistor has been made
                self.component_limit -= 1 #decrements the component limit
                self.image_ID = "ID" + str(self.id)

                #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
                self.component = self.canvas.create_image(400, 300, image=self.thermistor_image,
                                                          tags=(self.id, self.ohms, self.image_ID, 'thermistor',self.thermistor_path))

                #displays thermistor
                self.T_value_display = self.canvas.create_text(388, 317.5, text=str(self.ohms)+"Ω")

                #displays component ID
                self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

                #appends the image and text which was crated so that they can be dragged together relatively
                self.component_array.append([self.T_value_display, self.component, self.id_text])

                #binds the left mouse button to the method 'drag_component'
                self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

                #button which allows user to modify temperature which will then change resistance
                self.button_thermsistor = Button(self.canvas, text="Adjust Temperature", font=('Rockwell', 10, 'bold'), fg='white', bg='#142629', command=self.modify_thermistor)
                self.button_thermsistor.place(x=160, y=520)


    def modify_thermistor(self):
        window = ComponentValue("thermistor") #stores instance of ComponentValue class again to reaccess the window, passing the argument, "thermistor"
        window.wait_window() #prevents further execution of method until window closed
        if window.value: #if a value has been assigned, the following will be executed.
            self.ohms = window.value #assigns the value attribute from the ComponentValue window to the ohms attribute
            self.image_ID = "ID" + str(self.id)

            # adjusts the tags and display based on the new ohm value
            self.canvas.itemconfig(self.T_value_display, text=str(self.ohms)+"Ω")
            self.canvas.itemconfigure(self.component, tags=(self.therm_IDinstance, self.ohms, self.image_ID, 'thermistor',self.thermistor_path))

    def add_battery(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the battery
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        elif self.battery_exists:
            messagebox.showwarning("Cannot add component", "Battery already in simulation. You can enter any positive potential difference instead of requiring multiple cells.")
        else:
            window = ComponentValue("battery") #stores instance of ComponentValue class, passing the argument, "battery"
            window.wait_window() #prevents further execution of method until window closed
            self.volts = window.value #assigns the value attribute from the ComponentValue window to the volts attribute
            if self.volts:
                self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
                self.battery_exists = True #flag to show that a battery has been made
                self.component_limit -= 1 #decrements component limit
                self.image_ID = "ID" + str(self.id)

                #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
                self.component = self.canvas.create_image(400, 300, image=self.battery_image, tags=(self.id, self.volts, self.image_ID, 'battery', self.battery_path))

                #displays voltage
                self.value_display = self.canvas.create_text(388, 317.5, text=str(self.volts) + "V")

                #displays component ID
                self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

                #appends the image and text which was crated so that they can be dragged together relatively
                self.component_array.append([self.value_display, self.component, self.id_text])

                #binds the left mouse button to the method 'drag_component'
                self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

    def add_switch(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the switch
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        elif self.switch_exists:
            messagebox.showwarning("Cannot add component", "Switch already in simulation")
        else:
            self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
            self.switchIDinsance = self.id
            self.switch_exists = True #flag to show that a battery has been made
            self.component_limit -= 1 #decrements component limit

            self.image_ID = "ID" + str(self.id)

            #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
            self.component = self.canvas.create_image(400, 300, image=self.switchon_image, tags=(self.id, self.image_ID, 'switch', self.switchon_path))

            #displays component ID
            self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

            #appends the image and text which was crated so that they can be dragged together relatively
            self.component_array.append([self.component, self.id_text])

            #binds the left mouse button to the method 'drag_component'
            self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)
            self.switch_label = Label(self.canvas, text="Switch ON/OFF: ", font=('Rockwell', 10, 'bold'), bg="#ffffff")
            self.switch_label.place(x=460, y=522)

            #creates button which accesses toggle method. When pressed, button should alternate in text and colour, and the button_presesd boolean variable should switch
            self.switch_button = Button(self.canvas, width=7, height=1, text="ON", font=('Rockwell', 10, 'bold'), bg ="#66963b", command=self.toggle)
            self.switch_button.place(x=580, y=520)

    def add_voltmeter(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the voltmeter
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        else:
            self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
            self.image_ID = "ID" + str(self.id)

            #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
            self.component = self.canvas.create_image(400, 300, image=self.voltmeter_image, tags=(self.id, self.image_ID, 'voltmeter',self.voltmeter_path))

            #displays component ID
            self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

            #appends the image and text which was crated so that they can be dragged together relatively
            self.component_array.append([self.component, self.id_text])

            #binds the left mouse button to the method 'drag_component'
            self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

            #decrements component limit
            self.component_limit -= 1

    def add_ammeter(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the ammeter
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        else:
            self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
            self.component_limit -= 1 #decrements component limit
            self.image_ID = "ID" + str(self.id)

            #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
            self.component = self.canvas.create_image(400, 300, image=self.ammeter_image, tags=(self.id, self.image_ID, 'ammeter',self.ammeter_path))

            #displays component ID
            self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

            #appends the image and text which was crated so that they can be dragged together relatively
            self.component_array.append([self.component, self.id_text])

            #binds the left mouse button to the method 'drag_component'
            self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)


    def add_lightbulb(self):
        if self.component_limit==0: #if this is equal to 0, an error message pops up and the the user cannot add the lightbulb
            messagebox.showinfo("Cannot add component","You already have the maximum of 5 components in your simulation.")
        else:
            self.id += 1 #increments the custom component ID by 1 which will be used for component identification purposes
            self.component_limit -= 1 #decrements component limit
            self.image_ID = "ID" + str(self.id)

            #creates the tkinter widget which is draggable. It has tags which can be accessed using find_withtags() and itemcget()
            self.component = self.canvas.create_image(400, 300, image=self.lightbulboff_image, tags=(self.image_ID, self.id, 'lightbulb', self.lightbulboff_path))

            #displays component ID
            self.id_text = self.canvas.create_text(420, 317.5, text=self.id)

            #appends the image and text which was crated so that they can be dragged together relatively
            self.component_array.append([self.component, self.id_text])

            #binds the left mouse button to the method 'drag_component'
            self.canvas.tag_bind(self.component, '<B1-Motion>', self.drag_component)

    def add_line(self):
        ID_window = WireGeneration(self.canvas) #passes the canvas of CircuitMaker to the instance of the toplevel window of the WireGeneration class
        ID_window.wait_window() #method will only be executed until window is closed
        image_tags = ID_window.IDpair #once closed, the pair of image_tags is retrieved
        self.graph = ID_window.graphdic #the graphical dictionary representation of the circuit is also taken in
        self.voltmeters = ID_window.voltmeters

        connect_to_parallel = ID_window.checkbox_input() #returns a boolean expression which would have been determined based on a checkbox

        connecting_voltmeter = ID_window.voltmeterflag #returns a boolean expression which reflects if the connection was with a voltmeter

        def position_line(): #puts all lines at the lowest layer of the canvas behind everything
            self.canvas.lower(line1)
            if not connecting_voltmeter:
                self.canvas.lower(line2)
                if connect_to_parallel:
                    self.canvas.lower(line3)

        if len(image_tags) == 2: #if 2 tags were received, the following will happen
            # obtains x and y coordinates of both widgets are obtained
            x1, y1 = self.canvas.coords(image_tags[0])
            x2, y2 = self.canvas.coords(image_tags[1])

            if connecting_voltmeter: #if the connection involves a voltmeter, only create one line between the two components.
                line1 = self.canvas.create_line(x1, y1, x2, y2, width=2)
                position_line()

            #if the connection is not between a battery and a component, draw 2 lines which are 90 degrees of each other
            elif not connect_to_parallel:
                if (x2 < x1 and y2 > y1) or (x1 < x2 and y1 > y2): #switches coordinates based on relative position
                    x1, x2 = x2, x1
                    y1, y2 = y2, y1
                #draw lines
                line1 = self.canvas.create_line(x1, y1, x2, y1, width=2)
                line2 = self.canvas.create_line(x2, y1, x2, y2, width=2)
                self.line_ids.extend([line1, line2]) #adds the two lines into a big list of line ids
                position_line()

            elif connect_to_parallel: #these are drawn if the user wants 3 lines to be drawn. This is required to prevent lines from going through parallel components
                # vertical
                #if the target component is below the source component
                if abs(x2 - x1) <= 100 and y1 < y2: #abs(x2 - x1) <= 100 means if the source component is within 100 pixels in the x axis
                    line1 = self.canvas.create_line(x1, y1, x1 + 50, y1, width=2)
                    line2 = self.canvas.create_line(x1 + 50, y1, x1 + 50, y2, width=2)
                    line3 = self.canvas.create_line(x1 + 50, y2, x2, y2, width=2)
                    self.line_ids.extend([line1, line2, line3]) #adds the three lines into a big list of line ids

                    #this is set to true if a line has already been made directly from the battery to a parallel component vertically
                    self.vertical_parallel = True
                    position_line()

                #if the target component is above the source component
                elif (abs(x2 - x1) <= 100 or self.vertical_parallel) and (y1 > y2): #abs(x2 - x1) <= 100 means if the source component is within 100 pixels in the x axis
                    # draw the lines
                    line1 = self.canvas.create_line(x1, y1, x1 - 50, y1, width=2)
                    line2 = self.canvas.create_line(x1 - 50, y1, x1 - 50, y2, width=2)
                    line3 = self.canvas.create_line(x1 - 50, y2, x2, y2, width=2)
                    self.line_ids.extend([line1, line2, line3]) #adds the three lines into a big list of line ids
                    position_line()

                #if the target component is on the right of the source component
                elif abs(x2 - x1) > 100 and abs(y2 - y1) <= 100 and x1 < x2: #abs(x2 - x1) <= 100 means if the source component is within 100 pixels in the x axis and vice versa
                    line1 = self.canvas.create_line(x1, y1, x1, y1 - 50, width=2)
                    line2 = self.canvas.create_line(x1, y1 - 50, x2, y1 - 50, width=2)
                    line3 = self.canvas.create_line(x2, y1 - 50, x2, y2, width=2)
                    self.line_ids.extend([line1, line2, line3]) #adds the three lines into a big list of line ids

                    #this is set to true if a line has already been made directly from the battery to a parallel component horizontal to prevent creation of strange lines
                    self.horizontal_parallel = True
                    position_line()

                # if the target component is on the left of the source component
                elif (abs(x2 - x1) > 100 and abs(y2 - y1)) <= 100 or (self.horizontal_parallel and x1 > x2): #abs(x2 - x1) <= 100 means if the source component is within 100 pixels in the x axis and vice versa
                    line1 = self.canvas.create_line(x1, y1, x1, y1 + 50, width=2)
                    line2 = self.canvas.create_line(x1, y1 + 50, x2, y1 + 50, width=2)
                    line3 = self.canvas.create_line(x2, y1 + 50, x2, y2, width=2)
                    self.line_ids.extend([line1, line2, line3]) #adds the three lines into a big list of line ids
                    position_line()
        print("line IDs",self.line_ids)

    #this method is important as we need it to drag the components around the canvas to position them
    def drag_component(self, event):
        # To drag the latest added component on the canvas
        try: #this try except is used as there will be an index error as some components have only 2 indices while others have 3
            #this takes the last added component as you can see by -1. All other components will be static.
            self.canvas.coords(self.component_array[-1][0], event.x - 15, event.y + 17.5)
            self.canvas.coords(self.component_array[-1][1], event.x, event.y)
            self.canvas.coords(self.component_array[-1][2], event.x + 20, event.y + 17.5)
        except:
            self.canvas.coords(self.component_array[-1][0], event.x, event.y)
            self.canvas.coords(self.component_array[-1][1], event.x + 20, event.y + 17.5)

    #method to clear canvas and reset all values
    def clear_canvas(self):
        self.canvas.delete("all")
        self.component_array.clear()
        self.id = 0
        self.switched_on = True
        self.switch_exists = False
        self.thermistor_exists = False
        self.varesistor_exists = False
        self.battery_exists = False
        self.component_limit = 5
        self.image_ID = 0
        WireGeneration.graphdic = {}

    #this method is a recursive function for line animation, only activated when Simulate button is pressed.
    #It is recursive as it uses an updated index everytime it calls itself.
    def animate_lines(self, index):

            if not self.simbutton_on:
                return

            #change color of current line to yellow
            self.canvas.itemconfig(self.line_ids[index], fill="#FDDA0D")

            #schedule next iteration of the animation with 20ms delay
            self.canvas.after(20, self.animate_lines, (index + 1) % len(self.line_ids))

            #reset color of current line to black if all lines have been animated with 20ms delay
            if index == len(self.line_ids) - 1:
                self.canvas.after(25, self.reset_lines)

    def reset_lines(self):
            #sets color of all lines to black
            for line_id in self.line_ids:
                self.canvas.itemconfig(line_id, fill="black")


    def run_circuit(self):
        self.simbutton_on = not self.simbutton_on #performs NOT operation on Simulate button
        lightbulbs = self.canvas.find_withtag('lightbulb') #gets all internal tkinter IDs with the 'lightbulb' tag

        # if this is false because there is no battery, an error message will show up
        if not self.battery_exists:
            messagebox.showerror("No power source detected!", "You need to add a battery to the circuit.")
            self.simbutton_on = False

        #if a battery exists, the button has been pressed, this condition will be met
        elif self.run_button["text"] == "Simulate!" and self.simbutton_on:
            self.run_button.place(x=16, y=420)
            self.run_button.config(text="Terminate!", bg="#00542a") #Alternates button
            if len(self.graph) <= 2: #If there are less than 2 keys in the graph dictionary, that means there will only be a line between 2 components which is not a circuit.
                messagebox.showerror("No end-to-end connection found.",
                                     "You must make a functional electrical circuit to simulate.")
            else:
                if self.switched_on and self.simbutton_on: #if the switch is on (on by default) and the simulate button has been pressed
                    # Start the animation with the first line
                    if not self.json_loaded:
                        self.total_components = len(self.component_array)
                        self.animate_lines(0) #animates the lines. 0 is passed to change the first line in line_ids to yellow
                    for lightbulb in lightbulbs: #if the switch is on, all lightbulbs will change into switched-on lightbulbs
                        self.canvas.itemconfig(lightbulb, image=self.lightbulbon_image, tags=(self.image_ID, self.id, 'lightbulb', self.lightbulbon_path))
                #creates an instance of the Simulate class the canvas, switch status, and total number of components as arguments
                self.sim_window = Simulate(self.canvas, self.graph, self.switched_on, self.total_components, self.voltmeters)



        else:
            #Once the button is pressed again, everything is turned back to their original states.
            self.run_button.config(text="Simulate!", bg="#420a06")
            self.run_button.place(x=16, y=420)
            self.simbutton_on = False
            self.reset_lines()
            for lightbulb in lightbulbs:
                self.canvas.itemconfig(lightbulb, image=self.lightbulboff_image)

            #to prevent errors, first the app checks if CircuitMaker has the attribute 'sim_window' and check if it exists, then closes it.
            if hasattr(self, 'sim_window') and self.sim_window.winfo_exists():
                self.sim_window.destroy()

    #method to save canvas into JSON
    def save_canvas(self):
        #stores number of components
        total_components = len(self.component_array)
        #passes all arguments required to make a circuit and calls the save_to_json method and dumps all JSON data into canvasdata.json
        canvas_to_json = JSONCanvas(self.canvas,self.line_ids, self.graph, self.battery_exists, self.varesistor_exists, self.switch_exists, self.thermistor_exists,total_components, self.voltmeters).save_to_json(self.username+"_canvasdata.json")

    #method to load canvas from JSON to the tkinter canvas
    def load_canvas(self):
        #these arguments in this case are just placeholders as they are unneded but are there to prevent any unnecessary argument errors. Load method is called.
        loaded_contents = JSONCanvas(self.canvas,self.line_ids, self.graph, self.battery_exists, self.varesistor_exists, self.switch_exists, self.thermistor_exists, self.total_components, self.voltmeters).load_from_json(self.username+"_canvasdata.json")

        #all returned values from called method are stored into these attribues
        self.line_ids = loaded_contents[0]

        #the keys for the graphs are returned as strings, so we iterate through all keys and induvidually turn them into integers
        self.graph = loaded_contents[1]
        self.graph = {int(key): value for key, value in self.graph.items()}

        #assigns rest of the variables
        self.battery_exists = loaded_contents[2]
        self.varesistor_exists = loaded_contents[3]
        self.switch_exists = loaded_contents[4]
        self.thermistor_exists = loaded_contents[5]
        self.total_components = loaded_contents[6]
        self.voltmeters = loaded_contents[7]
        self.json_loaded = True


    #method for loading premade circuits
    def load_presets(self):
        preset_window = Toplevel()
        preset_window.title("Presets")
        preset_window["bg"] = "#add8e6"

        preset_label = Label(preset_window, text="Choose a preset", bg="#add8e6", font=('Rockwell', 11, 'bold'))
        preset_label.pack()

        #displays different button for different circuit type for variety
        preset1_button = Button(preset_window, text="Preset 1 - Series", font=('Rockwell', 10, 'bold'), bg="#add8e6",
                                command=self.loadpreset1)
        preset1_button.pack()
        preset2_button = Button(preset_window, text="Preset 2 - Parallel", font=('Rockwell', 10, 'bold'), bg="#add8e6",
                                command=self.loadpreset2)
        preset2_button.pack()
        preset3_button = Button(preset_window, text="Preset 3 - Series-Parallel", font=('Rockwell', 10, 'bold'),
                                bg="#add8e6", command=self.loadpreset3)
        preset3_button.pack()


    #the three following methods follow the same principle as the load_canvas method, but they do not create any new json files
    def loadpreset1(self):
        loaded_contents = JSONCanvas(self.canvas, self.line_ids, self.graph, self.battery_exists,
                                     self.varesistor_exists, self.switch_exists, self.thermistor_exists,
                                     self.total_components, self.voltmeters).load_from_json(
            "preset/preset1.json")
        #all returned values from called method are stored into these attribues
        self.line_ids = loaded_contents[0]

        #the keys for the graphs are returned as strings, so we iterate through all keys and induvidually turn them into integers
        self.graph = loaded_contents[1]
        self.graph = {int(key): value for key, value in self.graph.items()}

        #assigns rest of the variables
        self.battery_exists = loaded_contents[2]
        self.varesistor_exists = loaded_contents[3]
        self.switch_exists = loaded_contents[4]
        self.thermistor_exists = loaded_contents[5]
        self.total_components = loaded_contents[6]
        self.voltmeters = loaded_contents[7]
        self.json_loaded = True

    def loadpreset2(self):
        self.battery_exists = True
        loaded_contents = JSONCanvas(self.canvas, self.line_ids, self.graph, self.battery_exists,
                                     self.varesistor_exists, self.switch_exists, self.thermistor_exists,
                                     self.total_components, self.voltmeters).load_from_json(
            "preset/preset2.json")
        #all returned values from called method are stored into these attribues
        self.line_ids = loaded_contents[0]

        #the keys for the graphs are returned as strings, so we iterate through all keys and induvidually turn them into integers
        self.graph = loaded_contents[1]
        self.graph = {int(key): value for key, value in self.graph.items()}

        #assigns rest of the variables
        self.battery_exists = loaded_contents[2]
        self.varesistor_exists = loaded_contents[3]
        self.switch_exists = loaded_contents[4]
        self.thermistor_exists = loaded_contents[5]
        self.total_components = loaded_contents[6]
        self.voltmeters = loaded_contents[7]
        self.json_loaded = True

    def loadpreset3(self):
        self.battery_exists = True
        loaded_contents = JSONCanvas(self.canvas, self.line_ids, self.graph, self.battery_exists,
                                     self.varesistor_exists, self.switch_exists, self.thermistor_exists,
                                     self.total_components, self.voltmeters).load_from_json(
            "preset/preset3.json")
        #all returned values from called method are stored into these attribues
        self.line_ids = loaded_contents[0]

        #the keys for the graphs are returned as strings, so we iterate through all keys and induvidually turn them into integers
        self.graph = loaded_contents[1]
        self.graph = {int(key): value for key, value in self.graph.items()}

        #assigns rest of the variables
        self.battery_exists = loaded_contents[2]
        self.varesistor_exists = loaded_contents[3]
        self.switch_exists = loaded_contents[4]
        self.thermistor_exists = loaded_contents[5]
        self.total_components = loaded_contents[6]
        self.voltmeters = loaded_contents[7]
        self.json_loaded = True

#WireGeneration class purpose: This class is required to connect two components together with wires.
#It is also needed to store the connections of the components in the graph abstract data type.
#Voltmeters are not stored in the graph dictionary as they're always connected to components in parallel and current is assumed to not pass through them as they have infinitely large resistance.
class WireGeneration(Toplevel):
    graphdic = {}
    voltmeters = []
    def __init__(self, canvas):
        super().__init__()
        #calls superclass constructor

        #intialises instance
        self.canvas = canvas
        self.IDpair = []

        #flag to determine if the connection involves a voltmeter so that it can avoid adding the connection to the dictionary
        self.voltmeterflag = False

        #prevents resizing window
        self.resizable(False, False)
        self.title("A= Source ║ B= Target")

        #sets background
        self.tag_bg = ImageTk.PhotoImage(Image.open("wallpaper/mainbackground.jpg"))
        background_label = Label(self, image=self.tag_bg)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #sets window dimensions
        self.geometry(str(250) + "x" + str(127))

        self.title_text = Label(self, text="Insert component IDs of A & B", font=("Cambria", 11, 'bold'),
                                fg="#09221e", bg='#90bcad')
        self.title_text.place(x=20, y=2)

        #creates a label and entry for the first image tag
        self.tagrequest1 = Label(self, text="Component tag A: ", font=("Cambria", 11), fg="#09221e",
                                 bg='#90bcad')
        self.tagrequest1.place(x=50, y=22)

        self.tagentry1 = Entry(self, width=2, font=("Cambria", 9, 'bold'))
        self.tagentry1.place(x=170, y=24)

        #creates a label and entry for the second image tag
        self.tagrequest2 = Label(self, text="Component tag B: ", font=("Cambria", 11), fg="#09221e",
                                 bg='#90bcad')
        self.tagrequest2.place(x=50, y=42)

        self.tagentry2 = Entry(self, width=2, font=("Cambria", 9, 'bold'))
        self.tagentry2.place(x=170, y=44)

        #boolean variable changed based on whether checkbox is ticked or unticked.
        #This checkbox is only ticked if the connection is between the battery to parallel component directly or vice versa
        #The reason this is here is to prevent component and wire visual collision.
        self.checkbox_var = BooleanVar(value=False)
        self.checkbox = Checkbutton(self, text="Connect battery to parallel directly", font=('Rockwell', 9, 'bold'), fg="#09221e", bg='#b7c9b1', variable=self.checkbox_var, relief="raised")
        self.checkbox.place(x=10, y=67)

        #pressing button activated tag_validation method
        button = Button(self, text="Connect Wire", font=('Rockwell', 10, 'bold'), fg='white', bg='#0f1c14',
                        command=self.tag_validation)
        button.place(x=75, y=95)

    #method to get the checkbox state as a boolean value
    def checkbox_input(self):
        result = self.checkbox_var.get()
        return result #returns value to caller

    #this method is important for adding the connections to the dictionary or finding out if the connection involves a voltmeter
    def tag_validation(self):
        #gets all voltmeter components in the canvas
        get_voltmeters = self.canvas.find_withtag('voltmeter')
        #try-except used to prevent user from entering non-numeric characters
        try:
            image_tag1 = int(self.tagentry1.get())
            image_tag2 = int(self.tagentry2.get())

            tag1_isvalid = self.canvas.find_withtag("ID" + str(image_tag1))[0]
            tag2_isvalid = self.canvas.find_withtag("ID" + str(image_tag2))[0]

        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid tag entered. Re-enter tag.")
            return #returns to caller and prevents further execution of method

        #if the entered tags are positive and are not the same as each other, the following will be executed
        if image_tag1 > 0 and image_tag2 > 0 and image_tag1 != image_tag2:
            #a list of pairs is crated
            self.IDpair = [tag1_isvalid, tag2_isvalid]

            #if either of the components are a voltmeter, the pair will also be added to voltmeters list for later calculations
            if tag1_isvalid in get_voltmeters:
                self.voltmeters.append([image_tag1,image_tag2])
                self.voltmeterflag = True #sets flag to true
            elif tag2_isvalid in get_voltmeters:
                self.IDpair = [tag2_isvalid,tag1_isvalid]
                self.voltmeters.append([image_tag2,image_tag1])
                self.voltmeterflag = True #sets flag to true
            else:
                #adds the tags to the graph. As the graph is undirected, the source will be a key and the target will be a key.
                #e.g. if A was the source and B was the target, in the dictionary, A: B and B: A will be created
                if image_tag1 in self.graphdic:
                    if image_tag2 not in self.graphdic[image_tag1]:
                        self.graphdic[image_tag1] += [image_tag2]
                else:
                    self.graphdic[image_tag1] = [image_tag2]

                if image_tag2 in self.graphdic:
                    if image_tag1 not in self.graphdic[image_tag2]:
                        self.graphdic[image_tag2] += [image_tag1]
                else:
                    self.graphdic[image_tag2] = [image_tag1]



            #this part is executed if the checkbox is checked.
            #parallel connections directly with the connection on a graph will only have one edge between them.
            #I have used "x" as a placeholder to pass circuit functionality checks as nodes with only one degree are expected to be dead-end-nodes
            if self.checkbox_input():
                #add 'x' to the values of each key in graphdic
                for key in self.graphdic:
                    if len(self.graphdic[key]) < 2:
                        self.graphdic[key].append('x')
            print(self.graphdic)
        else:
            #display error if error encountered
            messagebox.showerror("Error", "Invalid tag entered. Re-enter tag.")
            return #return back to caller
        self.destroy() #close window

#Simulate class purpose: This class holds most of the backend of the app. It processes all calculations based on the graph dictionary.
#It is compatible with different types of circuits: series, parallel and series-parallel circuits.
#It inherits from TopLevel similar to the other classes
class Simulate(Toplevel):
    def __init__(self, canvas, graph, switched_on, total_components, voltmeters):
        super().__init__() #calling superclass constructor
        self.resizable(False,False)

        #stores instances of passed arguments
        self.canvas = canvas
        self.switched_on = switched_on
        self.total_components = total_components
        print(self.total_components)

        #sets background
        self.wallpaper = ImageTk.PhotoImage(Image.open("wallpaper/mainbackground.jpg"))
        background_label = Label(self, image=self.wallpaper)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.title("Simulation Results")

        #stores the graph that has 'x' placeholders in graph_old
        self.graph_old = graph
        #stores instance of WireGeneration's voltmeter attribute
        self.voltmeters = voltmeters

        #initializing attributes
        self.graph = {}
        self.circuit_type=""
        self.A_in_series = []
        self.R_in_series = []
        self.S_in_series = []
        self.L_in_series = []
        self.dead_end_nodes = []
        self.total_voltage = 0
        self.total_resistance = 0
        self.total_current = 0
        #removes the 'x' placeholders so that the graph can be passed properly through the DFS algorithm
        for key, values in self.graph_old.items():
            without_x = [value for value in values if value != "x"]
            if without_x:
                self.graph[key] = without_x

        #the graph dictionary is passed as an argument into get_cycles() method which gets the cycles from the DFS method
        self.cycles = self.get_cycles(self.graph)

        print("Simulation Result:")
        print("Graph:",self.graph)
        print("Cycles:",self.cycles)

        #the circuit_composition() result is called and stored in circuit_type to then be displayed and used to perform calculations quicker using selection statements
        self.circuit_type = self.circuit_composition()

        title_label = Label(self, text="Circuit Calculations", font=('Rockwell', 18, 'bold'), fg='white', bg='#1A2421', relief = "raised",
                      borderwidth=4)
        title_label.pack(pady=10)

        #all ammeters and voltmeters are displayed along with their component IDs and the values they measure
        self.display_meters()

        #labels which display the key attributes of the circuit made by the user
        circuit_type_label = Label(self, text="Circuit Type: " + self.circuit_composition(), font=('Rockwell', 15), fg='white', bg='#1C352D', relief = "raised",
                      borderwidth=4)
        circuit_type_label.pack(pady=5)

        #self.total_components is passed as an argument and used directly here
        total_components_label = Label(self, text="No. of components: " + str(self.total_components), font=('Rockwell', 15), fg='white', bg='#00755E', relief = "raised",
                      borderwidth=4)
        total_components_label.pack(pady=5)

        #the resistance in series is called and stored here. If the circuit is series, this will remain the same, otherwise it will be updated soon
        resistance_label = Label(self, text="Total resistance (R): " + str(self.series_resistance()) + "Ω", font=('Rockwell', 15), fg='white', bg='#004B49', relief = "raised",
                      borderwidth=4)
        resistance_label.pack(pady=5)

        #displays potential difference from battery which is called and stored here.
        pd_label = Label(self, text="Potential Difference (V): " + str(self.series_voltage())+"V", font=('Rockwell', 15), fg='white', bg='#3B7A57', relief = "raised",
                      borderwidth=4)
        pd_label.pack(pady=5)

        #displays overall current in label
        current_label = Label(self, text="Total current (I): " + str(self.total_current)+"A", font=('Rockwell', 15), fg='white', bg='#00755E', relief = "raised",
                      borderwidth=4)
        current_label.pack(pady=5)

        #updates resistance if not series
        if len(self.cycles) > 1:
            resistance_label.config(text="Total resistance: " + str(self.total_resistance) + "Ω" )

    #this method returns the battery of the circuit and its voltage
    def get_volts(self):
        battery_volts = []
        # this method gets all components with the tag 'battery'
        battery_widgets = self.canvas.find_withtag("battery")

        #extracts the battery ID and its potential difference from battery_widgets
        for widget in battery_widgets:
            widget_tags = self.canvas.itemcget(widget, "tags")
            widget_tags_list = widget_tags.split(" ")
            #slices component id
            widget_id = widget_tags_list[0]
            #slices voltage value
            voltage = widget_tags_list[1]
            battery_volts.append([widget_id, voltage])
        return battery_volts

    #this method returns the battery of the circuit and its voltage
    def get_ohms(self):
        resistor_ohms = []
        #gets all widgets of the canvas and removes the uneeded one using process of elimination with selective statements
        for widget in self.canvas.find_all():
            tags = self.canvas.gettags(widget)
            #extracts the resistor/thermistor/variable resistor ID and its resistance
            if "resistor" in tags or "varesistor" in tags or "thermistor" in tags:
                #slices component id
                widget_id = tags[0]
                #slices ohm value
                widget_ohms = float(tags[1])
                resistor_ohms.append([int(widget_id), int(round(widget_ohms))])
        return resistor_ohms

    def series_voltage(self):
        # if there is a node that is not connected to the full circuit, this would return 0 and stop further execution of the method
        if self.dead_end_nodes or not self.switched_on:
            return 0
        voltages = self.get_volts()  #gets voltage values
        total_voltage = 0
        for volt in voltages:
            total_voltage += float(volt[1]) #gets the overall potential difference of the circuit
        return total_voltage

    def series_resistance(self):
        if self.dead_end_nodes or not self.switched_on:
            return 0
        resistances = self.get_ohms()  #get resistance values
        total_resistance = 0
        for res in resistances:
            #res[1] slices the reisistance
            total_resistance += float(res[1]) #adds up total resistance in a
        return total_resistance

    #this method determines the circuit_type of the simulated circuit
    def circuit_composition(self):
        #find number of cycles
        num_cycles = len(self.cycles)

        #stores all components in series. This is only required to see if at least one series component exists.
        in_series = self.get_series_components()
        if num_cycles == 1:
            #circuit has only one cycle, so it's a series circuit
            circuit_type = "Series"

        elif (num_cycles > 1) and in_series:
            #circuit has multiple cycles and there are components in series, so it's a series-parallel circuit
            circuit_type = "Series-Parallel"
        else:
            #circuit has multiple cycles but no component in series, so it's a parallel circuit
            circuit_type = "Parallel"

            #this checks for dead-end branches
            for node in self.graph_old.keys():
                #this checks if the key only has one neighbour and if it is not already appended
                if len(self.graph_old[node]) == 1 and node not in self.dead_end_nodes:
                    #as there is only neighbour, we can just index 0.
                    neighbor = self.graph[node][0]
                    #checks if the neighbour is part of a cycle
                    if neighbor in self.cycles:
                        #nighbor is part of a cycle, so node is not a dead end
                        continue
                    #appends to dead_end_nodes
                    self.dead_end_nodes.append(node)

            if self.dead_end_nodes: #this results in every voltage, current, and resistance value be returned as 0
                circuit_type = "Disconnected component detected."

        return circuit_type #returns the circuit_type to the caller

    #this is a general method to retrieve the IDs of a component
    def get_componentID(self, component):
        widget = self.canvas.find_withtag(component)
        tags = self.canvas.itemcget(widget, "tags")
        widget_tags_list = tags.split(" ")
        #slices the ID values
        id_values = widget_tags_list[0]
        return id_values

    #this method gets all components in series and stores them in a 1D list
    def get_series_components(self):
        in_series=[]
        #using methods to get all IDs
        resistor_ids = self.get_ohms()
        ammeter_ids = self.get_componentID("ammeter")
        switch_id = self.get_componentID("switch")
        lightbulb_ids = self.get_componentID("lightbulb")

        #this nested function is made to make this more efficient otherwise a lot of code will be repeated
        def find_series_components(IDlist, series_list): #the list of IDs and the list to store in are the parameters respectfully
            added_ids = []
            for ID in IDlist:
                in_all_cycles = True #initially set to true
                for cycle in self.cycles:
                    if ID[0] not in cycle: #the idea here is that if the componenet ID is in every cycle, that means it is in series
                        in_all_cycles = False #if they are not in every cyclel, they are not in series
                        break
                # prevents already added IDs to be readded
                if in_all_cycles and ID not in added_ids:
                    series_list.append(ID) #appends the components in series to the passed list
                    added_ids.append(ID) #appens component ID into added_ids list

        #executing nested function for different components
        find_series_components(ammeter_ids, self.A_in_series)
        find_series_components(resistor_ids, self.R_in_series)
        find_series_components(switch_id, self.S_in_series)
        find_series_components(lightbulb_ids, self.L_in_series)

        if len(self.A_in_series) > 1: #prevents user from using same ammeter in series twice as it produces same results and is unnecessary
            messagebox.showwarning("Terminated", "Only 1 ammeter needed in series as all ammeters in series show same display.")
            self.destroy() #closes window

        #extend is used to keep list 1-dimensional
        in_series.extend(self.A_in_series)
        in_series.extend(self.R_in_series)
        in_series.extend(self.S_in_series)
        in_series.extend(self.L_in_series)
        return in_series #returns final list to caller

    #this method is important to get every parallel_branches will be needed for parallel/series-parallel calculations
    def get_parallel_branches(self):
        parallel_branches = []
        if len(self.cycles) > 1:
            #makes an independent copy of self.cycles
            parallel_branches = [cycle[:] for cycle in self.cycles]

            #removes largest cycle as it is not useful in calculation
            largest_branch = parallel_branches.index(max(parallel_branches, key=len))
            parallel_branches.pop(largest_branch)

            #turns the first index into set to use for comparison
            common_items = set(parallel_branches[0])

            #set for unique IDs
            unique_items = set()

            #cycles through the branches in the list of parallel branches.
            for i in range(1, len(parallel_branches)):
                #this performs the operation (common_items ∩ parallel_branches[i]) in order to retrieve all common IDs
                common_items = common_items.intersection(set(parallel_branches[i]))

            #for the range of how many branches the list 'parallel_branches' is remade but without the common_items.
            #the remaining nodes are then added onto the 'unique_items' set
            for i in range(len(parallel_branches)):
                parallel_branches[i] = [ID for ID in parallel_branches[i] if ID not in common_items]

                parallel_branches[i] = [ID for ID in parallel_branches[i] if
                                        ID not in unique_items and not unique_items.add(ID)]

            #this removes all empty branches from the list as you can see by 'len(branch) > 0'
            parallel_branches = [branch for branch in parallel_branches if len(branch) > 0]

        return parallel_branches #returns the parallel_branches list to the caller

    #this is the one of the key methods of the Simulate class. It displays both ammeters and voltmeters present in the circuit.
    #It also calculates the total current and total resistance of the circuit in series, parallel and series-parallel cases.
    def display_meters(self):
        #gets the IDs using the get_componentID method
        ammeter_ids = self.get_componentID("ammeter")
        voltmeter_ids = self.get_componentID("voltmeter")
        resistor_ids = self.get_ohms()

        #gets all parallel branches using get_parallel_branches method
        parallel_branches = self.get_parallel_branches()

        #voltage in series and resistance in series is assigned to V and R by default
        V = self.series_voltage()
        R = self.series_resistance()

        if not self.switched_on:
            #if the switch of the circuit if present is switched off, all values will be presented as 0
            for ID in ammeter_ids:
                ammeter_label = Label(self, text="Ammeter " + str(ID[0]) + ": 0A", font=('Rockwell', 12),
                                      fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                ammeter_label.pack(pady=5)

            for ID in voltmeter_ids:
                voltmeter_label = Label(self, text="Voltmeter " + str(ID) + ": 0V",
                                      font=('Rockwell', 12),
                                      fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                voltmeter_label.pack(pady=5)


        elif self.circuit_type == "Series":
            self.total_current = round((V / R),2) #uses Ohm's law to calculate the total current of the circuit, then rounds it to 2dp
            #displays all ammeters along with the total current
            for ID in ammeter_ids:
                ammeter_label = Label(self, text="Ammeter " + str(ID[0]) + ": " + str(self.total_current) + "A", font=('Rockwell', 12),
                                      fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                ammeter_label.pack(pady=5)

            for ID in voltmeter_ids:
                if self.circuit_type == "Series":
                    #voltage is split across every component in circuits, we would have to divide the total potential difference by number of components
                    #we do not count the voltmeters and battery when counting number of components for this, so we subtract the total components by (len(voltmeter_ids)+1)
                    voltmeter_value = round((self.series_voltage() / (self.total_components - (len(voltmeter_ids)+1))), 2)

                    #displays the values with the voltmeter_value
                    voltmeter_label = Label(self, text="Voltmeter " + str(ID) + ": " + str(voltmeter_value) + "V",
                                          font=('Rockwell', 12),
                                          fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                    voltmeter_label.pack(pady=5)

        #if the circuit is parallel or series-parallel and has no dead-end-nodes
        elif len(self.cycles) > 1 and not self.dead_end_nodes:
            R_in_parallel = [] #initalising list

            #iterates through every resistor ID and parallel branch to see if the resistor is a parallel component
            for resistor in resistor_ids:
                for branch in parallel_branches:
                    if (resistor[0] in branch) and (resistor not in R_in_parallel):
                        #appends the resistor to a list if it is a parallel component
                            R_in_parallel.append(resistor)

            #initialising lists
            I_branches = []
            R_branches = []
            #finding total resistance
            #try except used to report zero-error as an ammeter has negligible resistance and if it is alone in a parallel branch, there will be a zero error.
            #key equation used here to calculate resistance in parallel: 1/Rₜₒₜₐₗ = 1/R₁ + 1/R₂ + 1/R₃
            try:
                #iterates a parallel branch at a time and every resistor in that branch
                for branch in parallel_branches:
                    R_branch = 0
                    for resistor in R_in_parallel:
                        if resistor[0] in branch:
                            R_branch += resistor[1] #total resistance in the branch
                    if R_branch > 0:
                        self.total_resistance += 1 / R_branch #reciprocal of the resistance of that branch is added to the total_resistance
                        I_branches.append(round((V / R_branch),2)) #the current of the branch is found using V/R
                    R_branches.append(R_branch) #The total resistance within the branch is appended to the 1D list R_branches

                #this will be reached once the iteration has cycled through every parallel branch and have added up every resistor in each branch.
                #the final total resistance of the parallel circuit would be the reciprocal of the total
                self.total_resistance = 1 / self.total_resistance

                #if the circuit is series-parallel, we can use R_in_series to find resistors in series
                for resistor in self.R_in_series:
                    #the resistance of the resistor can be sliced and added onto the total resistance
                    self.total_resistance += resistor[1]

                #the total resistance is rounded to 2dp
                self.total_resistance = round(self.total_resistance, 2)

                print("final total resistance:",self.total_resistance)
            except:
                self.destroy()
                messagebox.showerror("Undefined error", "Cannot divide potential difference by 0. You must include any resistor in series with the component: Aₚ = Vₜₒₜₐₗ / Rₚ")

            #total current
            #from the iteration when finding resistance, we have made the array of I_branches which is the current of every parallel branch
            #using Kirchoff's current law, we can find the overall current of the circuit with the equation Iₜₒₜₐₗ = I₁ + I₂ + I₃ where Iₙ is the current of a parallel branch
            self.total_current = sum(I_branches)
            #zip is used to pair the ID from ammeter_ids with the corresponding current from I_branches
            for ID, current in zip(ammeter_ids, I_branches):
                #if in series, it will just display the total current
                if ID in self.A_in_series:
                    ammeter_label = Label(self, text="Ammeter " + str(ID[0]) + ": " + str(self.total_current) + "A",
                                          font=('Rockwell', 12),
                                          fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                    ammeter_label.pack(pady=5)
                else:
                    #The 'current' variable from I_branches would be displayed instead
                    ammeter_label = Label(self, text="Ammeter " + str(ID[0]) + ": " + str(current) + "A",
                                          font=('Rockwell', 12),
                                          fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                    ammeter_label.pack(pady=5)

            #displaying voltmeters
            #here we get the total number of components that are in series
            in_series = self.get_series_components()
            in_series_count = len(in_series)
            try:
                #voltmeter_split is used to divide the overall potential difference by the number of components in series.
                voltmeter_split = round((self.series_voltage() / (in_series_count)),2)
            except:
                #if the circuit is in parallel, in_series_count would be 0, so voltmeter_split would instead just be equal to the potential difference
                voltmeter_split = self.series_voltage()
            print("Resistors in parallel:", R_in_parallel)
            print("Parallel branches:", parallel_branches)
            print("ID of voltmeter and component pair:",self.voltmeters)
            print("IDs of components in series:",self.get_series_components())

            #this iterates through each branch induvidually to check if a resistor from R_in_Parallel is in that branch.
            for branch in parallel_branches:
                for resistor in R_in_parallel:
                    if resistor[0] in branch:
                        #if the resistor is in the branch, it then iterates through every voltmeter that exists in the voltmeters ID (which stored voltmeter-resistor pairs)
                        for voltmeter in self.voltmeters:
                            if voltmeter[1] == resistor[0]: #if any of the voltmeters during iteration match the said resistor, the following will happen
                                branch_num = parallel_branches.index(branch) #the index of the branch in the current iteration stage is stored in branch_num

                                # branch_num is used to slice the resistance value of the branch in R_branches
                                voltmeter_value = (voltmeter_split / R_branches[branch_num]) * resistor[1]

                                #value displayed in label
                                voltmeter_label = Label(self, text="Voltmeter " + str(voltmeter[0]) + ": " + str(voltmeter_value) + "V",
                                                        font=('Rockwell', 12),
                                                        fg='white', bg='#8A9A5B', relief="raised", borderwidth=4)
                                voltmeter_label.pack(pady=5)

    #this method is important as it is used to determine every calculation.
    #it is the depth-first search algorithm, implemented to return every cycle of a graph
    #several filters are also put in place to remove some unwanted cycles
    def dfs(self, node, graph, visited, stack, cycles):
        #this has 5 parameters:
        #node is the current node being visited
        #graph is the graph which it will be used on,
        #visited is a dictionary which has nodes as keys and boolean expressions as values to keep track of visited nodes
        #stack is used to keep track of all paths that have been taken, and will be used to backtrack if there are no more neighbours for a node
        #cycles stores every cycle found ni the graph

        #initially sets current node as visited
        visited[node] = True

        #adds current node to stack
        stack.append(node)

        #visits every neighbour of the node
        for neighbor in graph[node]:
            #if it has not been visited yet
            if not visited[neighbor]:
                #recursively call the depth-first search algorithm again. This will then mark that node as visited and go through its own neighbours.
                self.dfs(neighbor, graph, visited, stack, cycles)
            #if the neighbour is at the first index of the stack, that means there is a cycle, we have gone back to the start where the cycle started.
            #The length of the stack must be at least 2 otherwise it would not count as a cycle
            elif neighbor == stack[0] and len(stack) > 2:

                #this creates a new independent cycle
                cycle = sorted(stack[:-1] + [node])
                if cycle not in cycles:
                    #if it does not exist in the cycles list, it will be appended
                    cycles.append(cycle)

        #This is to allow parallel circuit graphs to count as a cycle despite often only having edge between nodes
        if len(graph[node]) == 1 and len(stack) > 1:
            #node is a leaf node, but treat it as if it were part of a cycle
            cycle = sorted(stack)
            if cycle not in cycles:
                cycles.append(cycle)

        #this removes the current node from the stack then it marks the current node as unvisited
        stack.pop()
        visited[node] = False

    def get_cycles(self, graph):
        #this creates a dictionary which initalises all nodes as unvisted (False)
        visited = {node: False for node in graph}

        #this keeps a list where all cycles will be appended
        cycles = []

        #this will apply the DFS algorithm on all unvisited nodes and will retrieve all cycles
        for node in graph:
            if not visited[node]:
                self.dfs(node, graph, visited, [], cycles) #takes the empty cycles list as parameter
        return cycles #returns the cycles list to caller


# Generates main window and uses loginpage class
main = Tk() #this is the tkinter class, used to create a root window
main.resizable(False, False) #prevents resizing
page1 = Authentication(main) #creates instance of Authentication class while main is the root window
main.mainloop() #starts main event loop of root window
