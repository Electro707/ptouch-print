"""
A wrapper around libptouch, allowing easy usage thru Python
"""
# import the swig generated file
from pyTouch.ptouchSwig import *
from PIL import Image
from enum import Enum


class PTouchConnection(Exception):
    """Raised when a connection error occured with a Ptouch device"""


class PTouch:
    def __init__(self):
        self.dev = ptouch_dev()

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

    def get_tape_width_px(self) -> int:
        """Returns the current tape with in pixels"""
        return ptouch_get_tape_width(self.dev)

    def get_printhead_width(self) -> int:
        return ptouch_get_max_width(self.dev)

    def close(self):
        return ptouch_close(self.dev)

    def print_png(self, png_path: str, resize: bool = True, eject: bool = True):
        if not png_path.endswith('.png'):
            raise ValueError("Path given is not a png image")
        im = Image.open(png_path)
        set_h = self.get_tape_width_px()
        bytes_buff = buffer(16)

        im = im.convert('1')
        if resize:
            print(im.width, im.height)
            im = im.resize((int(im.width / im.height * set_h), set_h), resample=Image.Resampling.LANCZOS)

        image_offset = (self.get_printhead_width() - set_h) // 2

        im.save(png_path+'2.png')

        ptouch_rasterstart(self.dev)

        for col in range(im.width):
            for i in range(16):
                bytes_buff[i] = 0

            for i in range(im.height):
                pc = im.getpixel((col, im.height-i-1))
                if pc == 0:
                    buffer_x = (i+image_offset)
                    bytes_buff[15 - (buffer_x // 8)] |= 1 << (buffer_x % 8)
                    print(buffer_x % 8, ' ', end='')
            print([bin(bytes_buff[i]) for i in range(16)])
            ptouch_sendraster(self.dev, bytes_buff.cast(), 16)

        if eject:
            ptouch_eject(self.dev)
        else:
            ptouch_ff(self.dev)
        im.close()

    def print_pdf(self, pdf_path: str):
        # todo: this
        raise NotImplementedError

