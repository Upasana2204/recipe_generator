import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import io
import webbrowser
from tkinter import font as tkfont

# Spoonacular API setup
API_KEY = "c25f33a039f84132a0616d6737338feb"
BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"

# Custom color scheme
BG_COLOR = "#f5f5f5"
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
ACCENT_COLOR = "#4fc3f7"
TEXT_COLOR = "#333333"

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Recipe Generator")
        self.root.geometry("800x700")
        self.root.configure(bg=BG_COLOR)
        
        # Custom fonts
        self.title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=10)
        self.button_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, padx=20, pady=15)
        header_frame.pack(fill="x")
        
        title_label = tk.Label(
            header_frame, 
            text="Recipe Generator", 
            font=self.title_font,
            fg="white",
            bg=PRIMARY_COLOR
        )
        title_label.pack(side="left")
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=20)
        input_frame.pack(fill="x")
        
        # Ingredients Input
        ingredient_frame = tk.Frame(input_frame, bg=BG_COLOR)
        ingredient_frame.pack(fill="x", pady=5)
        
        tk.Label(
            ingredient_frame,
            text="Ingredients (comma separated):",
            font=self.label_font,
            bg=BG_COLOR
        ).pack(anchor="w")
        
        self.ingredient_entry = ttk.Entry(
            ingredient_frame,
            width=50,
            font=self.label_font
        )
        self.ingredient_entry.pack(fill="x", pady=5)
        
        # Filters Frame
        filters_frame = tk.Frame(input_frame, bg=BG_COLOR)
        filters_frame.pack(fill="x", pady=10)
        
        # Diet Filter
        diet_frame = tk.Frame(filters_frame, bg=BG_COLOR)
        diet_frame.pack(side="left", padx=10)
        
        tk.Label(
            diet_frame,
            text="Diet:",
            font=self.label_font,
            bg=BG_COLOR
        ).pack(anchor="w")
        
        self.diet_combo = ttk.Combobox(
            diet_frame,
            values=["Any", "Vegan", "Vegetarian", "Gluten Free", "Keto", "Paleo"],
            font=self.label_font,
            width=15
        )
        self.diet_combo.current(0)
        self.diet_combo.pack(fill="x")
        
        # Cuisine Filter
        cuisine_frame = tk.Frame(filters_frame, bg=BG_COLOR)
        cuisine_frame.pack(side="left", padx=10)
        
        tk.Label(
            cuisine_frame,
            text="Cuisine:",
            font=self.label_font,
            bg=BG_COLOR
        ).pack(anchor="w")
        
        self.cuisine_combo = ttk.Combobox(
            cuisine_frame,
            values=["Any", "Italian", "Chinese", "Indian", "Mexican", "American"],
            font=self.label_font,
            width=15
        )
        self.cuisine_combo.current(0)
        self.cuisine_combo.pack(fill="x")
        
        # Search Button
        search_button = tk.Button(
            input_frame,
            text="Find Recipes",
            command=self.fetch_recipes,
            bg=SECONDARY_COLOR,
            fg="white",
            font=self.button_font,
            padx=20,
            pady=8,
            relief="flat",
            activebackground=ACCENT_COLOR
        )
        search_button.pack(pady=10)
        
        # Results Frame
        self.result_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable Canvas for results
        self.canvas = tk.Canvas(self.result_frame, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def fetch_recipes(self):
        ingredients = self.ingredient_entry.get().strip()
        if not ingredients:
            messagebox.showwarning("Input Error", "Please enter at least one ingredient.")
            return
        
        diet = self.diet_combo.get()
        cuisine = self.cuisine_combo.get()
        
        # Show loading state
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        loading_label = tk.Label(
            self.scrollable_frame,
            text="Searching for recipes...",
            font=self.label_font,
            bg=BG_COLOR
        )
        loading_label.pack(pady=50)
        self.root.update()
        
        # Get recipes
        recipes = self.get_recipes(
            ingredients,
            None if diet == "Any" else diet,
            None if cuisine == "Any" else cuisine
        )
        
        self.display_recipes(recipes)
    
    def get_recipes(self, ingredients, diet=None, cuisine=None):
        params = {
            "apiKey": API_KEY,
            "includeIngredients": ingredients,
            "diet": diet,
            "cuisine": cuisine,
            "number": 5,  # Fetch 5 recipes
            "addRecipeInformation": True
        }

        try:
            response = requests.get(BASE_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                messagebox.showerror("Error", "Failed to fetch recipes!")
                return []
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server!")
            return []
    
    def display_recipes(self, recipes):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not recipes:
            no_results = tk.Label(
                self.scrollable_frame,
                text="No recipes found. Try different ingredients or filters.",
                font=self.label_font,
                bg=BG_COLOR
            )
            no_results.pack(pady=50)
            return
        
        for i, recipe in enumerate(recipes):
            # Recipe card frame
            card_frame = tk.Frame(
                self.scrollable_frame,
                bg="white",
                bd=1,
                relief="groove",
                padx=15,
                pady=15
            )
            card_frame.pack(fill="x", pady=10, ipady=10)
            
            # Recipe title
            title_frame = tk.Frame(card_frame, bg="white")
            title_frame.pack(fill="x")
            
            tk.Label(
                title_frame,
                text=recipe["title"],
                font=("Helvetica", 12, "bold"),
                bg="white",
                fg=TEXT_COLOR,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
            
            # Recipe image and details
            content_frame = tk.Frame(card_frame, bg="white")
            content_frame.pack(fill="x", pady=10)
            
            # Recipe image
            img_url = recipe["image"]
            try:
                img_data = requests.get(img_url).content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((150, 150), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(
                    content_frame,
                    image=img,
                    bg="white",
                    bd=0
                )
                img_label.image = img
                img_label.pack(side="left", padx=10)
            except Exception as e:
                print("Image load failed:", e)
            
            # Recipe details
            details_frame = tk.Frame(content_frame, bg="white")
            details_frame.pack(side="left", fill="both", expand=True)
            
            # Servings and time
            tk.Label(
                details_frame,
                text=f"🍽️ Servings: {recipe.get('servings', 'N/A')}",
                font=self.label_font,
                bg="white",
                fg=TEXT_COLOR,
                anchor="w"
            ).pack(fill="x", pady=2)
            
            tk.Label(
                details_frame,
                text=f"⏱️ Ready in: {recipe.get('readyInMinutes', 'N/A')} mins",
                font=self.label_font,
                bg="white",
                fg=TEXT_COLOR,
                anchor="w"
            ).pack(fill="x", pady=2)
            
            # View recipe button
            button_frame = tk.Frame(details_frame, bg="white")
            button_frame.pack(fill="x", pady=10)
            
            view_button = tk.Button(
                button_frame,
                text="View Full Recipe",
                command=lambda url=recipe["sourceUrl"]: self.open_url(url),
                bg=PRIMARY_COLOR,
                fg="white",
                font=self.button_font,
                padx=15,
                pady=5,
                relief="flat",
                activebackground=ACCENT_COLOR
            )
            view_button.pack(side="left")
            
            # Add separator between recipes
            if i < len(recipes) - 1:
                ttk.Separator(
                    self.scrollable_frame,
                    orient="horizontal"
                ).pack(fill="x", pady=5)
    
    def open_url(self, url):
        webbrowser.open(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()