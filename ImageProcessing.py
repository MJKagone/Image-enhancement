import cv2
import numpy as np
import tkinter as tk
from skimage import exposure
from tkinter import filedialog
from skimage.filters import unsharp_mask
from PIL import Image, ImageTk

class ImageProcessing:

    def __init__(self):
        self.original_image = None
        self.file_path = ""
        self.working_image = None
    
    def scale_image(self, image):

        def scale_width(image):
            scale = 1280 / image.size[0]
            return image.resize((1280, int(image.size[1] * scale)))
        
        def scale_height(image):
            scale = 720 / image.size[1]
            return image.resize((int(image.size[0] * scale), 720))
        
        if image.size[0] > 1280:
            image = scale_width(image)
        if image.size[1] > 720:
            image = scale_height(image)
            
        return image

    def get_image(self):
        file_path = filedialog.askopenfilename()
        img = Image.open(file_path)
        if img.size[0] > 1280 or img.size[1] > 720:
            img = self.scale_image(img)
        self.original_image = img
        self.working_image = img
        return img

    def reset(self, frame):
        self.working_image = self.original_image
        self.display_image(self.original_image, frame)

    def display_image(self, img, frame):
        self.clear_frame(frame)
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(frame, image=img_tk)
        label.image = img_tk
        label.pack(side=tk.BOTTOM)
        # Center the image
        label.pack(expand=True, anchor=tk.CENTER)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def enhance_contrast(self, image, frame):
        image = np.array(image)
        p1, p99 = np.percentile(image, (1,99))
        image_rescaled = exposure.rescale_intensity(image, in_range=(p1, p99))
        image_rescaled = Image.fromarray(image_rescaled)
        self.working_image = image_rescaled
        self.display_image(image_rescaled, frame)
        return image_rescaled
    
    def white_balance(self, image, frame):
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        result = cv2.xphoto.createSimpleWB()
        result.setP(0.5)
        image = result.balanceWhite(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.working_image = image
        self.display_image(image, frame)
        return image

    def smoothen(self, image, frame):
        image = np.array(image)
        image = cv2.medianBlur(image, 3)
        image = Image.fromarray(image.astype(np.uint8))
        self.working_image = image
        self.display_image(image, frame)

    def denoise(self, image, frame):
        # Use Non-local Means Denoising algorithm from cv2
        image = np.array(image)
        denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 5, 5, 7, 21) # 5, 5 -> 10, 10 for stronger effect
        denoised_image = Image.fromarray(denoised_image)
        self.working_image = denoised_image
        self.display_image(denoised_image, frame)
        return denoised_image

    def sharpen(self, image, frame, k=1):

        image = np.array(image)
        
        if image.ndim == 2:  # Grayscale image
            sharpened_image = unsharp_mask(image, radius=5, amount=k)
            sharpened_image = (sharpened_image * 255).astype(np.uint8)
            image = sharpened_image

        elif image.ndim == 3:  # Color image
            # Convert to HSV color space
            image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            v_channel = image_hsv[:, :, 2]
            
            # Apply the sharpening to the V channel
            sharpened_v_channel = unsharp_mask(v_channel, radius=1, amount=2)
            sharpened_v_channel = (sharpened_v_channel * 255).astype(np.uint8)  # Scale back to [0, 255]
            image_hsv[:, :, 2] = sharpened_v_channel

            # Convert back to RGB color space
            image = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2RGB)

        image = Image.fromarray(image.astype(np.uint8))
        self.working_image = image
        self.display_image(image, frame)
        return image

    def inpaint(self, image, mask, frame):
        image = np.array(image)

        if image.ndim == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        mask = np.array(mask)
        mask = mask.astype(np.uint8)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

        inpainted_image = cv2.inpaint(image, mask, 3, cv2.INPAINT_NS)
        inpainted_image = Image.fromarray(inpainted_image)
        self.working_image = inpainted_image
        self.display_image(inpainted_image, frame)

    def open_mask_drawing_window(self, frame):
        mask_window = tk.Toplevel()
        mask_window.title("Draw mask")

        canvas = tk.Canvas(mask_window, width=self.working_image.width, height=self.working_image.height)
        canvas.pack()

        # Convert the working image to a format that can be displayed on the canvas
        img_tk = ImageTk.PhotoImage(self.working_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk  # Keep a reference to avoid garbage collection

        mask = np.zeros((self.working_image.height, self.working_image.width), dtype=np.uint8)

        def draw_mask(event):
                x, y = event.x, event.y
                radius = 7  # Radius of the circular brush
                for i in range(-radius, radius + 1):
                    for j in range(-radius, radius + 1):
                        if i**2 + j**2 <= radius**2:  # Check if the point is within the circle
                            if 0 <= x + i < mask.shape[1] and 0 <= y + j < mask.shape[0]:
                                mask[y + j, x + i] = 255
                                canvas.create_rectangle(x + i, y + j, x + i + 1, y + j + 1, fill="white", outline="white")

        canvas.bind("<B1-Motion>", draw_mask)

        def apply_inpainting():
            mask_window.destroy()
            self.inpaint(self.working_image, mask, frame)

        apply_button = tk.Button(
            mask_window,
            text="Apply",
            width=20,
            height=2,
            command=apply_inpainting
        )
        apply_button.pack()

        # Add just a little bit of empty space at the bottom
        mask_window.geometry(f"{self.working_image.width}x{self.working_image.height + 50}")

        mask_window.mainloop()
    
    def save_image(self):
        self.working_image.save(self.file_path.join("_enhanced.jpg"))
        