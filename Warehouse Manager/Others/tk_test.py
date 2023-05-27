import tkinter as tk
import pandas as pd


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("Navigation App")
        self.geometry("1280x720")

        # Create a menu frame on the left side
        self.menu_frame = tk.Frame(self, bg="lightgray", width=100)
        self.menu_frame.pack(side="left", fill="y")

        # Create buttons for navigation
        self.create_button("Create Orders", self.show_create_orders)
        self.create_button("Warehouse Status", self.show_warehouse_status)
        self.create_button("Settings", self.show_settings)

        # Create a container frame to hold the pages
        self.container = tk.Frame(self)
        self.container.pack(side="left", fill="both", expand=True)

        # Create the pages
        self.pages = {}
        self.create_orders_page()
        self.warehouse_status_page()
        self.settings_page()

        # Show the initial page
        self.show_create_orders()

    def create_button(self, text, command):
        button = tk.Button(self.menu_frame, text=text, width=15, command=command)
        button.pack(pady=10)

    def create_orders_page(self):
        page = tk.Frame(self.container, bg="white")
        label = tk.Label(page, text="Create Orders Page", font=("Arial", 18))
        label.pack(pady=50)
        self.pages["create_orders"] = page

    def warehouse_status_page(self):
        page = tk.Frame(self.container, bg="white")

        items = pd.read_excel(r"Items.xlsx", sheet_name="Items")

        # Create a sample DataFrame
        data = {'Product': ['A', 'B', 'C'],
                'Quantity': [10, 20, 15]}
        df = pd.DataFrame(data)

        # Create a Frame to hold the Text widget and Scrollbars
        frame = tk.Frame(page)
        frame.pack(pady=50)

        # Create a Vertical Scrollbar
        y_scrollbar = tk.Scrollbar(frame, orient="vertical")

        # Create a Horizontal Scrollbar
        x_scrollbar = tk.Scrollbar(frame, orient="horizontal")

        # Create a Text widget with Scrollbars
        text_widget = tk.Text(
            frame,
            height=400,
            width=700,
            wrap="none",  # Prevent automatic line wrapping
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        # Configure the Scrollbars
        y_scrollbar.config(command=text_widget.yview)
        x_scrollbar.config(command=text_widget.xview)

        # Pack the Scrollbars and Text widget
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        text_widget.pack()

        # Insert the DataFrame content into the Text widget
        text_widget.insert(tk.END, items.to_string(index=False))

        self.pages["warehouse_status"] = page

    def settings_page(self):
        page = tk.Frame(self.container, bg="white")
        label = tk.Label(page, text="Settings Page", font=("Arial", 18))
        label.pack(pady=50)
        self.pages["settings"] = page

    def show_create_orders(self):
        self.hide_all_pages()
        self.pages["create_orders"].pack(fill="both", expand=True)

    def show_warehouse_status(self):
        self.hide_all_pages()
        self.pages["warehouse_status"].pack(fill="both", expand=True)

    def show_settings(self):
        self.hide_all_pages()
        self.pages["settings"].pack(fill="both", expand=True)

    def hide_all_pages(self):
        for page in self.pages.values():
            page.pack_forget()


# Create and run the app
app = App()
app.mainloop()