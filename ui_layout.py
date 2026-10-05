"""
ui_layout.py - The Frontend
This module strictly handles the graphical user interface. It constructs the
grid layout, manages widget visibility, and captures user input values to
generate a state dictionary for the Orchestrator.
"""

import tkinter as tk
from tkinter import ttk, filedialog as fd, colorchooser
import os


class WatermarkUI:
    def __init__(self, master):
        """Configures the main window dimensions and internal grid structure."""

        self.root = master
        self.root.title("Watermarker Pro")
        self.root.geometry("1280x768")
        self.controller = None

        self.selected_base_images = []
        self.custom_watermark_path = ""
        self.current_color = "#ffffff"

        # dictionary to map the short display names to their full absolute paths
        self.font_mapping = {
            "arial.ttf": "arial.ttf",
            "DejaVuSans.ttf": "DejaVuSans.ttf",
            "times.ttf": "times.ttf",
            "Select a font...": "Select a font..."
        }

        # --- GRID SETUP ---
        # The 'uniform' parameter ensures columns 1 and 2 maintain perfectly equal widths
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1, uniform="group1")
        self.root.columnconfigure(2, weight=1, uniform="group1")

        # Initializes 9 rows. Row 2 is assigned a minimum size to prevent
        # structural collapse when input fields are toggled dynamically.
        for i in range(9):
            if i == 2:
                self.root.rowconfigure(i, weight=1, minsize=115)
            else:
                self.root.rowconfigure(i, weight=1)

        self._build_ui()
        self.toggle_inputs()
        self._bind_events()

    def set_controller(self, controller):
        """Assigns the orchestrator instance for event triggering."""
        self.controller = controller

    def get_state(self):
        """Compiles all UI widget values into a standardized dictionary payload."""
        return {
            "mode": self.choice_var.get(),
            "text_input": self.text_input.get("1.0", "end-1c"),
            "text_align": self.align_var.get(),
            "font_path": self.font_mapping.get(self.font_var.get(), self.font_var.get()), # <-- Mapping applied here
            "watermark_path": self.custom_watermark_path,
            "scale": self.size_scale.get(),
            "transparency": self.transparency_scale.get(),
            "padding": self.padding_scale.get(),
            "position": self.position_var.get(),
            "base_images": self.selected_base_images,
            "color": self.current_color
        }

    def _build_ui(self):
        """Instantiates and arranges all Tkinter widgets onto the grid."""

        # 1. Canvas
        self.canvas = tk.Canvas(self.root, bg="grey", highlightthickness=0, width=800, height=718)
        self.canvas.grid(row=0, column=0, padx=20, pady=20, rowspan=9, sticky="nsew")

        self.canvas_placeholder = self.canvas.create_text(
            0, 0, text="Upload Image(s) to Preview", fill="white", font=("Arial", 16)
        )

        # 2. Clear / Cancel
        self.clear_cancel_btn = tk.Button(self.root, text="Clear", command=self.handle_clear_cancel, fg="white", bg="red")
        self.clear_cancel_btn.grid(row=0, column=2, padx=20, pady=20, sticky="ew")

        # 3. Radio Toggles
        self.choice_var = tk.StringVar(value="Text")
        self.rb_text = tk.Radiobutton(self.root, text="Text", variable=self.choice_var, value="Text", command=self.toggle_inputs)
        self.rb_text.grid(row=1, column=1, padx=20, sticky="ew")

        self.rb_image = tk.Radiobutton(self.root, text="Image", variable=self.choice_var, value="Image", command=self.toggle_inputs)
        self.rb_image.grid(row=1, column=2, padx=20, sticky="ew")

        # 4. Dynamic Input Frame
        self.dynamic_frame = tk.Frame(self.root)
        self.dynamic_frame.grid(row=2, column=1, columnspan=2, padx=15, pady=10, sticky="ew")
        self.dynamic_frame.columnconfigure(0, weight=1)
        self.dynamic_frame.columnconfigure(1, weight=1)

        # Multi-line text widget (height=3 lines, wraps at word boundaries)
        self.text_input = tk.Text(self.dynamic_frame, height=3, width=40, wrap="word")

        self.font_var = tk.StringVar(value="default")
        self.font_dropdown = ttk.Combobox(self.dynamic_frame, textvariable=self.font_var, values=["default"], state="readonly")

        self.custom_font_btn = tk.Button(self.dynamic_frame, text="Add Font...", command=self.upload_custom_font)
        self.color_btn = tk.Button(self.dynamic_frame, text="Chose a colour", command=self.choose_color)

        # The Alignment Dropdown
        self.align_var = tk.StringVar(value="Center")
        self.align_dropdown = ttk.Combobox(self.dynamic_frame, textvariable=self.align_var,
                                           values=["Left", "Center", "Right"], state="readonly")
        # Explicit button to manually trigger text rendering
        self.preview_text_btn = tk.Button(self.dynamic_frame, text="Preview", command=self.trigger_preview)

        self.image_upload_btn = tk.Button(self.dynamic_frame, text="Select Watermark File", command=self.upload_watermark)

        # 5. Universal Sliders and Dropdowns
        self.size_scale = tk.Scale(self.root, from_=0, to=100, orient="horizontal", label="Size (%)", tickinterval=20, resolution=1)
        # Default size of 20%
        self.size_scale.set(20)
        self.size_scale.grid(row=3, column=1, columnspan=2, padx=20, sticky="ew")

        self.transparency_scale = tk.Scale(self.root, from_=0, to=100, orient="horizontal", label="transparency (%)", tickinterval=20, resolution=1)
        self.transparency_scale.grid(row=4, column=1, columnspan=2, padx=20, sticky="ew")

        self.padding_scale = tk.Scale(self.root, from_=0, to=100, orient="horizontal", label="Edge Padding (px)", tickinterval=20, resolution=1)
        self.padding_scale.grid(row=5, column=1, columnspan=2, padx=20, sticky="ew")

        positions = ["Top-Left", "Top-Center", "Top-Right", "Center-Left", "Center", "Center-Right", "Bottom-Left", "Bottom-Center", "Bottom-Right"]
        self.position_var = tk.StringVar(value="Bottom-Right")
        self.position_dropdown = ttk.Combobox(self.root, textvariable=self.position_var, values=positions, state="readonly")
        self.position_dropdown.grid(row=6, column=1, columnspan=2, padx=20, sticky="ew")

        # 6. Action Buttons
        self.upload_base_btn = tk.Button(self.root, text="Upload Image(s)", command=self.upload_base_images, fg="white", bg="blue")
        self.upload_base_btn.grid(row=7, column=1, padx=20, pady=20, sticky="ew")

        self.start_btn = tk.Button(self.root, text="Start", command=self.start_processing, fg="white", bg="green")
        self.start_btn.grid(row=7, column=2, padx=20, pady=20, sticky="ew")

        # 7. Progress Indicator
        self.progress_label = tk.Label(self.root, text="Idle", font=("Arial", 10))
        self.progress_label.grid(row=8, column=1, columnspan=2, sticky="ew")

    def _bind_events(self):
        """Binds widget state changes to the preview rendering mechanism."""
        # Fixes slider lag by only rendering when you release the mouse
        self.align_dropdown.bind("<<ComboboxSelected>>", lambda _: self.trigger_preview())
        self.size_scale.bind("<ButtonRelease-1>", lambda _: self.trigger_preview())
        self.transparency_scale.bind("<ButtonRelease-1>", lambda _: self.trigger_preview())
        self.padding_scale.bind("<ButtonRelease-1>", lambda _: self.trigger_preview())

        self.position_dropdown.bind("<<ComboboxSelected>>", lambda _: self.trigger_preview())
        self.font_dropdown.bind("<<ComboboxSelected>>", lambda _: self.trigger_preview())


        def on_shift_enter(event):
            self.trigger_preview()
            return "break"  # Stops Tkinter from adding a new line

        # Bind Shift+Enter to the function "on_shift_enter"
        self.text_input.bind("<Shift-Return>", on_shift_enter)

        # trigger a preview if one clicks away from the text box
        self.text_input.bind("<FocusOut>", lambda _: self.trigger_preview())

        # Ensures placeholder text remains perfectly centered upon window resize
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, event):
        """Dynamically adjusts the canvas text coordinates relative to current dimensions."""
        if not self.selected_base_images:
            self.canvas.coords(self.canvas_placeholder, event.width / 2, event.height / 2)
        self.trigger_preview()

    def trigger_preview(self):
        """Dispatches an update request to the Orchestrator."""
        if self.controller:
            self.controller.update_canvas_preview()

    def toggle_inputs(self):
        """Manages the visibility of mode-specific widgets via Tkinter grid manipulation."""
        if self.choice_var.get() == "Text":
            self.image_upload_btn.grid_remove()

            # Row 0: Full width multi-line text box
            self.text_input.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

            # Row 1: Font dropdown and custom OS font button
            self.font_dropdown.grid(row=1, column=0, sticky="ew", padx=(5, 2), pady=(0, 5))
            self.custom_font_btn.grid(row=1, column=1, sticky="ew", padx=(2, 5), pady=(0, 5))

            # Row 2: Alignment dropdown on the left, Colour picker on the right
            self.align_dropdown.grid(row=2, column=0, sticky="ew", padx=(5, 2), pady=(0, 5))
            self.color_btn.grid(row=2, column=1, sticky="ew", padx=(2, 5), pady=(0, 5))

            # Row 3: Preview button tucked under the Colour picker (The grip)
            self.preview_text_btn.grid(row=3, column=1, sticky="ew", padx=(2, 5), pady=(0, 5))
        else:
            self.text_input.grid_remove()
            self.font_dropdown.grid_remove()
            self.custom_font_btn.grid_remove()
            self.align_dropdown.grid_remove()
            self.color_btn.grid_remove()
            self.preview_text_btn.grid_remove()

            self.image_upload_btn.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        self.trigger_preview()

    def choose_color(self):
        """Invokes the native OS color dialog and captures the hex value."""
        color_code = colorchooser.askcolor(title="Choose Text Color")[1]
        if color_code:
            self.current_color = color_code
            self.color_btn.config(text=color_code)
            self.trigger_preview()

    def upload_base_images(self):
        paths = fd.askopenfilenames(title="Select Image(s)", filetypes=(("Images", "*.png *.jpg *.jpeg"),))
        if paths:
            self.selected_base_images = list(paths)
            self.trigger_preview()

    def upload_watermark(self):
        path = fd.askopenfilename(title="Select Watermark", filetypes=(("Images", "*.png *.jpg *.jpeg"),))
        if path:
            self.custom_watermark_path = path
            self.trigger_preview()

    def upload_custom_font(self):
        """Permits selection of arbitrary OS fonts and dynamically updates the Combobox."""
        path = fd.askopenfilename(title="Select Font File", filetypes=(("Fonts", "*.ttf *.otf"),))
        if path:
            # get only the file name
            filename = os.path.basename(path)

            # map the short name to the full path
            self.font_mapping[filename] = path

            # Dynamically inject only the short name into the dropdown list
            current_values = list(self.font_dropdown["values"])
            if filename not in current_values:
                current_values.append(filename)
                self.font_dropdown["values"] = current_values

            self.font_var.set(filename)
            self.trigger_preview()

    def handle_clear_cancel(self):
        """Interprets button action based on current processing state."""
        if hasattr(self, 'is_processing') and self.is_processing:
            if self.controller:
                self.controller.abort_job()
        else:
            # 1. Wipes the stored file paths and text input
            self.selected_base_images = []
            self.custom_watermark_path = ""
            self.text_input.delete("1.0", tk.END)

            # 2. THIS IS THE SLIDER RESET LOGIC
            # Explicitly resets all sliders and buttons to their default states
            self.size_scale.set(20) # default size is 20%
            self.transparency_scale.set(0)
            self.padding_scale.set(0)
            self.image_upload_btn.config(text="Select Watermark File")

            # 3. Wipes the visual preview and draws the default text
            self.canvas.delete("all")
            self.align_var.set("Center")
            center_x = self.canvas.winfo_width() / 2
            center_y = self.canvas.winfo_height() / 2
            self.canvas_placeholder = self.canvas.create_text(
                center_x, center_y, text="Preview Cleared\nUpload Image(s) to Preview", fill="white", justify="center", font=("Arial", 16)
            )

    def start_processing(self):
        """Validates base image existence and requests destination output folder."""
        if not self.selected_base_images:
            return
        save_dir = fd.askdirectory(title="Select Save Folder")
        if save_dir and self.controller:
            self.controller.run_batch_job(save_dir)

    def lock_ui(self):
        """Disables interactive elements during batch processing to prevent concurrent state changes."""
        self.is_processing = True
        self.clear_cancel_btn.config(text="Cancel")
        self.start_btn.config(state="disabled")
        self.upload_base_btn.config(state="disabled")

    def unlock_ui(self):
        """Restores interactive capabilities post-execution."""
        self.is_processing = False
        self.clear_cancel_btn.config(text="Clear")
        self.start_btn.config(state="normal")
        self.upload_base_btn.config(state="normal")