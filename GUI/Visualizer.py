import math
import threading
import tkinter as tk
import customtkinter as ctk
import Output.TextToSpeech

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


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

        def animate():
            nonlocal phase
            
            # Skip animation if window is minimized
            try:
                if root.state() == 'iconic':  # Window is minimized
                    root.after(100, animate)  # Check less frequently when minimized
                    return
            except:
                pass  # Some platforms don't support state()
            
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

            root.after(33, animate)  # ~30 FPS

        root.after(0, animate)
        return root

    if run_in_thread:
        def run():
            root = create_window()
            root.mainloop()
        threading.Thread(target=run, daemon=True).start()
        return None
    else:
        return create_window()