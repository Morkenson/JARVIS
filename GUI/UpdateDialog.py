import customtkinter as ctk
import threading

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def show_update_dialog(current_version, latest_version, release_notes=""):
    """Show a dialog notifying the user about an available update
    
    Returns:
        True if user wants to update now, False otherwise
    """
    result = {'update_now': False}
    
    def on_update_now():
        result['update_now'] = True
        dialog.destroy()
    
    def on_update_later():
        result['update_now'] = False
        dialog.destroy()
    
    dialog = ctk.CTk()
    dialog.title("Update Available")
    dialog.geometry("500x300")
    dialog.resizable(False, False)
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (300 // 2)
    dialog.geometry(f"500x300+{x}+{y}")
    
    # Make dialog appear on top
    dialog.attributes('-topmost', True)
    dialog.focus()
    
    # Title
    title = ctk.CTkLabel(
        dialog,
        text="Update Available",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=(20, 10))
    
    # Version info
    version_text = f"Current version: {current_version}\nLatest version: {latest_version}"
    version_label = ctk.CTkLabel(
        dialog,
        text=version_text,
        font=ctk.CTkFont(size=14)
    )
    version_label.pack(pady=10)
    
    # Message
    message = ctk.CTkLabel(
        dialog,
        text="A new version of Jarvis is available.\nWould you like to update now?",
        font=ctk.CTkFont(size=13),
        text_color=("gray70", "gray40")
    )
    message.pack(pady=10)
    
    # Buttons
    buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons_frame.pack(pady=20)
    
    update_btn = ctk.CTkButton(
        buttons_frame,
        text="Update Now",
        command=on_update_now,
        width=150,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    update_btn.pack(side="left", padx=10)
    
    later_btn = ctk.CTkButton(
        buttons_frame,
        text="Update Later",
        command=on_update_later,
        width=150,
        height=40,
        font=ctk.CTkFont(size=14),
        fg_color="transparent",
        text_color=("gray70", "gray40"),
        hover_color=("gray80", "gray30"),
        border_width=1,
        border_color=("gray60", "gray50")
    )
    later_btn.pack(side="left", padx=10)
    
    # Run dialog
    dialog.mainloop()
    
    return result['update_now']

