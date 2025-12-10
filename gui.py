import tkinter as tk
from tkinter import filedialog
import os

from downloader import Downloader

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
downloader = Downloader()

root = tk.Tk()
root.title("Video Downloader")
root.geometry("800x550")
root.resizable(False, False)

# Logo
logo = tk.PhotoImage(file="logo.png", width=300, height=150)
logo_label = tk.Label(root, image=logo)
logo_label.grid(row=0, column=0, columnspan=2, padx=50, pady=20)

# Frame for input fields
frame = tk.Frame(root, width=700, height=400)
frame.grid(row=1, column=0, columnspan=2, padx=50, pady=10)


# URL label and text on the same line
tk.Label(frame, text="URL: ", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
url_text = tk.Text(frame, height=1, width=50, font=("Arial", 12))
url_text.grid(row=0, column=1, columnspan=1, padx=10, pady=(10,0))

# Validation label
validation_label = tk.Label(frame, text="", height=2, font=("Arial", 10), fg="red", wraplength=400, justify="left", anchor="n")
validation_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

# Check URL button
def check_url():
    check_url_button.config(state=tk.DISABLED)
    download_button.config(state=tk.DISABLED)
    downloader.url = url_text.get("1.0", tk.END).strip()
    status, message = downloader.check_url()
    if status:
        filename_text.delete("1.0", tk.END)
        filename_text.insert(tk.END, downloader.title)

        title = downloader.title if len(downloader.title) <= 50 else downloader.title[:47] + "..."
        validation_label.config(text=f"Valid URL: {title}. Duration: {downloader.duration}s", fg="green")

        transcription_check.config(state="normal" if downloader.has_cc else "disabled")
    else:
        validation_label.config(text=message, fg="red")
    
    check_url_button.config(state=tk.ACTIVE)
    download_button.config(state=tk.ACTIVE)
check_url_button = tk.Button(frame, text="Check URL", width=10, font=("Arial", 10), command=check_url)
check_url_button.grid(row=0, column=2, padx=10, pady=(10,0))


# Folder path label and text
tk.Label(frame, text="Folder Path: ", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=(10,20), sticky="w")
folder_entry = tk.Entry(frame, width=50, font=("Arial", 12))
folder_entry.grid(row=2, column=1, padx=10, pady=(10,20))
folder_entry.insert(0, CURRENT_DIR+"/downloads")

# Folder path browse button
def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_selected)
tk.Button(frame, text="Browse", width=10, font=("Arial", 10), command=select_folder).grid(row=2, column=2, padx=10, pady=(10,20))


# File name label and text
tk.Label(frame, text="File Name: ", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=(10,20), sticky="w")
filename_text = tk.Text(frame, height=1, width=63, font=("Arial", 12))
filename_text.grid(row=3, column=1, columnspan=2, padx=10, pady=(10,20))


# Mode checkbox
tk.Label(frame, text="Mode: ", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=(10,20), sticky="w")
checkbox_frame = tk.Frame(frame)
checkbox_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=(10,20))
mode_var = tk.StringVar(value="video")
tk.Radiobutton(checkbox_frame, text="Video", variable=mode_var, value="video", font=("Arial", 10)).grid(row=0, column=0, padx=10)
tk.Radiobutton(checkbox_frame, text="Audio", variable=mode_var, value="audio", font=("Arial", 10)).grid(row=0, column=1, padx=10)
transcription_check = tk.Radiobutton(checkbox_frame, text="Transcription", variable=mode_var, value="transcription", font=("Arial", 10))
transcription_check.grid(row=0, column=2, padx=10)
tk.Radiobutton(checkbox_frame, text="Audio+Transcription", variable=mode_var, value="audio_transcription", font=("Arial", 10)).grid(row=0, column=3, padx=10)


# Download button
def download():
    downloader.url = url_text.get("1.0", tk.END).strip()
    downloader.folder_path = folder_entry.get().strip()
    downloader.filename = filename_text.get("1.0", tk.END).strip()
    mode = mode_var.get()

    status, message = downloader.check_url()
    if not status: tk.messagebox.showerror("Invalid URL", message)
    else:
        check_url_button.config(state=tk.DISABLED)
        download_button.config(state=tk.DISABLED)
        try:
            if mode == "video":
                downloader.download_video()
            elif mode == "audio":
                downloader.download_audio()
            else:
                downloader.transcribe_audio(exclude_cc=False if mode == "transcription" else True)
            tk.messagebox.showinfo("Download Complete", "The download has been completed successfully.")
        except Exception as e:
            tk.messagebox.showerror("Download Error", f"An error occurred during download: {str(e)}")
        finally:
            check_url_button.config(state=tk.ACTIVE)
            download_button.config(state=tk.ACTIVE)
download_button = tk.Button(frame, text="Download", font=("Arial", 12), command=download)
download_button.grid(row=5, column=0, columnspan=2, pady=20)

root.mainloop()