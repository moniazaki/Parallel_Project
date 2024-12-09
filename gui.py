import os
from tkinter import Tk, filedialog, Button, Label, Text, ttk, Frame, PhotoImage,Canvas, Scrollbar
import threading
from downloader import FileDownloader


class DownloaderGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("File Downloader")
        self.root.geometry("750x750")
        self.root.configure(bg="#f0f4f7")  # Light blue-gray background

        self.urls = []
        self.dest_folder = ""
        self.progress_bars = []
        self.progress_labels = []
        self.file_downloader = None

        self.setup_ui()

    def setup_ui(self):
        # Create a canvas and a scrollable frame
        self.canvas = Canvas(self.root, bg="#f0f4f7")
        self.scrollable_frame = Frame(self.canvas, bg="#f0f4f7")
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
        title_frame = Frame(self.scrollable_frame, bg="#4a90e2")
        title_frame.pack(fill="x")
        Label(
            title_frame, text="File Downloader", font=("Helvetica", 24, "bold"),
            bg="#4a90e2", fg="white", pady=10
        ).pack()

        # URLs Input Section
        input_frame = Frame(self.scrollable_frame, bg="#f0f4f7", pady=10)
        input_frame.pack(fill="x")
        Label(input_frame, text="Enter URLs (one per line):", font=("Arial", 14), bg="#f0f4f7").pack(anchor="w", padx=20)
        self.text_box = Text(input_frame, height=10, width=80, font=("Arial", 12))
        self.text_box.pack(pady=10, padx=20)

        # Destination Folder Section
        folder_frame = Frame(self.scrollable_frame, bg="#f0f4f7", pady=10)
        folder_frame.pack(fill="x")
        Label(folder_frame, text="Destination Folder:", font=("Arial", 14), bg="#f0f4f7").pack(anchor="w", padx=20)
        self.folder_label = Label(folder_frame, text="Not Selected", font=("Arial", 12), bg="#e6e9ed", anchor="w", width=60)
        self.folder_label.pack(pady=5, padx=20)
        Button(
            folder_frame, text="Browse", command=self.browse_folder, font=("Arial", 12),
            bg="#4a90e2", fg="white", activebackground="#3a78c2", activeforeground="white"
        ).pack(pady=5)

        # Status Label
        self.status_label = Label(self.scrollable_frame, text="", font=("Arial", 12), bg="#f0f4f7", fg="#333333")
        self.status_label.pack(pady=5)

        # Control Buttons
        control_frame = Frame(self.scrollable_frame, bg="#f0f4f7", pady=10)
        control_frame.pack()
        Button(
            control_frame, text="Start Download", command=self.start_download_thread, font=("Arial", 12),
            bg="#4a90e2", fg="white", activebackground="#3a78c2", activeforeground="white", width=15
        ).pack(side="left", padx=10)
        Button(
            control_frame, text="Pause", command=self.pause_download, font=("Arial", 12),
            bg="#ffcc00", fg="black", activebackground="#e6b800", activeforeground="black", width=15
        ).pack(side="left", padx=10)
        Button(
            control_frame, text="Resume", command=self.resume_download, font=("Arial", 12),
            bg="#4caf50", fg="white", activebackground="#3e8e41", activeforeground="white", width=15
        ).pack(side="left", padx=10)
        Button(
            control_frame, text="Cancel", command=self.cancel_download, font=("Arial", 12),
            bg="#f44336", fg="white", activebackground="#d32f2f", activeforeground="white", width=15
        ).pack(side="left", padx=10)

        # Progress Section
        progress_frame = Frame(self.scrollable_frame, bg="#f0f4f7", pady=10)
        progress_frame.pack(fill="both", expand=True)
        Label(progress_frame, text="Progress:", font=("Arial", 14), bg="#f0f4f7").pack(anchor="w", padx=20)
        self.progress_frame = Frame(progress_frame, bg="#f0f4f7")
        self.progress_frame.pack(fill="x", padx=20, pady=5)

        # Log Section
        log_frame = Frame(self.scrollable_frame, bg="#f0f4f7", pady=10)
        log_frame.pack(fill="both", expand=True)
        Label(log_frame, text="Logs:", font=("Arial", 14), bg="#f0f4f7").pack(anchor="w", padx=20)
        self.log_box = Text(log_frame, height=10, width=80, font=("Arial", 12), bg="#e6e9ed", state="disabled")
        self.log_box.pack(pady=10, padx=20)

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

        self.update_status("Downloading...", "#4a90e2")
        self.clear_progress_bars()

        self.progress_bars = []
        self.progress_labels = []

        for _ in urls:
            bar = ttk.Progressbar(self.progress_frame, length=600, mode="determinate")
            bar.pack(pady=2)
            self.progress_bars.append(bar)

            label = Label(self.progress_frame, text="0%", font=("Arial", 12), bg="#f0f4f7")
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


