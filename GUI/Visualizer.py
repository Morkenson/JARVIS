import math
import threading
import tkinter as tk
import customtkinter as ctk
import Output.TextToSpeech
import os
from pathlib import Path
from dotenv import load_dotenv

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def check_integration_status():
    """Check the connection status of all integrations"""
    # Load .env file
    app_dir = Path(__file__).parent.parent
    env_path = app_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    status = {}
    
    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY', '')
    status['openai'] = {
        'connected': bool(openai_key and openai_key.strip() and openai_key != 'your-openai-api-key-here'),
        'name': 'OpenAI'
    }
    
    # Check Spotify
    spotify_id = os.getenv('SPOTIPY_CLIENT_ID', '')
    spotify_secret = os.getenv('SPOTIPY_CLIENT_SECRET', '')
    spotify_cache = app_dir / '.spotify_cache'
    status['spotify'] = {
        'connected': bool(spotify_id and spotify_secret and 
                        spotify_id != 'your-spotify-client-id' and 
                        spotify_secret != 'your-spotify-client-secret' and
                        spotify_cache.exists()),
        'name': 'Spotify'
    }
    
    # Check Microsoft Calendar
    ms_client_id = os.getenv('MS_GRAPH_CLIENT_ID', '')
    ms_client_secret = os.getenv('MS_GRAPH_CLIENT_SECRET', '')
    ms_user_id = os.getenv('MS_GRAPH_USER_ID', '')
    ms_token = app_dir / 'ms_graph_api_token.json'
    status['microsoft'] = {
        'connected': bool(ms_client_id and ms_client_secret and ms_user_id and
                        ms_client_id != 'your-azure-app-client-id' and
                        ms_client_secret != 'your-azure-app-client-secret' and
                        ms_user_id != 'your-email@domain.com' and
                        ms_token.exists()),
        'name': 'Microsoft Calendar'
    }
    
    return status


def start_visualizer(speaking_event, run_in_thread=False, text_input_callback=None):
    """Start a CustomTkinter window with a circular border.

    When speaking_event is set, the bottom-right quadrant of the border
    moves inward like a 'mouth' opening/closing.
    
    Args:
        speaking_event: Event to signal when TTS is active
        run_in_thread: If True, runs in a daemon thread. If False, returns the root window for mainloop().
        text_input_callback: Callback function(text) to call when user submits text input
    
    Returns:
        The root window if run_in_thread=False, None otherwise
    """

    def create_window():
        root = ctk.CTk()
        root.title("Jarvis")
        
        # Set window background to match visualizer background
        bg_color = "#1a1a1a"
        root.configure(bg_color=bg_color)
        root.configure(fg_color=bg_color)
        
        # Allow window to be resizable and have normal controls (minimize, maximize, close)
        root.resizable(True, True)
        
        # Maximize window after it's created (Windows)
        def maximize_window():
            try:
                # Try Windows-specific maximize
                root.state('zoomed')
            except:
                # Fallback: set to screen size
                root.update_idletasks()
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.geometry(f"{width}x{height}+0+0")
        
        # Maximize after window is fully initialized
        root.after(100, maximize_window)

        # Create a frame to hold the canvas - fill entire window and center content
        canvas_frame = ctk.CTkFrame(root, fg_color="transparent")
        canvas_frame.pack(fill="both", expand=True)
        
        # Integrations dropdown menu in top left
        integrations_menu_visible = False
        
        def toggle_integrations_menu():
            """Toggle the integrations menu visibility"""
            nonlocal integrations_menu_visible
            if integrations_menu_visible:
                integrations_panel.place_forget()
                integrations_menu_visible = False
            else:
                integrations_panel.place(x=10, y=50)  # Below the button
                integrations_menu_visible = True
                refresh_integrations_status()
        
        # Integrations button (top left)
        integrations_btn = ctk.CTkButton(
            root,
            text="Integrations",
            command=toggle_integrations_menu,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray80", "gray40")
        )
        integrations_btn.place(x=10, y=10)
        
        # Integrations panel (initially hidden, positioned top left)
        integrations_panel = ctk.CTkFrame(root, width=350, height=400, fg_color=("gray20", "gray15"))
        integrations_panel.pack_propagate(False)
        # Don't pack initially - will be shown when button is clicked
        
        # Title
        title_label = ctk.CTkLabel(
            integrations_panel,
            text="Integrations",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Integration items container
        integrations_container = ctk.CTkScrollableFrame(integrations_panel, fg_color="transparent")
        integrations_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        def refresh_integrations_status():
            """Refresh and display integration status"""
            # Clear existing items
            for widget in integrations_container.winfo_children():
                widget.destroy()
            
            status = check_integration_status()
            
            # Create integration items
            for key, info in status.items():
                item_frame = ctk.CTkFrame(integrations_container, fg_color=("gray25", "gray20"))
                item_frame.pack(fill="x", pady=8, padx=5)
                
                # Name and status
                name_status_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                name_status_frame.pack(fill="x", padx=10, pady=8)
                
                name_label = ctk.CTkLabel(
                    name_status_frame,
                    text=info['name'],
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                name_label.pack(side="left")
                
                # Status indicator
                status_color = "#23d160" if info['connected'] else "#ff4444"
                status_text = "Connected" if info['connected'] else "Not Connected"
                status_label = ctk.CTkLabel(
                    name_status_frame,
                    text=status_text,
                    font=ctk.CTkFont(size=12),
                    text_color=status_color
                )
                status_label.pack(side="right")
                
                # Connect/Disconnect button
                def make_action_handler(integration_key):
                    def handler():
                        if status[integration_key]['connected']:
                            disconnect_integration(integration_key)
                        else:
                            connect_integration(integration_key)
                        refresh_integrations_status()
                    return handler
                
                action_btn = ctk.CTkButton(
                    item_frame,
                    text="Disconnect" if info['connected'] else "Connect",
                    command=make_action_handler(key),
                    width=120,
                    height=30,
                    font=ctk.CTkFont(size=12),
                    fg_color=("#ff4444", "#cc3333") if info['connected'] else ("#23d160", "#1ea850")
                )
                action_btn.pack(pady=(0, 8))
        
        def connect_integration(integration_key):
            """Connect an integration"""
            app_dir = Path(__file__).parent.parent
            env_path = app_dir / ".env"
            
            if integration_key == 'openai':
                # Open a dialog to enter OpenAI API key
                from GUI.Onboarding import start_onboarding_ui
                def on_ready():
                    pass
                # This is blocking - waits for user to save
                start_onboarding_ui(speaking_event, on_ready, test_mode=False)
                # After onboarding closes, refresh the integrations status
                if integrations_menu_visible:
                    refresh_integrations_status()
            elif integration_key == 'spotify':
                # Trigger Spotify authorization
                try:
                    import Spotify.Spotify
                    # Spotify will need to authenticate - this will open browser
                    threading.Thread(target=lambda: Spotify.Spotify.get_available_devices(), daemon=True).start()
                except Exception as e:
                    print(f"Error connecting Spotify: {e}")
            elif integration_key == 'microsoft':
                # Trigger Microsoft Calendar authorization
                try:
                    from Calendar import AccessToken
                    threading.Thread(target=lambda: AccessToken.generate_access_token(), daemon=True).start()
                except Exception as e:
                    print(f"Error connecting Microsoft Calendar: {e}")
        
        def disconnect_integration(integration_key):
            """Disconnect an integration"""
            app_dir = Path(__file__).parent.parent
            
            if integration_key == 'openai':
                # Remove OpenAI key from .env
                env_path = app_dir / ".env"
                if env_path.exists():
                    lines = env_path.read_text().splitlines()
                    new_lines = []
                    for line in lines:
                        if not line.strip().startswith('OPENAI_API_KEY='):
                            new_lines.append(line)
                    env_path.write_text("\n".join(new_lines) + "\n")
            elif integration_key == 'spotify':
                # Remove Spotify cache
                cache_path = app_dir / '.spotify_cache'
                if cache_path.exists():
                    cache_path.unlink()
            elif integration_key == 'microsoft':
                # Remove Microsoft token
                token_path = app_dir / 'ms_graph_api_token.json'
                if token_path.exists():
                    token_path.unlink()

        # Container for circle and text input (centered both horizontally and vertically)
        center_container = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Larger circle for fullscreen (increased by 25%)
        size = 500  # 400 * 1.25 = 500
        bg = "#1a1a1a"  # Slightly lighter to match CTk dark theme
        fg = "#23d160"  # green
        border_w = 19  # Scaled border for larger circle (15 * 1.25 ≈ 19)

        # Canvas for the circle - centered horizontally and vertically
        circle_container = ctk.CTkFrame(center_container, fg_color="transparent")
        circle_container.pack(pady=(0, 20))

        canvas = tk.Canvas(circle_container, width=size, height=size, bg=bg, highlightthickness=0)
        canvas.pack()

        # Button to enter text mode (below the circle, centered)
        text_mode_btn = ctk.CTkButton(
            center_container,
            text="Enter Text Mode",
            command=lambda: toggle_text_input(),
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray80", "gray40")
        )
        text_mode_btn.pack(pady=(0, 10))

        # Text input section (initially hidden, centered)
        text_input_frame = ctk.CTkFrame(center_container, fg_color="transparent")
        # Don't pack initially - will be shown when button is clicked
        
        text_var = tk.StringVar()
        text_entry = ctk.CTkEntry(
            text_input_frame,
            textvariable=text_var,
            width=500,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Type your message here..."
        )
        text_entry.pack(side="left", padx=(0, 10))

        def submit_text():
            text = text_var.get().strip()
            if text and text_input_callback:
                text_input_callback(text)
                text_var.set("")  # Clear the input after submitting
                text_entry.focus()  # Keep focus on text entry

        submit_btn = ctk.CTkButton(
            text_input_frame,
            text="Submit",
            command=submit_text,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        submit_btn.pack(side="left")

        # Bind Enter key to submit
        text_entry.bind('<Return>', lambda e: submit_text())

        # Track text input visibility
        text_input_visible = False

        def toggle_text_input():
            """Show or hide the text input section"""
            nonlocal text_input_visible
            if text_input_visible:
                text_input_frame.pack_forget()
                text_mode_btn.configure(text="Enter Text Mode")
                text_input_visible = False
            else:
                text_input_frame.pack(pady=10)
                text_mode_btn.configure(text="Hide Text Mode")
                text_input_visible = True
                text_entry.focus()  # Focus the text entry when shown

        R = (size // 2) - 19  # outer radius (adjusted for larger circle)
        mouth_max_inset = 63  # how far inward the mouth can go at peak (scaled for larger circle: 50 * 1.25 ≈ 63)
        phase = 0.0
        speaking_phase_speed = 1.25  # Animation speed when speaking
        animation_id = None  # Track animation callback ID for cleanup
        is_destroyed = False  # Track if window is being destroyed

        def animate():
            nonlocal phase, animation_id
            
            # Check if window is being destroyed
            try:
                if is_destroyed or not root.winfo_exists():
                    return
            except:
                return
            
            # Skip animation if window is minimized
            try:
                if root.state() == 'iconic':  # Window is minimized
                    if not is_destroyed:
                        animation_id = root.after(100, animate)  # Check less frequently when minimized
                    return
            except:
                pass  # Some platforms don't support state()
            
            try:
                canvas.delete("all")

                cx = cy = size // 2

                # Animate at consistent speed while speaking
                if speaking_event.is_set():
                    phase += speaking_phase_speed
                    inset = (0.5 + 0.5 * math.sin(phase)) * mouth_max_inset
                else:
                    inset = 0

                # Draw circle as a continuous path that curves inward in bottom-right quadrant
                # Calculate points along the circle, curving inward for the "mouth" section
                points = []
                num_points = 360  # One point per degree for smooth curve
                
                # Mouth section: bottom-right quadrant (315° to 45°)
                mouth_start_angle = 315  # degrees
                mouth_end_angle = 45  # degrees (wraps around)
                mouth_span = 90  # degrees
                
                for i in range(num_points):
                    angle_deg = (i / num_points) * 360
                    angle_rad = math.radians(angle_deg)
                    
                    # Determine if we're in the mouth section
                    # Handle wrap-around: 315° to 360° and 0° to 45°
                    in_mouth = False
                    if angle_deg >= mouth_start_angle or angle_deg <= mouth_end_angle:
                        in_mouth = True
                        # Calculate how far into the mouth section we are (0 to 1)
                        if angle_deg >= mouth_start_angle:
                            mouth_progress = (angle_deg - mouth_start_angle) / mouth_span
                        else:
                            mouth_progress = (angle_deg + (360 - mouth_start_angle)) / mouth_span
                        
                        # Create smooth curve using sine wave for natural transition
                        curve_factor = math.sin(mouth_progress * math.pi)
                        current_inset = inset * curve_factor
                    else:
                        current_inset = 0
                    
                    # Calculate radius at this angle
                    current_radius = R - current_inset
                    
                    # Calculate point on circle
                    x = cx + current_radius * math.cos(angle_rad)
                    y = cy + current_radius * math.sin(angle_rad)
                    points.append((x, y))
                
                # Draw the circle as a smooth continuous line (single line with all points)
                if len(points) > 1:
                    # Flatten points list for create_line (x1, y1, x2, y2, ...)
                    flat_points = []
                    for point in points:
                        flat_points.extend(point)
                    # Close the circle by adding first point at the end
                    flat_points.extend(points[0])
                    
                    # Draw as single smooth line for better performance
                    canvas.create_line(
                        *flat_points,
                        fill=fg, width=border_w, smooth=True, 
                        capstyle=tk.ROUND, joinstyle=tk.ROUND, splinesteps=36
                    )

                # Schedule next frame only if window still exists
                if not is_destroyed:
                    animation_id = root.after(33, animate)  # ~30 FPS
            except tk.TclError:
                # Window was destroyed, stop animation
                pass

        def on_closing():
            """Handle window closing - cancel animation callbacks"""
            nonlocal is_destroyed, animation_id
            is_destroyed = True
            if animation_id:
                try:
                    root.after_cancel(animation_id)
                except:
                    pass
            root.destroy()

        # Bind close event
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start animation
        animation_id = root.after(0, animate)
        return root

    if run_in_thread:
        def run():
            root = create_window()
            root.mainloop()
        threading.Thread(target=run, daemon=True).start()
        return None
    else:
        return create_window()