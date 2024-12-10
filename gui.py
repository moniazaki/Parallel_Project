import os
from tkinter import Tk, filedialog, Button, Label, Text, ttk, Frame, Canvas, Scrollbar
import threading
from downloader import FileDownloader  # Ensure you have this custom module

# Define constants for repeated values
BG_COLOR = "#14262E"
BUTTON_COLOR = "#19323C"
BUTTON_ACTIVE_COLOR = "#14262E"
ERROR_COLOR = "#F2545B"
SUCCESS_COLOR = "#19323C"
LIGHT_BG = "#F3F7F0"
TEXT_BOX_BG = "#FDF6E3"
TEXT_BOX_FG = "#333333"
TEXT_BOX_CURSOR_COLOR = "#19323C"
FONT_REGULAR = ("Arial", 12)
FONT_BOLD = ("Helvetica", 24, "bold")
FONT_LABEL = ("Arial", 14)
FONT_STATUS = ("Arial", 12)

class DownloaderGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Multiple Files Downloader")
        self.root.geometry("750x750")
        self.root.resizable(False, False)

        self.root.configure(bg=BG_COLOR)  # Background: Mint Cream

        self.urls = []
        self.dest_folder = ""
        self.progress_bars = []
        self.progress_labels = []
        self.file_downloader = None

        self.setup_ui()

    def setup_ui(self):
        # Create a canvas and a scrollable frame
        self.canvas = Canvas(self.root, bg=LIGHT_BG)
        self.scrollable_frame = Frame(self.canvas, bg=LIGHT_BG)
        self.scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind the scrollable frame to the canvas scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Add content to the scrollable frame
        self.create_content()

    def create_content(self):
        # Title Section
        title_frame = self.create_frame(self.scrollable_frame, BG_COLOR)
        title_frame.pack(fill="x")
        Label(
            title_frame, text="Multiple Files Downloader", font=FONT_BOLD,
            bg=BG_COLOR, fg="white", pady=10
        ).pack()

        # URLs Input Section
        input_frame = self.create_frame(self.scrollable_frame, LIGHT_BG, pady=10)
        input_frame.pack(fill="x")
        Label(input_frame, text="Enter URLs (one per line):", font=FONT_LABEL, bg=LIGHT_BG).pack(anchor="w", padx=20)
        self.text_box = self.create_text_box(input_frame)
        self.text_box.pack(pady=10, padx=20)

        # Destination Folder Section
        folder_frame = self.create_frame(self.scrollable_frame, LIGHT_BG, pady=10)
        folder_frame.pack(fill="x")
        Label(folder_frame, text="Destination Folder:", font=FONT_LABEL, bg=LIGHT_BG).pack(anchor="w", padx=20)
        self.folder_label = Label(folder_frame, text="Not Selected", font=FONT_REGULAR, bg=TEXT_BOX_BG, fg=TEXT_BOX_FG, anchor="w", width=70)
        self.folder_label.pack(pady=5, padx=20)
        Button(
            folder_frame, text="Browse", command=self.browse_folder, font=FONT_REGULAR,
            bg=BUTTON_COLOR, fg="white", activebackground=BUTTON_ACTIVE_COLOR, activeforeground="white"
        ).pack(pady=5)

        # Status Label
        self.status_label = Label(self.scrollable_frame, text="", font=FONT_STATUS, bg=LIGHT_BG, fg=TEXT_BOX_FG)
        self.status_label.pack(pady=5)

        # Control Buttons
        control_frame = self.create_frame(self.scrollable_frame, LIGHT_BG, pady=10)
        control_frame.pack()
        self.create_button(control_frame, "Start Download", self.start_download_thread, BUTTON_COLOR, BUTTON_ACTIVE_COLOR, 15)
        self.create_button(control_frame, "Pause", self.pause_download, ERROR_COLOR, "#C2434A", 15)
        self.create_button(control_frame, "Resume", self.resume_download, BUTTON_COLOR, BUTTON_ACTIVE_COLOR, 15)
        self.create_button(control_frame, "Cancel", self.cancel_download, ERROR_COLOR, "#C2434A", 15)

        # Progress Section
        progress_frame = self.create_frame(self.scrollable_frame, LIGHT_BG, pady=10)
        progress_frame.pack(fill="both", expand=True)
        Label(progress_frame, text="Progress:", font=FONT_LABEL, bg=LIGHT_BG).pack(anchor="w", padx=20)
        self.progress_frame = Frame(progress_frame, bg=LIGHT_BG)
        self.progress_frame.pack(fill="x", padx=20, pady=5)

        # Log Section
        log_frame = self.create_frame(self.scrollable_frame, LIGHT_BG, pady=10)
        log_frame.pack(fill="both", expand=True)
        Label(log_frame, text="Logs:", font=FONT_LABEL, bg=LIGHT_BG).pack(anchor="w", padx=20)
        self.log_box = self.create_text_box(log_frame, state="disabled")  # Read-only log box
        self.log_box.pack(pady=10, padx=20)

    def create_frame(self, parent, bg_color, pady=0):
        frame = Frame(parent, bg=bg_color, pady=pady)
        return frame

    def create_text_box(self, parent, state="normal"):
        return Text(
            parent, height=10, width=80, font=FONT_REGULAR,
            bg=TEXT_BOX_BG, fg=TEXT_BOX_FG, insertbackground=TEXT_BOX_CURSOR_COLOR, state=state
        )

    def create_button(self, parent, text, command, bg_color, active_bg_color, width):
        Button(
            parent, text=text, command=command, font=FONT_REGULAR,
            bg=bg_color, fg="white", activebackground=active_bg_color, activeforeground="white", width=width
        ).pack(side="left", padx=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_label.config(text=folder)

    def start_download_thread(self):
        thread = threading.Thread(target=self.start_download)
        thread.start()

    def start_download(self):
        urls = self.text_box.get("1.0", "end-1c").splitlines()
        dest_folder = self.folder_label.cget("text")

        if not urls:
            self.update_status("Enter URLs to download.", "red")
            return
        if not dest_folder or dest_folder == "Not Selected":
            self.update_status("Select a destination folder.", "red")
            return

        self.update_status("Downloading...", BUTTON_COLOR)
        self.clear_progress_bars()

        self.progress_bars = []
        self.progress_labels = []

        for _ in urls:
            bar = ttk.Progressbar(self.progress_frame, length=600, mode="determinate")
            bar.pack(pady=2)
            self.progress_bars.append(bar)

            label = Label(self.progress_frame, text="0%", font=FONT_REGULAR, bg=LIGHT_BG)
            label.pack(pady=2)
            self.progress_labels.append(label)

        self.file_downloader = FileDownloader(
            urls, dest_folder, self.update_progress, self.update_error
        )
        self.file_downloader.start_download()
        self.update_status("Download Complete!", "green")

    def pause_download(self):
        if self.file_downloader:
            self.file_downloader.pause()
            self.log_message("Download paused.")

    def resume_download(self):
        if self.file_downloader:
            self.file_downloader.resume()
            self.log_message("Download resumed.")

    def cancel_download(self):
        if self.file_downloader:
            self.file_downloader.stop()
            self.update_status("Download canceled.", "red")
            self.log_message("Download canceled.")

    def clear_progress_bars(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

    def update_progress(self, index, progress):
        if progress == -1:
            self.progress_labels[index].config(text="Failed", fg="red")
        else:
            self.progress_bars[index]["value"] = progress
            self.progress_labels[index].config(text=f"{progress:.2f}%")

    def update_error(self, index, message):
        self.progress_labels[index].config(text=message, fg="red")
        self.log_message(f"Error for file {index + 1}: {message}")

    def update_status(self, message, color):
        self.status_label.config(text=message, fg=color)

    def log_message(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.config(state="disabled")

    def run(self):
        self.root.mainloop()


