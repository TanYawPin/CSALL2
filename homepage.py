import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from PIL import Image, ImageTk
from functools import partial

class HomePage(tk.Toplevel):
    def __init__(self, root, username, is_admin=False):
        self.root = root
        self.root.title("Tourism App")

        # Initialize database
        self.conn = sqlite3.connect('tourism_locations.db')
        self.create_location_table()

        self.username = username
        self.is_admin = is_admin

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

        # Admin CRUD buttons (only visible to admin)
        if self.is_admin:
            self.add_location_button = tk.Button(self.root, text="Add Location", command=self.add_location)
            self.add_location_button.pack(pady=10)

            self.edit_location_button = tk.Button(self.root, text="Edit Location", command=self.edit_location)
            self.edit_location_button.pack(pady=5)

            self.delete_location_button = tk.Button(self.root, text="Delete Location", command=self.delete_location)
            self.delete_location_button.pack(pady=5)

        self.sign_out_button = tk.Button(self.root, text="Sign Out", command=self.sign_out)
        self.sign_out_button.pack()

        # Default page is 'Locations'
        self.show_locations()

    def create_location_table(self):
        # Create location table if not exists
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    image TEXT,
                    description TEXT,
                    price TEXT
                )
            ''')

    def show_locations(self):
        # Clear current display
        self.clear_display()

        self.label_welcome = tk.Label(self.root, text=f"Welcome, {self.username}")
        self.label_welcome.pack(pady=10)

        # Add search bar and button
        self.add_search_bar()

        # Display locations
        self.display_locations()


    def show_food(self):
        # Clear current display
        self.clear_display()
        if self.is_admin:
            if hasattr(self, 'add_location_button'):
                self.add_location_button.pack_forget()
            if hasattr(self, 'edit_location_button'):
                self.edit_location_button.pack_forget()
            if hasattr(self, 'delete_location_button'):
                self.delete_location_button.pack_forget()
        self.sign_out_button.pack_forget()


        # Open the FoodPage when the "Food" button is pressed
        from foodpage import FoodPage
        foodpage = FoodPage(self.root, self.username, self.is_admin)
        foodpage.grab_set()  # Make the homepage modal if needed
        self.root.wait_window(foodpage)

    def show_transport(self):
        # Clear current display
        self.clear_display()
        if self.is_admin:
            if hasattr(self, 'add_location_button'):
                self.add_location_button.pack_forget()
            if hasattr(self, 'edit_location_button'):
                self.edit_location_button.pack_forget()
            if hasattr(self, 'delete_location_button'):
                self.delete_location_button.pack_forget()
        self.sign_out_button.pack_forget()

        from transportpage import TransportPage
        transportpage = TransportPage(self.root, self.username, self.is_admin)
        transportpage.grab_set() 
        self.root.wait_window(transportpage)

    def show_map(self):
        self.clear_display()

        if self.is_admin:
            if hasattr(self, 'add_location_button'):
                self.add_location_button.pack_forget()
            if hasattr(self, 'edit_location_button'):
                self.edit_location_button.pack_forget()
            if hasattr(self, 'delete_location_button'):
                self.delete_location_button.pack_forget()
        self.sign_out_button.pack_forget()

        from map import Map
        mappage = Map(self.root, self.username, self.is_admin)
        mappage.grab_set()
        self.root.wait_window(mappage)

    def search_locations(self, search_term):
        # Clear current display
        self.clear_display()

        self.label_welcome = tk.Label(self.root, text=f"Welcome, {self.username}")
        self.label_welcome.pack(pady=10)

        self.add_search_bar()
        
        # Display locations based on the search term
        self.display_locations(search_term)

    def add_search_bar(self):
        # Create entry widget for search term
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack(pady=5)

        # Create search button
        self.search_button = tk.Button(
            self.root, text="Search", command=lambda: self.search_locations(self.search_entry.get())
        )
        self.search_button.pack(pady=5)

    def remove_search_bar(self):
        # Check if search elements exist and destroy them
        if hasattr(self, 'search_entry'):
            self.search_entry.destroy()
            del self.search_entry
        if hasattr(self, 'search_button'):
            self.search_button.destroy()
            del self.search_button

    def display_locations(self, search_term=None):
        # Fetch locations from the database and display them
        with self.conn:
            cursor = self.conn.cursor()
            if search_term:
                # Use LIKE to find names that contain the search term
                cursor.execute("SELECT * FROM locations WHERE name LIKE ?", ('%' + search_term + '%',))
            else:
                cursor.execute("SELECT * FROM locations")
            locations = cursor.fetchall()

        num_columns = 2

        # Create a frame to hold the grid
        grid_frame = tk.Frame(self.root)
        grid_frame.pack()

        # Create a canvas to contain the frame with items
        canvas = tk.Canvas(grid_frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollbar for the canvas
        scrollbar = tk.Scrollbar(grid_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to hold the items
        items_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=items_frame, anchor="nw")

        # Iterate over locations and display them in a grid
        for i, location in enumerate(locations):
            # Load image
            image_path = location[2]  # Assuming image path is stored in the third column
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Adjust the size as needed
            img = ImageTk.PhotoImage(img)

            # Create a frame for each transport's information 
            location_frame = tk.Frame(items_frame)
            location_frame.grid(row=i // num_columns, column=i % num_columns, padx=10, pady=10)


            # Display image 
            image_label = tk.Label(location_frame, image=img)
            image_label.image = img
            image_label.grid(row=0, column=0, pady=5)

            # Display name, description, and price below the image
            name_label = tk.Label(location_frame, text=f"Name: {location[1]}", anchor="w")
            name_label.grid(row=1, column=0, pady=2, sticky="w")

            description_label = tk.Label(location_frame, text=f"Description: {location[3]}", anchor="w")
            description_label.grid(row=2, column=0, pady=2, sticky="w")

            price_label = tk.Label(location_frame, text=f"Price: {location[4]}", anchor="w")
            price_label.grid(row=3, column=0, pady=2, sticky="w")

        # Set up canvas scrolling region 
        items_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # If the number of locations is not a multiple of num_columns, add empty labels to fill the row
        remaining_cells = (num_columns - (len(locations) % num_columns)) % num_columns
        for _ in range(remaining_cells):
            empty_label = tk.Label(grid_frame, text="")
            empty_label.grid(row=len(locations) // num_columns, column=(len(locations) % num_columns) + _, padx=10, pady=10)



    def add_location(self):
        # Create a Toplevel window for the input fields
        add_location_window = tk.Toplevel(self.root)
        add_location_window.title("Add Location")

        # Entry fields for name, image URL, description, and price
        name_label = tk.Label(add_location_window, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(add_location_window)
        name_entry.pack()

        image_label = tk.Label(add_location_window, text="Image URL:")
        image_label.pack()
        image_entry = tk.Entry(add_location_window)
        image_entry.pack()

        description_label = tk.Label(add_location_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(add_location_window)
        description_entry.pack()

        price_label = tk.Label(add_location_window, text="Price:")
        price_label.pack()
        price_entry = tk.Entry(add_location_window)
        price_entry.pack()

        # Function to handle the OK button click
        def on_ok():
            # Get values from the entry fields
            name = name_entry.get()
            image = image_entry.get()
            description = description_entry.get()
            price = price_entry.get()

            # Check if all fields are filled
            if name and image and description and price:
                # Insert into the database
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO locations (name, image, description, price) VALUES (?, ?, ?, ?)",
                                (name, image, description, price))

                messagebox.showinfo("Add Location", "Location added successfully!")

                # Close the add_location_window
                add_location_window.destroy()

                # Refresh the display after adding a location
                self.refresh_display()
            else:
                messagebox.showwarning("Add Location", "Please fill in all fields.")

        # Button to confirm the input
        ok_button = tk.Button(add_location_window, text="OK", command=on_ok)
        ok_button.pack()

        # Button to cancel the operation
        cancel_button = tk.Button(add_location_window, text="Cancel", command=add_location_window.destroy)
        cancel_button.pack()


    def edit_location(self):
        # Fetch the location names from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM locations")
            location_names = [row[0] for row in cursor.fetchall()]

        # Create a pop-up window for selecting the location to edit
        selected_location = simpledialog.askstring("Edit Location", "Select Location to Edit:",
                                                    initialvalue=location_names[0], parent=self.root)
        if not selected_location:
            return  # User pressed cancel

        # Fetch the selected location information from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM locations WHERE name=?", (selected_location,))
            location = cursor.fetchone()

        # Create a pop-up window for editing the location
        edit_location_window = tk.Toplevel(self.root)
        edit_location_window.title("Edit Location")

        # Entry fields for name, image URL, description, and price
        name_label = tk.Label(edit_location_window, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(edit_location_window)
        name_entry.insert(0, location[1])  # Set the current value
        name_entry.pack()

        image_label = tk.Label(edit_location_window, text="Image URL:")
        image_label.pack()
        image_entry = tk.Entry(edit_location_window)
        image_entry.insert(0, location[2])  # Set the current value
        image_entry.pack()

        description_label = tk.Label(edit_location_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(edit_location_window)
        description_entry.insert(0, location[3])  # Set the current value
        description_entry.pack()

        price_label = tk.Label(edit_location_window, text="Price:")
        price_label.pack()
        price_entry = tk.Entry(edit_location_window)
        price_entry.insert(0, location[4])  # Set the current value
        price_entry.pack()

        # Function to handle the "Done" button click
        def on_done():
            # Get values from the entry fields
            new_name = name_entry.get()
            new_image = image_entry.get()
            new_description = description_entry.get()
            new_price = price_entry.get()

            # Update the location information in the database
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE locations SET name=?, image=?, description=?, price=? WHERE name=?",
                            (new_name, new_image, new_description, new_price, selected_location))

            messagebox.showinfo("Edit Location", "Location updated successfully!")

            # Close the edit_location_window
            edit_location_window.destroy()

            # Refresh the display after editing a location
            self.refresh_display()

        # Button to confirm the changes
        done_button = tk.Button(edit_location_window, text="Done", command=on_done)
        done_button.pack()

        # Button to cancel the operation
        cancel_button = tk.Button(edit_location_window, text="Cancel", command=edit_location_window.destroy)
        cancel_button.pack()

    def delete_location(self):
        # Fetch the location names from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM locations")
            location_names = [row[0] for row in cursor.fetchall()]

        # Create a pop-up window for selecting the location to delete
        selected_location = simpledialog.askstring("Delete Location", "Select Location to Delete:",
                                                    initialvalue=location_names[0], parent=self.root)
        if not selected_location:
            return  # User pressed cancel

        # Confirm deletion with the user
        confirmation = messagebox.askyesno("Delete Location", f"Are you sure you want to delete {selected_location}?")
        if not confirmation:
            return  # User canceled the deletion

        # Delete the selected location from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM locations WHERE name=?", (selected_location,))

        messagebox.showinfo("Delete Location", f"{selected_location} deleted successfully!")

        # Refresh the display after deleting a location
        self.refresh_display()

    def refresh_display(self):
        # Clear the current display in the locations frame
        self.clear_display()

        # Redisplay the locations
        self.display_locations()

        self.remove_search_bar()

        if not hasattr(self, 'sign_out_button'):
            self.sign_out_button = tk.Button(self.root, text="Sign Out", command=self.root.destroy)
            self.sign_out_button.pack()

        # Admin CRUD buttons (only visible to admin)
        if self.is_admin:
            if not hasattr(self, 'add_location_button'):
                self.add_location_button = tk.Button(self.add_location_button, text="Add Location", command=self.add_location)
                self.add_location_button.pack(pady=10)

            if not hasattr(self, 'edit_location_button'):
                self.edit_location_button = tk.Button(self.edit_location_button, text="Edit Location", command=self.edit_location)
                self.edit_location_button.pack(pady=5)

            if not hasattr(self, 'delete_location_button'):
                self.delete_location_button = tk.Button(self.delete_food_button, text="Delete Location", command=self.delete_location)
                self.delete_location_button.pack(pady=5)
                
        self.add_search_bar()


    def clear_display(self):
        for widget in self.root.winfo_children():
             if widget != self.sidebar_frame and not isinstance(widget, tk.Button):
                widget.destroy()

        # Clear existing search elements
        self.remove_search_bar()

    def sign_out(self):
        # Close the current window
        self.root.destroy()

        # Open the login/register page
        from login_register import TourismSystem
        root = tk.Tk()
        app = TourismSystem(root)
        root.mainloop()

