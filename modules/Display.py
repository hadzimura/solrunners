#!/usr/bin/env python3
# coding=utf-8

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


class PiLED(object):

    def __init__(self):


        # Initialize OLED display dimensions
        WIDTH = 128
        HEIGHT = 32

        # Set up I2C communication with the OLED display
        i2c = board.I2C()  # Utilizes board's SCL and SDA pins
        self.oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

        # Clear the OLED display
        self.oled.fill(0)
        self.oled.show()


        # Load the default font for text
        self.font = ImageFont.load_default()


    def paint(self):

        # Draw a filled white rectangle as the background
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)

        # Define border size for an inner rectangle
        BORDER = 5
        # Draw a smaller black rectangle inside the larger one
        self.draw.rectangle(
            (BORDER, BORDER, self.oled.width - BORDER - 1, self.oled.height - BORDER - 1),
            outline=0,
            fill=0,
        )

    def print(self, text):

        # Create a new image with 1-bit color for drawing
        image = Image.new("1", (self.oled.width, self.oled.height))


        # Obtain a drawing object to manipulate the image
        draw = ImageDraw.Draw(image)

        # Draw a filled white rectangle as the background
        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)

        # Define border size for an inner rectangle
        BORDER = 5
        # Draw a smaller black rectangle inside the larger one
        draw.rectangle(
            (BORDER, BORDER, self.oled.width - BORDER - 1, self.oled.height - BORDER - 1),
            outline=0,
            fill=0,
        )

        # Get the width and height of the text in pixels
        (font_width, font_height) = self.getfontsize(text)
        # Draw the text, centered on the display
        draw.text(
            (self.oled.width // 2 - font_width // 2, self.oled.height // 2 - font_height // 2),
            text,
            font=self.font,
            fill=255,
        )

        self.oled.image(image)
        self.oled.show()


    def getfontsize(self, text):
        # Calculate the size of the text in pixels
        left, top, right, bottom = self.font.getbbox(text)
        return right - left, bottom - top

    def out_print(self):

        # Send the image to the OLED display
        self.oled.fill(0)
        self.oled.show()
