"""
A wrapper around libptouch, allowing easy usage thru Python
"""
import typing
import io
# import the swig generated file
from pyPTouch.ptouchSwig import *
from PIL import Image
from enum import Enum
import pdf2image
import cairosvg

class PTouchConnection(Exception):
    """Raised when a connection error occured with a Ptouch device"""


class PTouch:
    def __init__(self):
        self.dev = None  # gets assigned later when we have memory allocated by ptouch_open

    def open(self):
        """
        Connects and initializes a PTouch label maker
        """
        tmp_dev = new_ptouch_devPP()  # create pointer of a pointer of a struct
        if ptouch_open(tmp_dev) != 0:
            raise PTouchConnection()
        self.dev = ptouch_devPP_value(tmp_dev)
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
        r = ptouch_close(self.dev)
        delete_ptouch_devP(self.dev)
        return r

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def is_printer_available() -> bool:
        ret = ptouch_printer_available()
        if ret == 1:
            return True
        return False

    def get_tape_width_px(self) -> int:
        """Returns the current tape with in pixels"""
        return ptouch_get_tape_width(self.dev)

    def get_printhead_width(self) -> int:
        """Returns the maximum tape head in pixels"""
        return ptouch_get_max_width(self.dev)

    def get_printhead_width_mm(self) -> int:
        """Returns the maximum tape head in millimeters"""
        ptouch_getstatus(self.dev)
        return self.dev.status.media_width

    def print_raster_img(self, img: typing.Union[str, Image.Image], resize: bool = True, eject: bool = True):
        """
        Prints any raster image, as long as Pillow can open it. Preferable JPEG or PNG

        Args:
            img: The image path, or a Pillow Image object
            resize: Whether to resize the image into the correct tape width
            eject: Whether to eject the label after printing, or not for chain printing
        """
        if type(img) is str:
            im = Image.open(img)
        else:
            im = img
        set_h = self.get_tape_width_px()
        bytes_buff = buffer(16)  # Make a uint8_t buffer

        if resize:
            im = im.resize((int(im.width / im.height * set_h), set_h), resample=Image.Resampling.LANCZOS)
        else:
            if im.height > self.get_tape_width_px():
                raise UserWarning("Image height is greater than the tape width!")
        im = im.convert('1', dither=Image.Dither.NONE)

        image_offset = (self.get_printhead_width() - set_h) // 2

        ptouch_rasterstart(self.dev)

        for col in range(im.width):
            # print('col: ', col, 'data', ','.join([str(im.getpixel((col, im.height - i - 1))) for i in range(im.height)]))
            # Clear buffer
            for i in range(16):
                bytes_buff[i] = 0

            for i in range(im.height):
                pc = im.getpixel((col, im.height - i - 1))
                if pc == 0:
                    buffer_x = (i + image_offset)
                    bytes_buff[15 - (buffer_x // 8)] |= 1 << (buffer_x % 8)
            ptouch_sendraster(self.dev, bytes_buff.cast(), 16)

        if eject:
            ptouch_eject(self.dev)
        else:
            ptouch_ff(self.dev)
        im.close()

    def print_pdf(self, pdf_path: typing.Union[str, bytes], eject_at_end: bool = True):
        """
        Prints a PDF on the label, handling the conversion to an image
        Handles multiple pages

        work in progress????
        """
        set_h = self.get_tape_width_px()
        if type(pdf_path) is bytes:
            imgs = pdf2image.convert_from_bytes(pdf_path, size=(None, set_h))
        else:
            imgs = pdf2image.convert_from_path(pdf_path, size=(None, set_h))
        for i, img in enumerate(imgs):
            eject = False
            if i == len(imgs)-1:
                eject = eject_at_end
            self.print_raster_img(img, False, eject)

    def print_svg(self, svg_path: typing.Union[str, bytes], eject_at_end: bool = True):
        """
        Prints an SVG on the label
        """
        set_h = self.get_tape_width_px()

        if type(svg_path) is bytes:
            img = cairosvg.svg2png(bytestring=svg_path, output_height=set_h)
        else:
            img = cairosvg.svg2png(file_obj=svg_path, output_height=set_h)

        im = Image.open(io.BytesIO(img))
        self.print_raster_img(im, False, eject_at_end)

    def read_status(self):
        ptouch_read_status(self.dev, 0)
        # print(self.dev.status)
        # print(self.dev.status)
        # print(ptouch_statP_value(self.dev.status))
        # print(ptouch_statP_value(self.dev.status))
        # print(self.dev.status.size)
        # pt_dev_statPP(self.dev.status)
        # return copy_ptouch_statP(self.dev.status)
        return self.dev.status

    def wait_for_print(self):
        """
        This function HANGS until the print is finished
        Only call this after to call a printing function
        """
        while True:  # todo: add timeout
            a = self.read_status()
            # print(a.phase_type, a.status_type)
            if a.phase_type == 0 and a.status_type == 6:  # if we get a state change, and the state is back to waiting to receive
                break

    def send_bytes(self, data: bytes):
        """
        Sends some bytes directly to the PTouch device. This is a low-level function
        """
        b = buffer(len(data))
        for i in range(len(data)):
            b[i] = data[i]
        ptouch_send(self.dev, b.cast(), len(data))
