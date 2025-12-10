import tkinter as tk
from tkinter import filedialog
import os

from downloader import Downloader


# Initialize the downloader
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
downloader = Downloader()


# Create the main application window
root = tk.Tk()
root.title("Video Downloader")
root.geometry("800x550")
root.resizable(False, False)

# Set the logo for the application
logo_width = 400
logo_height = 150
canvas = tk.Canvas(root, width=logo_width, height=logo_height)
canvas.grid(row=0, column=0, columnspan=2, padx=50, pady=(40,0))
logo = tk.PhotoImage(file="logo.png")
canvas.create_image(logo_width//2, logo_height//2, image=logo, anchor="center")
canvas.image = logo

# Create a frame for easier management of input fields
url_frame = tk.Frame(root, width=700, height=400)
url_frame.grid(row=1, column=0, columnspan=2, padx=50, pady=0)

# URL label and text on the same line
tk.Label(url_frame, text="URL: ", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
url_text = tk.Text(url_frame, height=1, width=50, font=("Arial", 12))
url_text.grid(row=0, column=1, columnspan=1, padx=10, pady=(10,0))
# Validation label below URL text
validation_label = tk.Label(url_frame, text="", height=2, font=("Arial", 10), fg="red", wraplength=400, justify="left", anchor="n")
validation_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

# Folder path label and text on the same line
tk.Label(url_frame, text="Folder Path: ", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=(10,20), sticky="w")
folder_entry = tk.Entry(url_frame, width=50, font=("Arial", 12))
folder_entry.grid(row=2, column=1, padx=10, pady=(10,20))
folder_entry.insert(0, CURRENT_DIR+"/downloads")

# File name label and text on the same line
tk.Label(url_frame, text="File Name: ", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=(10,20), sticky="w")
filename_text = tk.Text(url_frame, height=1, width=63, font=("Arial", 12))
filename_text.grid(row=3, column=1, columnspan=2, padx=10, pady=(10,20))

# Mode checkbox
tk.Label(url_frame, text="Mode: ", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=(10,20), sticky="w")
checkbox_frame = tk.Frame(url_frame)
checkbox_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=(10,20))
mode_var = tk.StringVar(value="video")
tk.Radiobutton(checkbox_frame, text="Video", variable=mode_var, value="video", font=("Arial", 10)).grid(row=0, column=0, padx=10)
tk.Radiobutton(checkbox_frame, text="Audio", variable=mode_var, value="audio", font=("Arial", 10)).grid(row=0, column=1, padx=10)
transcription_check = tk.Radiobutton(checkbox_frame, text="Transcription", variable=mode_var, value="transcription", font=("Arial", 10))
transcription_check.grid(row=0, column=2, padx=10)
tk.Radiobutton(checkbox_frame, text="Audio+Transcription", variable=mode_var, value="audio_transcription", font=("Arial", 10)).grid(row=0, column=3, padx=10)


# Buttons and their functions
def check_url():
    """ Get the text from the URL text box and check if it's valid. Update the validation label and the transcription mode accordingly. """
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
# Check URL button
check_url_button = tk.Button(url_frame, text="Check URL", width=10, font=("Arial", 10), command=check_url)
check_url_button.grid(row=0, column=2, padx=10, pady=(10,0))

# ------------------------------------------------------------------------------------------------------------ #

def select_folder():
    """ Open a folder selection dialog and update the folder path entry. """
    folder_selected = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_selected)
# Folder path browse button
tk.Button(url_frame, text="Browse", width=10, font=("Arial", 10), command=select_folder).grid(row=2, column=2, padx=10, pady=(10,20))

# ------------------------------------------------------------------------------------------------------------ #

def download():
    """ Start the download process based on the selected mode. """
    downloader.url = url_text.get("1.0", tk.END).strip()
    downloader.folder_path = folder_entry.get().strip()
    downloader.filename = filename_text.get("1.0", tk.END).strip()
    mode = mode_var.get()

    os.makedirs(downloader.folder_path, exist_ok=True)
    downloader.filename = downloader.filename if downloader.filename else downloader.title

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
# Download button
download_button = tk.Button(url_frame, text="Download", font=("Arial", 12), command=download)
download_button.grid(row=5, column=0, columnspan=3, pady=20)


# Start the main event loop
root.mainloop()