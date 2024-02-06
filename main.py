import tkinter as tk
from tkinter import Label, scrolledtext, messagebox, filedialog, ttk
import threading
import os
from PIL import Image, ImageTk

from image_generator_comfyui_nolargefiles import generate_portraits
from DnDGameClasses import DnDGameMaster


def display_prompt(message):
    messagebox.showinfo("Prompt", message)


def run_generate_portraits():
    display_prompt("Generating portrait with prompts...")
    try:
        test_json = {
            "Sorceress": [
                "Young sorceress, short brown hair, girl, brown eyes, purple robe",
                "boy",
            ]
        }
        # generate_portraits.main(test_json)
        messagebox.showinfo("Success", "Portrait generation completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate portrait. Error: {str(e)}")


def run_generate_backgrounds():
    display_prompt("Generating background with prompts...")
    try:
        # generate_background.main()  # Add appropriate arguments as needed
        messagebox.showinfo("Success", "Background generation completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate background. Error: {str(e)}")


def display_image(image_path):
    global photo_image  # Prevent the image from being garbage-collected
    image = Image.open(image_path)
    image = resize_image_aspect_ratio(image, 800, 600)
    photo_image = ImageTk.PhotoImage(image)
    image_label.config(image=photo_image)
    image_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


def resize_image_aspect_ratio(image, max_width, max_height, resample=Image.BICUBIC):
    """
    Resize an image while maintaining its aspect ratio.

    Args:
        image (PIL.Image): The original image.
        max_width (int): Maximum width the image should have after resizing.
        max_height (int): Maximum height the image should have after resizing.
        resample (PIL.Image.Resampling): The resampling filter to use.

    Returns:
        PIL.Image: The resized image.
    """
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    resized_image = image.resize((new_width, new_height), resample=resample)

    return resized_image


def select_latest_image():
    output_folder = "image_generator_comfyui_nolargefiles/ComfyUI/output"
    try:
        # List all files in the output folder and find the newest (last modified) image
        files = [os.path.join(output_folder, f) for f in os.listdir(output_folder)]
        latest_image = max(files, key=os.path.getmtime)
        display_image(latest_image)
    except Exception as e:
        messagebox.showerror(
            "Error", f"Failed to display the latest image. Error: {str(e)}"
        )


def fetch_response_and_update_ui(message):
    """
    Fetches response from the chat model in a separate thread and updates the UI.
    """
    try:
        response = game_master.process_input(message)
        # This thread queues, allowing asynchronous calls to the UI
        app.after(0, update_ai_chat_history, response)
    finally:
        app.after(0, reset_send_button)


# def update_chat_history(user_message, ai_response):
#     """
#     Updates the chat history with the user's message and the AI's response.
#     """
#     chat_history.configure(state=tk.NORMAL)

#     # Insert the user's message with a specific formatting
#     user_message_formatted = f"\nYou: {user_message}\n"
#     chat_history.insert(tk.END, user_message_formatted, "user")

#     # Insert a newline for spacing if needed
#     chat_history.insert(tk.END, "\n")

#     # Insert the AI's response with a different formatting
#     ai_response_formatted = f"Game Master: {ai_response}\n"
#     chat_history.insert(tk.END, ai_response_formatted, "ai")

#     chat_history.see(tk.END)  # Scroll to the bottom to see the latest messages
#     chat_history.configure(state=tk.DISABLED)


def update_ai_chat_history(ai_response):
    """
    Updates the chat history with the AI's response.
    """
    chat_history.configure(state=tk.NORMAL)

    # Insert the AI's response with a different formatting
    ai_response_formatted = f"Game Master: {ai_response}\n"
    chat_history.insert(tk.END, ai_response_formatted, "ai")

    chat_history.see(tk.END)  # Scroll to the bottom to see the latest messages
    chat_history.configure(state=tk.DISABLED)


def update_user_chat_history(user_message):
    """
    Updates the chat history with the user's message.
    """
    chat_history.configure(state=tk.NORMAL)

    # Insert the user's message with a specific formatting
    user_message_formatted = f"\nYou: {user_message}\n"
    chat_history.insert(tk.END, user_message_formatted, "user")

    chat_history.see(tk.END)  # Scroll to the bottom to see the latest messages
    chat_history.configure(state=tk.DISABLED)


def start_game():
    update_ai_chat_history(
        "Welcome to AI Dungeons & Dragons! \n\n Please choose a world setting for your DnD quest:\n\n1. The Shattered Isles \n2. Jungle World \n3. The Frozen Wastes"
    )


def reset_send_button():
    send_button.config(state=tk.NORMAL, text="Send")


def send_message():
    message = user_input.get("1.0", tk.END).strip()
    if message:
        send_button.config(state=tk.DISABLED, text="Loading...")  # Indicate loading
        user_input.delete("1.0", tk.END)  # Clear the input after sending the message
        update_user_chat_history(message)
        threading.Thread(target=fetch_response_and_update_ui, args=(message,)).start()


def on_send_message_click(event=None):
    send_message()


game_master = DnDGameMaster()
app = tk.Tk()
app.title("AI Dungeons & Dragons")

# Set the theme for light mode
style = ttk.Style()
style.theme_use("clam")

light_background = "#FFFFFF"
dark_text = "#000000"
input_background = "#F0F0F0"
button_color = "#E1E1E1"

# Configure the grid layout
app.configure(background=light_background)
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=3)
app.grid_columnconfigure(1, weight=2)

# Left side frame for chat and controls
left_frame = tk.Frame(app, bg=light_background, padx=10, pady=10)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_rowconfigure(1, weight=1)  # Allow chat history to expand

# Right side for image display
image_label = Label(app, bg=light_background)

# Chat History Box
chat_history = scrolledtext.ScrolledText(
    left_frame, state="disabled", height=30, bg=light_background, fg=dark_text
)
chat_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
chat_history.tag_configure("user", foreground="blue", font=("Helvetica", 14, ""))
chat_history.tag_configure("ai", foreground="green", font=("Helvetica", 14, "bold"))
# User Input Box
user_input = tk.Text(left_frame, height=3)
user_input.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
user_input.bind("<Return>", on_send_message_click)

# Buttons Frame
buttons_frame = tk.Frame(left_frame)
buttons_frame.grid(row=3, column=0, pady=5, sticky="ew")

# Generate Portrait Button
portrait_button = tk.Button(
    buttons_frame,
    text="Generate Portrait",
    command=lambda: threading.Thread(target=run_generate_portraits).start(),
)
portrait_button.pack(side=tk.LEFT, padx=5)

# Generate Background Button
background_button = tk.Button(
    buttons_frame,
    text="Generate Background",
    command=lambda: threading.Thread(target=run_generate_backgrounds).start(),
)
background_button.pack(side=tk.LEFT, padx=5)

# Display Latest Image Button
select_image_button = tk.Button(
    left_frame, text="Display Latest Image", command=select_latest_image
)
select_image_button.grid(row=4, column=0, pady=5, sticky="ew")

# Send Message Button
send_button = tk.Button(left_frame, text="Send", command=on_send_message_click)
send_button.grid(row=2, column=0, pady=5, sticky="ew")

start_game()
app.mainloop()
