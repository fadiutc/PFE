import tkinter as tk
from tkinter import ttk, simpledialog, font as tkFont, messagebox
import pandas as pd
from PIL import Image, ImageTk

EXCEL_FILE_PATH = "C:/Users/ASUS/Downloads/hhhhh/save.xlsx"
LOGO_PATH = "C:/Users/ASUS/Downloads/hhhhh/pura1.png"

def load_data(filename):
    """Load Excel data into a Pandas DataFrame."""
    try:
        return pd.read_excel(filename)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")
        return pd.DataFrame()

def save_data(df, filename):
    """Save the DataFrame to an Excel file."""
    try:
        df.to_excel(filename, index=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {e}")

class ExcelDataFrameViewer(tk.Tk):
    def __init__(self, filename):
        super().__init__()
        self.title("Medical Tools Tracking")
        self.geometry("1000x600")

        # Background image setup
        self.background_image = Image.open(LOGO_PATH)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        background_label = tk.Label(self, image=self.background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Header frame setup
        header_frame = tk.Frame(self, bg="#FFFFFF")
        header_frame.pack(side='top', fill='x', pady=10)

        # Display logo in the header frame
        logo_photo = ImageTk.PhotoImage(self.background_image)
        logo_label = tk.Label(header_frame, image=logo_photo, bg="#FFFFFF")
        logo_label.image = logo_photo
        logo_label.pack(side='left', padx=10)

        # Title label
        title_font = tkFont.Font(family="Arial", size=24, weight="bold", slant="italic")
        title_label = tk.Label(header_frame, text="Medical Tools Tracking", font=title_font, bg="#FFFFFF")
        title_label.pack(expand=True)

        # Load data
        self.df = load_data(filename)

        # Main frame for Treeview
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Treeview styling
        style = ttk.Style(self)
        style.theme_use("clam")
        header_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        style.configure("Treeview.Heading", font=header_font)
        style.map('Treeview', background=[('selected', 'blue')])

        # Treeview widget
        self.tree = ttk.Treeview(main_frame, columns=list(self.df.columns), show="headings", selectmode="browse")
        self.tree.pack(side='left', fill='both', expand=True)

        # Column configuration
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        # Insert row data into Treeview
        self.populate_treeview()

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Message area for warnings and notifications
        self.message_area = tk.Label(self, text="", bg="lightblue", fg="red", font=('Helvetica', 16, 'bold'), relief=tk.SUNKEN, bd=1)
        self.message_area.pack(fill='x', padx=20, pady=10)
        self.display_last_warning()

        # Button panel
        button_frame = tk.Frame(self)
        button_frame.pack(fill='x', padx=20, pady=10)
        tk.Button(button_frame, text="Refresh", command=self.refresh).pack(side='left', padx=10)
        tk.Button(button_frame, text="Add", command=self.add_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text="Delete", command=self.delete_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text="Edit", command=self.edit_entry).pack(side='left', padx=10)

    def populate_treeview(self):
        """Insert row data into the Treeview."""
        for row in self.df.itertuples(index=False, name=None):
            if row[0] == "Image":
                self.tree.insert("", "end", values=row, tags=('separator',))
            else:
                self.tree.insert("", "end", values=row)

        # Apply light blue color styling to separator rows
        self.tree.tag_configure('separator', background='#ADD8E6')

    def display_last_warning(self):
        """Display the last warning message from the Excel file."""
        if not self.df.empty and 'Warning' in self.df.columns:
            last_warning = self.df[self.df['Warning'].notna()]['Warning'].iloc[-1] if not self.df[self.df['Warning'].notna()].empty else "No warnings."
            self.message_area.config(text=last_warning)

    def refresh(self):
        """Refresh the data displayed in the Treeview."""
        self.df = load_data(EXCEL_FILE_PATH)
        self.tree.delete(*self.tree.get_children())
        self.populate_treeview()
        self.display_last_warning()

    def add_entry(self):
        """Add a new entry to the DataFrame and refresh the Treeview."""
        new_data = []
        for col in self.df.columns:
            entry = simpledialog.askstring("Add Entry", f"Enter {col}:")
            new_data.append(entry if entry else "")
        new_df = pd.DataFrame([new_data], columns=self.df.columns)
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        save_data(self.df, EXCEL_FILE_PATH)
        self.refresh()

    def delete_entry(self):
        """Delete the selected entry from the DataFrame and refresh the Treeview."""
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            self.df = self.df.drop(self.df.index[item_index])
            save_data(self.df, EXCEL_FILE_PATH)
            self.refresh()
            messagebox.showinfo("Delete Entry", "Selected entry has been deleted.")

    def edit_entry(self):
        """Edit the selected entry in the DataFrame and refresh the Treeview."""
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            current_values = self.df.iloc[item_index].tolist()
            new_values = []
            for i, col in enumerate(self.df.columns):
                new_value = simpledialog.askstring("Edit Entry", f"Edit {col} (current: {current_values[i]}):", initialvalue=current_values[i])
                new_values.append(new_value if new_value else current_values[i])
            self.df.loc[item_index] = new_values
            save_data(self.df, EXCEL_FILE_PATH)
            self.refresh()
            messagebox.showinfo("Edit Entry", "Selected entry has been updated.")

def main():
    filename = EXCEL_FILE_PATH
    app = ExcelDataFrameViewer(filename)
    app.mainloop()

if __name__ == "__main__":
    main()