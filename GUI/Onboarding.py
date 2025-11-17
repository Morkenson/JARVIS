import os
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pathlib import Path

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def start_onboarding_async(speaking_event) -> threading.Event:
    """Start onboarding in a persistent GUI with the Jarvis circle.

    Returns a threading.Event that is set once configuration is saved.
    The window remains open; the right panel collapses to a simple status and the circle stays.
    """
    completed_event = threading.Event()

    root = tk.Tk()
    root.title("Jarvis")
    root.geometry("740x360")
    root.configure(bg="#0f0f0f")
    root.resizable(False, False)

    # Left: Jarvis circle
    canvas_size = 260
    circle = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="#0f0f0f", highlightthickness=0)
    circle.grid(row=0, column=0, rowspan=10, padx=16, pady=16)

    fg = "#23d160"
    bg = "#0f0f0f"
    border_w = 10
    R = (canvas_size // 2) - 12
    phase = {"v": 0.0}
    mouth_max_inset = 30

    def animate():
        circle.delete("all")
        cx = cy = canvas_size // 2
        circle.create_oval(cx - R, cy - R, cx + R, cy + R, outline=fg, width=border_w)
        inset = 0
        if speaking_event.is_set():
            phase["v"] += 0.20
            inset = (0.5 + 0.5 * __import__("math").sin(phase["v"])) * mouth_max_inset
        circle.create_arc(cx - R, cy - R, cx + R, cy + R, start=315, extent=90, style=tk.ARC, outline=bg, width=border_w + 2)
        r2 = R - inset
        if r2 > border_w:
            circle.create_arc(cx - r2, cy - r2, cx + r2, cy + r2, start=315, extent=90, style=tk.ARC, outline=fg, width=border_w)
        root.after(33, animate)

    # Right: setup panel
    panel = ttk.Frame(root)
    panel.grid(row=0, column=1, padx=16, pady=16, sticky="nsew")
    panel.columnconfigure(1, weight=1)

    ttk.Label(panel, text="Welcome to Jarvis", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

    ttk.Label(panel, text="OpenAI API Key").grid(row=1, column=0, sticky="w")
    openai_var = tk.StringVar()
    ttk.Entry(panel, textvariable=openai_var, width=40, show="*").grid(row=1, column=1, sticky="ew", padx=(6, 0))

    def test_openai():
        key = openai_var.get().strip()
        if not key:
            messagebox.showwarning("OpenAI", "Please enter an API key.")
            return
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "ping"}], max_tokens=1)
            messagebox.showinfo("OpenAI", "API key looks valid.")
        except Exception as e:
            messagebox.showerror("OpenAI", f"Validation failed:\n{e}")

    ttk.Button(panel, text="Validate", command=lambda: threading.Thread(target=test_openai, daemon=True).start()).grid(row=1, column=2, padx=6)

    sep = ttk.Separator(panel, orient="horizontal")
    sep.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

    ttk.Label(panel, text="Optional: Pre-authorize services").grid(row=3, column=0, sticky="w")

    def auth_ms():
        def worker():
            try:
                from Calendar import AccessToken
                AccessToken.generate_access_token()
                messagebox.showinfo("Microsoft", "Authorization flow completed (or cached).")
            except Exception as e:
                messagebox.showerror("Microsoft", f"Authorization failed:\n{e}")
        threading.Thread(target=worker, daemon=True).start()

    def auth_spotify():
        def worker():
            try:
                from Spotify import Spotify
                Spotify.list_devices()
                messagebox.showinfo("Spotify", "Authorization may have opened in your browser. Complete it and return.")
            except Exception as e:
                messagebox.showerror("Spotify", f"Authorization trigger failed:\n{e}")
        threading.Thread(target=worker, daemon=True).start()

    ttk.Button(panel, text="Authorize Microsoft", command=auth_ms).grid(row=4, column=0, sticky="w", pady=(6, 0))
    ttk.Button(panel, text="Authorize Spotify", command=auth_spotify).grid(row=4, column=1, sticky="w", pady=(6, 0))

    def save_and_continue():
        key = openai_var.get().strip()
        if not key:
            messagebox.showwarning("Setup", "OpenAI API key is required.")
            return

        # Save to .env
        app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        env_path = app_dir / ".env"
        existing = {}
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()
        existing["OPENAI_API_KEY"] = key
        env_path.write_text("\n".join(f"{k}={v}" for k, v in existing.items()) + "\n")

        # Transform panel into a small status
        for w in panel.winfo_children():
            w.destroy()
        ttk.Label(panel, text="Jarvis is ready.", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
        completed_event.set()

    buttons = ttk.Frame(panel)
    buttons.grid(row=5, column=0, columnspan=3, sticky="e", pady=(16, 0))
    ttk.Button(buttons, text="Save & Continue", command=save_and_continue).pack(side="right", padx=6)

    # Run UI
    animate()
    threading.Thread(target=root.mainloop, daemon=True).start()
    return completed_event


def start_onboarding_ui(speaking_event, on_ready, test_mode=False) -> None:
    """Run onboarding UI on the main thread.

    Shows the setup form for configuring Jarvis.
    After saving, closes the window and invokes on_ready() to continue startup.
    The visualizer will appear as a separate window after onboarding closes.
    
    Args:
        speaking_event: Event to signal when TTS is active (not used in onboarding, but kept for API compatibility)
        on_ready: Callback when setup is complete
        test_mode: If True, don't actually save to .env file
    """
    root = ctk.CTk()
    root.title("Jarvis Setup")
    root.geometry("600x500")
    root.resizable(False, False)

    # Main container - just the setup panel (no circle)
    main_container = ctk.CTkFrame(root, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=40, pady=40)

    # Setup panel (centered, no circle)
    panel = ctk.CTkFrame(main_container)
    panel.pack(fill="both", expand=True)

    title_text = "Welcome to Jarvis" + (" (Test Mode)" if test_mode else "")
    title_label = ctk.CTkLabel(panel, text=title_text, font=ctk.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=(20, 10), anchor="w", padx=20)

    # OpenAI API Key section
    key_frame = ctk.CTkFrame(panel, fg_color="transparent")
    key_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(key_frame, text="OpenAI API Key", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
    
    input_frame = ctk.CTkFrame(key_frame, fg_color="transparent")
    input_frame.pack(fill="x")
    
    openai_var = tk.StringVar()
    openai_entry = ctk.CTkEntry(input_frame, textvariable=openai_var, width=300, show="*", font=ctk.CTkFont(size=12))
    openai_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def test_openai():
        key = openai_var.get().strip()
        if not key:
            messagebox.showwarning("OpenAI", "Please enter an API key.")
            return
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "ping"}], max_tokens=1)
            messagebox.showinfo("OpenAI", "API key looks valid.")
        except Exception as e:
            messagebox.showerror("OpenAI", f"Validation failed:\n{e}")

    validate_btn = ctk.CTkButton(input_frame, text="Validate", command=lambda: threading.Thread(target=test_openai, daemon=True).start(), width=100)
    validate_btn.pack(side="right")

    def save_and_continue():
        key = openai_var.get().strip()
        if not key:
            messagebox.showwarning("Setup", "OpenAI API key is required.")
            return
        
        if test_mode:
            # Test mode: don't save, just show a message
            messagebox.showinfo("Test Mode", "Test mode enabled - no changes were saved to .env")
        else:
            # Save to .env
            app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            env_path = app_dir / ".env"
            existing = {}
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.split("=", 1)
                        existing[k.strip()] = v.strip()
            existing["OPENAI_API_KEY"] = key
            env_path.write_text("\n".join(f"{k}={v}" for k, v in existing.items()) + "\n")

        # Call the ready callback first
        try:
            on_ready()
        except Exception:
            pass
        
        # Close the onboarding window after a brief delay to allow callback to execute
        root.after(100, root.destroy)

    def skip_for_now():
        """Skip setup and continue without saving API key"""
        # Call the ready callback to start backend
        try:
            on_ready()
        except Exception:
            pass
        # Close the onboarding window
        root.after(100, root.destroy)

    # Buttons frame
    buttons_frame = ctk.CTkFrame(panel, fg_color="transparent")
    buttons_frame.pack(pady=20)

    # Save button
    save_btn = ctk.CTkButton(buttons_frame, text="Save & Continue", command=save_and_continue, width=200, height=40, font=ctk.CTkFont(size=14, weight="bold"))
    save_btn.pack(pady=(0, 10))

    # Skip button (different color - gray/transparent style)
    skip_btn = ctk.CTkButton(buttons_frame, text="Skip for now", command=skip_for_now, width=200, height=35, 
                             font=ctk.CTkFont(size=13), fg_color="transparent", 
                             text_color=("gray70", "gray40"), hover_color=("gray80", "gray30"),
                             border_width=1, border_color=("gray60", "gray50"))
    skip_btn.pack()

    root.mainloop()


def start_onboarding(speaking_event) -> bool:
    """GUI onboarding prompt for OpenAI key only. Returns True if saved."""

    result = {"completed": False}

    root = tk.Tk()
    root.title("Jarvis Setup")
    root.geometry("520x220")
    root.configure(bg="#0f0f0f")
    root.resizable(False, False)

    # Simple form (no circle here; visualizer appears after setup)
    container = ttk.Frame(root)
    container.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")

    for i in range(3):
        container.rowconfigure(i, weight=1)
    container.columnconfigure(1, weight=1)

    title = ttk.Label(container, text="Welcome to Jarvis", font=("Segoe UI", 14, "bold"))
    title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

    ttk.Label(container, text="OpenAI API Key").grid(row=1, column=0, sticky="w")
    openai_var = tk.StringVar()
    openai_entry = ttk.Entry(container, textvariable=openai_var, width=40, show="*")
    openai_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

    def test_openai():
        key = openai_var.get().strip()
        if not key:
            messagebox.showwarning("OpenAI", "Please enter an API key.")
            return
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "ping"}], max_tokens=1)
            messagebox.showinfo("OpenAI", "API key looks valid.")
        except Exception as e:
            messagebox.showerror("OpenAI", f"Validation failed:\n{e}")

    ttk.Button(container, text="Validate", command=lambda: threading.Thread(target=test_openai, daemon=True).start()).grid(row=1, column=2, padx=6)

    # Note: Porcupine and Google TTS are bundled in the build, so we do not prompt for them here.
    # Advanced controls can be added later if you want users to override bundled credentials.

    # Optional cloud auth triggers
    sep = ttk.Separator(container, orient="horizontal")
    sep.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

    ttk.Label(container, text="Optional: Pre-authorize services").grid(row=3, column=0, sticky="w")

    def auth_ms():
        def worker():
            try:
                from Calendar import AccessToken
                AccessToken.generate_access_token()
                messagebox.showinfo("Microsoft", "Authorization flow completed (or cached).")
            except Exception as e:
                messagebox.showerror("Microsoft", f"Authorization failed:\n{e}")
        threading.Thread(target=worker, daemon=True).start()

    def auth_spotify():
        def worker():
            try:
                from Spotify import Spotify
                # Trigger auth by trying to list devices (or any call)
                Spotify.list_devices()
                messagebox.showinfo("Spotify", "Authorization may have opened in your browser. Complete it and return.")
            except Exception as e:
                messagebox.showerror("Spotify", f"Authorization trigger failed:\n{e}")
        threading.Thread(target=worker, daemon=True).start()

    ttk.Button(container, text="Authorize Microsoft", command=auth_ms).grid(row=4, column=0, sticky="w", pady=(6, 0))
    ttk.Button(container, text="Authorize Spotify", command=auth_spotify).grid(row=4, column=1, sticky="w", pady=(6, 0))

    # Actions
    def save_and_close():
        key = openai_var.get().strip()

        if not key:
            messagebox.showwarning("Setup", "OpenAI API key is required.")
            return

        # Compose .env content (update existing if present)
        app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        env_path = app_dir / ".env"

        existing = {}
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

        existing["OPENAI_API_KEY"] = key

        # Build content
        content_lines = [f"{k}={v}" for k, v in existing.items()]
        env_path.write_text("\n".join(content_lines) + "\n")

        # Google TTS and Porcupine are bundled; nothing else to copy here.

        result["completed"] = True
        root.destroy()

    buttons = ttk.Frame(container)
    buttons.grid(row=5, column=0, columnspan=3, sticky="e", pady=(16, 0))

    ttk.Button(buttons, text="Skip", command=lambda: (root.destroy())).pack(side="right", padx=6)
    ttk.Button(buttons, text="Save & Finish", command=save_and_close).pack(side="right", padx=6)

    # Show window
    root.mainloop()

    return result["completed"]

