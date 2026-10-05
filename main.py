# Copyright (C) 2026 Joshua Uzochukwu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
main.py - The Orchestrator
This file acts as the application's central controller. It initializes the
graphical user interface (UI) and the image processing engine, routing data
between them. It manages threading to ensure the application remains responsive
during intensive file operations.
"""

import os
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time
from PIL import ImageTk

from ui_layout import WatermarkUI
from image_engine import ImageEngine


class AppController:
    def __init__(self, root):
        """Initialises the application, linking the UI and the processing engine."""
        self.root = root
        self.ui = WatermarkUI(root)
        self.engine = ImageEngine()

        self.ui.set_controller(self)

        # Threading mechanisms to safely control background tasks
        self.abort_flag = threading.Event()
        self.error_response_queue = queue.Queue()

        # Maintains a reference to the Tkinter-compatible image object.
        # If this is not stored, Python's memory management will destroy it,
        # causing the canvas to appear blank.
        self.current_preview_tk = None

    def update_canvas_preview(self):
        """Retrieves UI state, requests a preview from the engine, and renders it."""
        state = self.ui.get_state()
        if not state["base_images"]:
            return

        canvas_w = round(self.ui.canvas.winfo_width())
        canvas_h = round(self.ui.canvas.winfo_height())

        # Prevents execution if the window geometry has not fully initialised
        if canvas_w < 10 or canvas_h < 10:
            return

        # Caches the watermark image in memory if Image mode is selected
        if state["mode"] == "Image" and state["watermark_path"]:
            self.engine.cache_image_watermark(state)

        preview_img = self.engine.generate_preview(state, canvas_w, canvas_h)

        if preview_img:
            self.current_preview_tk = ImageTk.PhotoImage(preview_img)
            self.ui.canvas.delete("all")
            self.ui.canvas.create_image(canvas_w / 2, canvas_h / 2, image=self.current_preview_tk, anchor="center")

    def abort_job(self):
        """Signals the active background thread to terminate."""
        self.abort_flag.set()

    def run_batch_job(self, save_dir):
        """Validates all inputs, locks the UI, and dispatches the background thread."""
        state = self.ui.get_state()

        # --- PRE-FLIGHT VALIDATION ---
        # Ensures necessary files and parameters exist before initiating processing
        if not os.path.exists(save_dir):
            messagebox.showerror("Error", "Save directory is invalid.")
            return
        if state["mode"] == "Text":
            if not state["text_input"]:
                messagebox.showerror("Error", "Please enter watermark text.")
                return
            if state["font_path"] == "Select a font...":
                messagebox.showerror("Error", "Please select a valid font.")
                return
        elif state["mode"] == "Image":
            if not state["watermark_path"] or not os.path.exists(state["watermark_path"]):
                messagebox.showerror("Error", "Please select a valid watermark image.")
                return

        # Pre-process and cache the watermark to avoid redundant calculations in the loop
        if state["mode"] == "Image":
            self.engine.cache_image_watermark(state)

        self.abort_flag.clear()
        self.ui.lock_ui()

        # Spawns a dedicated thread for file processing to maintain UI responsiveness
        thread = threading.Thread(target=self._process_loop, args=(state, save_dir))
        thread.start()

    def _process_loop(self, state, save_dir):
        """Executes the batch processing sequence asynchronously."""
        images = state["base_images"]
        total = len(images)

        for index, img_path in enumerate(images):
            if self.abort_flag.is_set():
                break

            # Validates file existence in case of external deletion during the queue
            if not os.path.exists(img_path):
                continue

            # Schedules a UI update on the main thread
            self.root.after(0, self.ui.progress_label.config, {"text": f"Processing {index + 1}/{total}..."})

            payload = self.engine.process_and_save_image(img_path, state, save_dir)

            # --- ERROR HANDLING ---
            if payload["status"] == "error":
                self.root.after(0, self._prompt_error, payload)

                # Halts thread execution until the user responds via the main UI thread
                user_choice = self.error_response_queue.get()
                if user_choice == "skip":
                    continue
                elif user_choice == "abort":
                    self.abort_job()
                    break

            # Yields execution slightly to prevent CPU starvation
            time.sleep(0.01)

        self.root.after(0, self.ui.unlock_ui)
        self.root.after(0, self.ui.progress_label.config, {"text": "Job Completed."})

    def _prompt_error(self, payload):
        """Generates an error dialog on the main thread and queues the user's response."""
        msg = f"Failed to process:\n{payload['file']}\n\nError: {payload['message']}\n\nSkip file and continue?"
        choice = messagebox.askyesno("Processing Error", msg)
        self.error_response_queue.put("skip" if choice else "abort")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.protocol("WM_DELETE_WINDOW",
                  lambda: root.destroy() if messagebox.askyesno("Quit", "Are you sure you want to quit?") else None)
    root.mainloop()