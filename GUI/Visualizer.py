import math
import threading
import tkinter as tk


def start_visualizer(speaking_event):
    """Start a Tkinter window with a circular border.

    When speaking_event is set, the bottom-right quadrant of the border
    moves inward like a 'mouth' opening/closing.
    """

    def run():
        root = tk.Tk()
        root.title("Jarvis")
        root.resizable(False, False)

        size = 240
        bg = "#0f0f0f"
        fg = "#23d160"  # green
        border_w = 10

        canvas = tk.Canvas(root, width=size, height=size, bg=bg, highlightthickness=0)
        canvas.pack()

        R = (size // 2) - 12  # outer radius
        mouth_max_inset = 30  # how far inward the mouth can go at peak
        phase = 0.0

        def animate():
            nonlocal phase
            canvas.delete("all")

            cx = cy = size // 2

            # Base circle border
            canvas.create_oval(
                cx - R, cy - R, cx + R, cy + R,
                outline=fg, width=border_w
            )

            # Animate mouth inset only when speaking
            if speaking_event.is_set():
                phase += 0.20
                inset = (0.5 + 0.5 * math.sin(phase)) * mouth_max_inset
            else:
                inset = 0

            # Erase the outer bottom-right quadrant of the border
            # Draw an arc on the base circle using background color to "cut out" that segment
            canvas.create_arc(
                cx - R, cy - R, cx + R, cy + R,
                start=315, extent=90, style=tk.ARC,
                outline=bg, width=border_w + 2
            )

            # Draw the mouth arc inward by 'inset' (smaller radius)
            r2 = R - inset
            if r2 > border_w:  # keep visible
                canvas.create_arc(
                    cx - r2, cy - r2, cx + r2, cy + r2,
                    start=315, extent=90, style=tk.ARC,
                    outline=fg, width=border_w
                )

            root.after(33, animate)  # ~30 FPS

        root.after(0, animate)
        root.mainloop()

    threading.Thread(target=run, daemon=True).start()