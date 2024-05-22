from PIL import ImageGrab,Image,ImageTk
import json
import tkinter as tk
from tkinter import ttk,messagebox
import os
import datetime

class EntryWithComboBox(tk.Frame):
    """A class representing a frame containing an entry field, a button, and a combo box.

    Attributes:
        main_obj : The main class of program.
        master: The master widget this frame is attached to.
        frame: A frame widget contained within the entry frame.
        current_datetime: The current date and time.
        default_folder: The default folder obtained from the configuration file.
        entry_var (tk.StringVar): The variable associated with the entry widget.
        entry (ttk.Entry): The entry widget for input.
        button (tk.Button): The button widget for triggering actions.
        combo_var (tk.StringVar): The variable associated with the combo box widget.
        combo (ttk.Combobox): The combo box widget for selecting paths.
    """
    def __init__(self,main_obj, master, *args, **kwargs):
        """Initialize the EntryWithComboBox frame.

        Args:
            main_obj (object): The main object associated with the entry frame.
            master: The master widget this frame is attached to.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(master, *args, **kwargs)
        self.main_obj=main_obj
        self.master=master
        self.frame = tk.Frame(self)
        self.frame.place(anchor=tk.CENTER)
        self.frame.pack(padx=10, pady=10)
        self.current_datetime = datetime.datetime.now()
        self.default_folder = self.get_default_folder()
         # Pole Entry
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.entry_var,width=40,font=("TkDefaultFont",13))
        self.entry.grid(row=0,column=0,pady=5)
        
        # Przycisk
        self.button = tk.Button(self.frame, text="Zatwierdź", command=self.save_img, font=("TkDefaultFont",13))
        self.button.grid(row=0,column=1,pady=5)

        # ComboBox
        self.combo_var = tk.StringVar()
        self.combo = ttk.Combobox(self.frame, textvariable=self.combo_var,width=50,font=("TkDefaultFont",13))
        self.combo['values'] = self.get_paths()
        self.combo.bind("<<ComboboxSelected>>", self.send_path_event)
        self.combo.bind("<Return>", self.send_path_event)
        self.combo.current(0)  # Ustawienie domyślnej wartości
        self.combo.grid(row=1,column=0,columnspan=2,padx=5,pady=5)

    def send_path_event(self,*args):
        """Send path event to the main object.

        Args:
            *args: Variable length argument list.
        """
        event = tk.Event()
        self.main_obj.active_path = self.combo.get()
        self.master.event_generate("<<PathSent>>",when="tail")

    def get_default_folder(self):
        """Get the default folder from the configuration file.

        Returns:
            str: The default folder path.
        """
        with open(".config",'r') as f:
            data=json.load(f)
            f.close()
        return data["default_folder"]
    
    def get_image_clipboard(self):
        """Get image from clipboard.

        Returns:
            Image: The image object from clipboard.
        """
        return ImageGrab.grabclipboard()

    def save_img(self):
        """Save the image to the specified path and to the default screenshot folder path"""
        #Pobranie obrazu
        img= self.get_image_clipboard()
        
        #nazwy
        img_name = str()
        img_name_long = str()
        
        #data 
        formatted_datetime = self.current_datetime.strftime("%m_%d_%Y%H%M%S")
        
        #pobranie sciezki
        path=self.combo.get()
        if not os.path.exists(path):
            os.makedirs(path)
        path_short= "__".join(path.split("\\")[-2:])
        on_defualt=False
        
        #pobranie nazwy
        name=self.entry.get()
       
       #dodanie sciezki do ostatnio uzywanych
        if path !=self.default_folder and path not in self.get_paths():
            self.add_path(path)
        #warunek defualt path
        if path == self.default_folder or path == "":
            path_short=""
            on_defualt=True
        
        name_components=list()
        if not path_short=="":name_components.append(path_short)
        if not name=="": name_components.append(name)
        name_components.append(formatted_datetime)

        img_name_long="___".join(name_components)
        img_name="___".join(name_components[-2:])
        if img is None :
            messagebox.showinfo("Brak screenshota","W schowku nie ma obecnie żadnego screenshota")
        else:    
            img.save(self.default_folder+"\\"+img_name_long+".png",'PNG')
            if not on_defualt:
                img.save(path+"\\"+img_name+".png",'PNG')
        self.main_obj.image_list.reload_img(tk.Event())
        

    def add_path(self,path):
        """Add a currently used path to the configuration file.

        Args:
            path (str): The path to be added.
        """
        with open(".config",'r') as f:
            data=json.load(f)
            f.close()
        data["latest_directories"].insert(0,path)
        with open(".config",'w') as f:
            json.dump(data,f)
            f.close()
        self.combo["values"]= self.get_paths()
    

    def get_paths(self):
        """Get the latest directories from the configuration file.

        Returns:
            list: A list of latest directory paths.
        """
        with open(".config",'r') as f:
            data=json.load(f)
            f.close()
        
        return data["latest_directories"]
    
class LabelWithId(tk.Label):
    """A class representing a label widget with an associated path.

    Attributes:
        path (str): The path associated with the label.
    """
    def __init__(self,master,image,path):
        """Initialize the LabelWithId label.

        Args:
            master: The master widget this label is attached to.
            image: The image to be displayed on the label.
            path (str): The path associated with the label.
        """
        super().__init__(master=master,image=image)
        self.path = path

class EditableLabel(tk.Label):
    """A class representing an editable label widget.

    Attributes:
        name (str): The name associated with the label.
        path (str): The path associated with the label.
        entry (tk.Entry): The entry widget for editing the label text.
    """
    def __init__(self, parent, text,path:str):
        """Initialize the EditableLabel label.

        Args:
            parent: The parent widget this label is attached to.
            text (str): The initial text of the label.
            path (str): The path associated with the label.
        """
        super().__init__(parent, text=text)
        self.entry = tk.Entry(self)
        self.name=text
        self.path=path
        self.bind("<Double-1>", self.edit_start)
        self.entry.bind("<Return>", self.edit_stop)
        self.entry.bind("<FocusOut>", self.edit_stop)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_start(self, event=None):
        """Start editing the label text."""
        self.entry.insert(0,self.name)
        self.entry.place(relx=.5, rely=.5, relwidth=1.0, relheight=1.0, anchor="center")
        self.entry.focus_set()
#zmienia text w labelu i nazwe pliku
    def edit_stop(self, event=None):
        """Stop editing the label text."""
        self.text=self.entry.get()
        self.configure(text=self.text)
        new_name=self.text
        new_path="/".join(self.path.split('/')[:-1])+'/'+self.text+'.png'
        os.rename(self.path,new_path)
        self.path=new_path
        self.name=new_name
        self.entry.place_forget()
    def edit_cancel(self, event=None):
        """Cancel editing the label text."""
        self.entry.delete(0, "end")
        self.entry.place_forget()

class ScrollableImageList(tk.Frame):
    """A class representing a scrollable list of images."""

    def __init__(self, main_obj, master, *args, **kwargs):
        """Initialize the ScrollableImageList frame.

        Args:
            main_obj: The main object associated with the image list.
            master: The master widget this frame is attached to.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.main_obj = main_obj
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<Enter>', self.activate_scroll)
        self.canvas.bind('<Leave>', self.deactivate_scroll)
        self.initialize_list()

    def add_images(self, image_paths):
        """Add images to the list.

        Args:
            image_paths (list): A list of image paths.
        """
        self.images_id = {}
        for id, path in enumerate(image_paths):
            if not path.endswith(".png"):
                continue
            image = Image.open(path)
            if max(image.size) > self.winfo_screenheight() / 2:
                image = image.resize((round(image.size[0] * 0.35), round(image.size[1] * 0.35)), Image.LANCZOS)
            else:
                image = image.resize((round(image.size[0] * 0.6), round(image.size[1] * 0.6)), Image.LANCZOS)
            image = ImageTk.PhotoImage(image)
            image_label = LabelWithId(self.image_frame, image=image, path=path)
            image_label.image = image
            image_label.bind("<Button-1>", lambda event: print(self.open_image(event.widget.path)))
            image_label.pack(pady=5)
            image_name = path.split('/')[-1].rstrip('.png')
            name_label = EditableLabel(self.image_frame, text=image_name, path=path)
            name_label.pack(pady=(0, 5))
            self.image_widgets.append(image_label)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def on_canvas_configure(self, event):
        """Configure the canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def activate_scroll(self, event):
        """Activate scrolling."""
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def deactivate_scroll(self, event):
        """Deactivate scrolling."""
        self.canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_image_paths(self, path):
        """Get image paths from a directory.

        Args:
            path (str): The directory path.

        Returns:
            list: A list of image paths.
        """
        return [path + '/' + f for f in os.listdir(path)][::-1]

    def reload_img(self, event):
        """Reload the image list."""
        self.image_frame.destroy()
        self.initialize_list()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_idletasks()

    def initialize_list(self):
        """Initialize the image list."""
        self.image_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor=tk.CENTER)
        self.image_widgets = []
        self.add_images(self.get_image_paths(self.main_obj.combo.combo.get()))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.deactivate_scroll(tk.Event())

    def open_image(self, path):
        """Open an image in a new window.

        Args:
            path (str): The path of the image to open.
        """
        image = Image.open(path)
        window_width = int(self.master.winfo_screenwidth() * 0.8)
        window_height = int(self.master.winfo_screenheight() * 0.8)
        image = image.resize((window_width, window_height))
        new_window = tk.Toplevel(self.master)
        new_window.title("Image Viewer : " + path)
        new_window.focus_set()
        new_window.bind("<Return>", lambda event: new_window.destroy())
        new_window.bind("<Escape>", lambda event: new_window.destroy())
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(new_window, image=photo)
        label.image = photo
        label.pack()


class ScreenshotMainApp:
    """A class representing the main application for screenshot functionality."""

    def reload_list(self, event):
        """Reload the image list."""
        self.image_list.destroy()
        self.image_list = ScrollableImageList(self, self.window)
        self.image_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def init_window(self):
        """Initialize the main window."""
        self.window = tk.Tk()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f'{screen_width//2}x{screen_height//2}+{screen_width//4}+{screen_height//5}')
        self.window.title("PyScreenshot")

    def __init__(self):
        """Initialize the ScreenshotMainApp."""
        self.init_window()
        self.active_path = str()
        self.combo = EntryWithComboBox(self, self.window)
        self.combo.pack(fill="x", side="top", padx=10, pady=10)
        self.image_list = ScrollableImageList(self, self.window)
        self.image_list.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.window.bind("<Return>", lambda event: self.combo.save_img())
        self.window.bind("<Escape>", lambda event: self.window.quit())
        self.window.bind("<<PathSent>>", self.reload_list)
        self.window.mainloop()
if __name__ == "__main__":
    ScreenshotMainApp()