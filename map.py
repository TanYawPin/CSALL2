import tkinter as tk
import requests
from io import BytesIO
from PIL import Image, ImageTk

class Map(tk.Toplevel):
    def __init__(self, root, username, is_admin=False):
        self.root = root
        self.root.title("Tourism App")

        self.username = username
        self.is_admin = is_admin

        self.google_maps_api_key = 'AIzaSyDTs23Vzaf-kZJSRJJLa86wpfCn4ccz-OY'

        # Create a frame for the sidebar
        self.sidebar_frame = tk.Frame(self.root, width=200, bg='lightgray')
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create buttons for sidebar choices
        self.location_button = tk.Button(self.sidebar_frame, text="Locations", command=self.show_locations)
        self.location_button.pack(pady=10)

        self.food_button = tk.Button(self.sidebar_frame, text="Food", command=self.show_food)
        self.food_button.pack(pady=10)

        self.transport_button = tk.Button(self.sidebar_frame, text="Transport", command=self.show_transport)
        self.transport_button.pack(pady=10)

        self.map_button = tk.Button(self.sidebar_frame, text="Map", command=self.show_map)
        self.map_button.pack(pady=10)

        self.sign_out_button = tk.Button(self.root, text="Sign Out", command=self.sign_out)
        self.sign_out_button.pack()

        self.show_map()

    def show_locations(self):
        # Clear current display
        self.clear_display()

        self.sign_out_button.pack_forget()

        from homepage import HomePage
        homepage = HomePage(self.root, self.username, self.is_admin)
        homepage.grab_set()
        self.root.wait_window(homepage)

    def show_food(self):
        # Clear current display
        self.clear_display()

        self.sign_out_button.pack_forget()

        # Open the FoodPage when the "Food" button is pressed
        from foodpage import FoodPage
        foodpage = FoodPage(self.root, self.username, self.is_admin)
        foodpage.grab_set()  # Make the homepage modal if needed
        self.root.wait_window(foodpage)

    def show_transport(self):
        # Clear current display
        self.clear_display()

        self.sign_out_button.pack_forget()

        from transportpage import TransportPage
        transportpage = TransportPage(self.root, self.username, self.is_admin)
        transportpage.grab_set()
        self.root.wait_window(transportpage)

    def show_map(self):
        self.clear_display()

        self.label_welcome = tk.Label(self.root, text=f"Welcome, {self.username}")
        self.label_welcome.pack(pady=10)

        # Get the static map image using Google Static Maps API
        static_map_url = self.get_static_map_url()
        image = self.get_static_map_image(static_map_url)

        # Display the static map image
        map_label = tk.Label(self.root, image=image) 
        map_label.image = image  # Keep a reference to the image to prevent it from being garbage collected
        map_label.pack()

        # Make the map window modal if needed
        self.grab_set()
        self.wait_window()

    def get_static_map_url(self):
        # Set the center location to Penang Island, Malaysia
        center_location = '5.4164,100.3327'
        zoom_level = 10
        map_size = '600x400'

        # Construct the static map URL
        static_map_url = f'https://maps.googleapis.com/maps/api/staticmap?center={center_location}&zoom={zoom_level}&size={map_size}&key={self.google_maps_api_key}'

        return static_map_url

    def get_static_map_image(self, static_map_url):
        try:
            # Download the static map image
            response = requests.get(static_map_url)
            response.raise_for_status()  # Raise an error for bad responses

            # Open the image using PIL
            image = Image.open(BytesIO(response.content))

            # Convert the image to Tkinter PhotoImage format
            tk_image = ImageTk.PhotoImage(image)

            return tk_image
        except Exception as e:
            print(f"Error loading static map image: {e}")
            return None

    def clear_display(self):
        for widget in self.root.winfo_children():
            if widget != self.sidebar_frame and not isinstance(widget, tk.Button):
                widget.destroy()

    def sign_out(self):
        # Close the current window
        self.root.destroy()

        # Open the login/register page
        from login_register import TourismSystem
        root = tk.Tk()
        app = TourismSystem(root)
        root.mainloop()