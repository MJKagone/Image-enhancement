import tkinter as tk
from ImageProcessing import ImageProcessing

def main():

    window = tk.Tk()
    window.title("Image enhancement")
    frame = tk.Frame()
    frame.pack()
    frame2 = tk.Frame()
    frame2.pack()
    frame2.config(width=1080, height=720)
    frame2.pack_propagate(False)
    ip = ImageProcessing()

    button1 = tk.Button(
        text="Load image",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.display_image(ip.get_image(), frame2)
    )
    button1.pack(side=tk.LEFT)

    button2 = tk.Button(
        text="Reset",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.reset(frame2)
    )
    button2.pack(side=tk.LEFT)

    button3 = tk.Button(
        text="Enhance contrast",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.enhance_contrast(ip.working_image, frame2)
    )
    button3.pack(side=tk.LEFT)

    button4 = tk.Button(
        text="White balance",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.white_balance(ip.working_image, frame2)
    )
    button4.pack(side=tk.LEFT)

    button5 = tk.Button(
        text="Unsharp filter",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.sharpen(ip.working_image, frame2)
    )
    button5.pack(side=tk.LEFT)

    button6 = tk.Button(
        text="Median filter",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.smoothen(ip.working_image, frame2)
    )
    button6.pack(side=tk.LEFT)

    button7 = tk.Button(
        text="Denoise",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.denoise(ip.working_image, frame2)
    )
    button7.pack(side=tk.LEFT)

    button8 = tk.Button(
        text="Inpaint",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.open_mask_drawing_window(frame2)
    )
    button8.pack(side=tk.LEFT)

    button9 = tk.Button(
        text="Save image",
        width=15,
        height=5,
        master=frame,
        command=lambda: ip.save_image()
    )
    button9.pack(side=tk.LEFT)

    window.mainloop()

main()