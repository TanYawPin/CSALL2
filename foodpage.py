import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from PIL import Image, ImageTk
from functools import partial

class FoodPage(tk.Toplevel):
    def __init__(self, root, username, is_admin=False):
        self.root = root
        self.root.title("Tourism App")

        # Initialize database
        self.conn = sqlite3.connect('tourism_foods.db')
        self.create_food_table()

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
            self.add_food_button = tk.Button(self.root, text="Add Food", command=self.add_food)
            self.add_food_button.pack(pady=10)

            self.edit_food_button = tk.Button(self.root, text="Edit Food", command=self.edit_food)
            self.edit_food_button.pack(pady=5)

            self.delete_food_button = tk.Button(self.root, text="Delete Food", command=self.delete_food)
            self.delete_food_button.pack(pady=5)

        self.sign_out_button = tk.Button(self.root, text="Sign Out", command=self.sign_out)
        self.sign_out_button.pack()

        self.show_food()

    def create_food_table(self):
        # Create location table if not exists
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS foods (
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
        if self.is_admin:
            if hasattr(self, 'add_food_button'):
                self.add_food_button.pack_forget()
            if hasattr(self, 'edit_food_button'):
                self.edit_food_button.pack_forget()
            if hasattr(self, 'delete_food_button'):
                self.delete_food_button.pack_forget()
        self.sign_out_button.pack_forget()

        # Open the FoodPage when the "Food" button is pressed
        from homepage import HomePage
        homepage = HomePage(self.root, self.username, self.is_admin)
        homepage.grab_set() 
        self.root.wait_window(homepage)

    def show_food(self):
        # Clear current display
        self.clear_display()

        self.label_welcome = tk.Label(self.root, text=f"Welcome, {self.username}")
        self.label_welcome.pack(pady=10)

        self.add_search_bar()
        # Display food
        self.display_foods()


    def show_transport(self):
        # Clear current display
        self.clear_display()
        if self.is_admin:
            if hasattr(self, 'add_food_button'):
                self.add_food_button.pack_forget()
            if hasattr(self, 'edit_food_button'):
                self.edit_food_button.pack_forget()
            if hasattr(self, 'delete_food_button'):
                self.delete_food_button.pack_forget()
        self.sign_out_button.pack_forget()


        from transportpage import TransportPage
        transportpage = TransportPage(self.root, self.username, self.is_admin)
        transportpage.grab_set() 
        self.root.wait_window(transportpage)

    def show_map(self):
        self.clear_display()

        if self.is_admin:
            if hasattr(self, 'add_food_button'):
                self.add_food_button.pack_forget()
            if hasattr(self, 'edit_food_button'):
                self.edit_food_button.pack_forget()
            if hasattr(self, 'delete_food_button'):
                self.delete_food_button.pack_forget()
        self.sign_out_button.pack_forget()

        from map import Map
        map = Map(self.root, self.username, self.is_admin)
        map.grab_set()
        self.root.wait_window(map)

    def search_foods(self, search_term):
        # Clear current display
        self.clear_display()

        self.label_welcome = tk.Label(self.root, text=f"Welcome, {self.username}")
        self.label_welcome.pack(pady=10)

        self.add_search_bar()

        # Display locations based on the search term
        self.display_foods(search_term)

    def add_search_bar(self):
        # Create entry widget for search term
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack(pady=5)

        # Create search button
        self.search_button = tk.Button(
            self.root, text="Search", command=lambda: self.search_foods(self.search_entry.get())
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

    def display_foods(self, search_term=None):
        # Fetch food from the database and display them
        with self.conn:
            cursor = self.conn.cursor()
            if search_term:
                # Use LIKE to find names that contain the search term
                cursor.execute("SELECT * FROM foods WHERE name LIKE ?", ('%' + search_term + '%',))
            else:
                cursor.execute("SELECT * FROM foods")
            foods = cursor.fetchall()

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

        for i, food in enumerate(foods):
            # Load image
            image_path = food[2]  # Assuming image path is stored in the third column
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Adjust the size as needed
            img = ImageTk.PhotoImage(img)

            # Create a frame for each food's information
            food_frame = tk.Frame(items_frame)
            food_frame.grid(row=i // num_columns, column=i % num_columns, padx=10, pady=10)

            # Display image
            image_label = tk.Label(food_frame, image=img)
            image_label.image = img
            image_label.grid(row=0, column=0, padx=10, pady=10)

            # Display name, description, and price below the image
            name_label = tk.Label(food_frame, text=f"Name: {food[1]}", anchor="w")
            name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            description_label = tk.Label(food_frame, text=f"Description: {food[3]}", anchor="w")
            description_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            price_label = tk.Label(food_frame, text=f"Price: {food[4]}", anchor="w")
            price_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Set up canvas scrolling region 
        items_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        remaining_cells = (num_columns - (len(foods) % num_columns)) % num_columns
        for _ in range(remaining_cells):
            empty_label = tk.Label(grid_frame, text="")
            empty_label.grid(row=len(foods) // num_columns * 4, column=(len(foods) % num_columns) + _, padx=10, pady=10)


    def add_food(self):
        # Create a Toplevel window for the input fields
        add_food_window = tk.Toplevel(self.root)
        add_food_window.title("Add foods")

        # Entry fields for name, image URL, description, and price
        name_label = tk.Label(add_food_window, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(add_food_window)
        name_entry.pack()

        image_label = tk.Label(add_food_window, text="Image URL:")
        image_label.pack()
        image_entry = tk.Entry(add_food_window)
        image_entry.pack()

        description_label = tk.Label(add_food_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(add_food_window)
        description_entry.pack()

        price_label = tk.Label(add_food_window, text="Price:")
        price_label.pack()
        price_entry = tk.Entry(add_food_window)
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
                    cursor.execute("INSERT INTO foods (name, image, description, price) VALUES (?, ?, ?, ?)",
                                (name, image, description, price))

                messagebox.showinfo("Add Food", "Food added successfully!")

                # Close the add_food_window
                add_food_window.destroy()

                # Refresh the display after adding a location
                self.refresh_display()
            else:
                messagebox.showwarning("Add Food", "Please fill in all fields.")

        # Button to confirm the input
        ok_button = tk.Button(add_food_window, text="OK", command=on_ok)
        ok_button.pack()

        # Button to cancel the operation
        cancel_button = tk.Button(add_food_window, text="Cancel", command=add_food_window.destroy)
        cancel_button.pack()

    def edit_food(self):
        # Fetch the food names from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM foods")
            food_names = [row[0] for row in cursor.fetchall()]

        # Create a pop-up window for selecting the food to edit
        selected_food = simpledialog.askstring("Edit Food", "Select Food to Edit:",
                                                    initialvalue=food_names[0], parent=self.root)
        if not selected_food:
            return  # User pressed cancel

        # Fetch the selected location information from the database
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM foods WHERE name=?", (selected_food,))
            food = cursor.fetchone()

        # Create a pop-up window for editing the location
        edit_food_window = tk.Toplevel(self.root)
        edit_food_window.title("Edit Food")

        # Entry fields for name, image URL, description, and price
        name_label = tk.Label(edit_food_window, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(edit_food_window)
        name_entry.insert(0, food[1])  # Set the current value
        name_entry.pack()

        image_label = tk.Label(edit_food_window, text="Image URL:")
        image_label.pack()
        image_entry = tk.Entry(edit_food_window)
        image_entry.insert(0, food[2])  # Set the current value
        image_entry.pack()

        description_label = tk.Label(edit_food_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(edit_food_window)
        description_entry.insert(0, food[3])  # Set the current value
        description_entry.pack()

        price_label = tk.Label(edit_food_window, text="Price:")
        price_label.pack()
        price_entry = tk.Entry(edit_food_window)
        price_entry.insert(0, food[4])  # Set the current value
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
                cursor.execute("UPDATE foods SET name=?, image=?, description=?, price=? WHERE name=?",
                            (new_name, new_image, new_description, new_price, selected_food))

            messagebox.showinfo("Edit Food", "Food updated successfully!")

            # Close the edit_location_window
            edit_food_window.destroy()

            # Refresh the display after editing a location
            self.refresh_display()

        # Button to confirm the changes
        done_button = tk.Button(edit_food_window, text="Done", command=on_done)
        done_button.pack()

        # Button to cancel the operation
        cancel_button = tk.Button(edit_food_window, text="Cancel", command=edit_food_window.destroy)
        cancel_button.pack()
    
    def delete_food(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM foods")
            food_names = [row[0] for row in cursor.fetchall()]

        selected_food = simpledialog.askstring("Delete Food", "Select Food to Delete:",
                                                    initialvalue=food_names[0], parent=self.root)
        if not selected_food:
            return  # User pressed cancel

        # Confirm deletion with the user
        confirmation = messagebox.askyesno("Delete Food", f"Are you sure you want to delete {selected_food}?")
        if not confirmation:
            return  # User canceled the deletion

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM foods WHERE name=?", (selected_food,))

        messagebox.showinfo("Delete Food", f"{selected_food} deleted successfully!")

        self.refresh_display()

    def refresh_display(self):
        # Clear the current food display
        self.clear_display()

        # Redisplay the locations
        self.display_foods()

        self.remove_search_bar()

        if not hasattr(self, 'sign_out_button'):
            self.sign_out_button = tk.Button(self.root, text="Sign Out", command=self.root.destroy)
            self.sign_out_button.pack()

        # Admin CRUD buttons (only visible to admin)
        if self.is_admin:
            if not hasattr(self, 'add_food_button'):
                self.add_food_button = tk.Button(self.root, text="Add Food", command=self.add_food)
                self.add_food_button.pack(pady=10)

            if not hasattr(self, 'edit_food_button'):
                self.edit_food_button = tk.Button(self.root, text="Edit Food", command=self.edit_food)
                self.edit_food_button.pack(pady=5)

            if not hasattr(self, 'delete_food_button'):
                self.delete_food_button = tk.Button(self.root, text="Delete Food", command=self.delete_food)
                self.delete_food_button.pack(pady=5)

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