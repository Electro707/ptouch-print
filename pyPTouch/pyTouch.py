"""
A wrapper around libptouch, allowing easy usage thru Python
"""
# import the swig generated file
from pyPTouch.ptouchSwig import *
from PIL import Image
from enum import Enum


class PTouchConnection(Exception):
    """Raised when a connection error occured with a Ptouch device"""


class PTouch:
    def __init__(self):
        self.dev = ptouch_devP()
        print(self.dev)

    def open(self):
        """
        Connects and initializes a PTouch label maker
        """
        if ptouch_open(self.dev) != 0:
            raise PTouchConnection()
        try:
            if ptouch_init(self.dev) != 0:
                raise PTouchConnection()
            # needed to get printer information, such as tape lenght, etc
            if ptouch_getstatus(self.dev) != 0:
                raise PTouchConnection()
        except PTouchConnection:
            self.close()
            raise

    def close(self):
        return ptouch_close(self.dev)

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_tape_width_px(self) -> int:
        """Returns the current tape with in pixels"""
        return ptouch_get_tape_width(self.dev)

    def get_printhead_width(self) -> int:
        """Returns the maximum tape head in pixels"""
        return ptouch_get_max_width(self.dev)

    def print_raster_img(self, img_path: str, resize: bool = True, eject: bool = True):
        """
        Prints any raster image, as long as Pillow can open it. Preferable JPEG or PNG

        Args:
            img_path: The image path
            resize: Whether to resize the image into the correct tape width
            eject: Whether to eject the label after printing, or not for chain printing
        """
        im = Image.open(img_path)
        set_h = self.get_tape_width_px()
        bytes_buff = buffer(16)     # Make a uint8_t buffer

        im = im.convert('1')
        if resize:
            im = im.resize((int(im.width / im.height * set_h), set_h), resample=Image.Resampling.LANCZOS)
        else:
            if im.height > self.get_tape_width_px():
                raise UserWarning("Image height is greater than the tape width!")

        image_offset = (self.get_printhead_width() - set_h) // 2

        ptouch_rasterstart(self.dev)

        for col in range(im.width):
            # Clear buffer
            for i in range(16):
                bytes_buff[i] = 0

            for i in range(im.height):
                pc = im.getpixel((col, im.height-i-1))
                if pc == 0:
                    buffer_x = (i+image_offset)
                    bytes_buff[15 - (buffer_x // 8)] |= 1 << (buffer_x % 8)
            ptouch_sendraster(self.dev, bytes_buff.cast(), 16)

        if eject:
            ptouch_eject(self.dev)
        else:
            ptouch_ff(self.dev)
        im.close()

    def print_pdf(self, pdf_path: str):
        """
        Prints a PDF on the label, handling the conversion to an image
        """
        # todo: this
        raise NotImplementedError

    def get_status(self):
        ptouch_read_status(self.dev, 0)
        return self.dev.value()

    def wait_for_print(self):
        """
        This function HANGS until the print is finished
        """
        ptouch_read_status(self.dev)
        # todo: error check above


    def send_bytes(self, data: bytes):
        """
        Sends some bytes directly to the PTouch device. This is a low-level function
        """
        b = buffer(len(data))
        for i in range(len(data)):
            b[i] = data[i]
        ptouch_send(self.dev, b.cast(), len(data))

