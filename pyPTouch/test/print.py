from typing import *
import pyPTouch


def test_get_tape_width_px(printer: pyPTouch.PTouch):
    px = printer.get_tape_width_px()
    print(f"test_get_tape_width_px = {px}")

def test_print_image(printer: pyPTouch.PTouch):
    printer.print_raster_img('Among_Us.png')

def init() -> Optional[pyPTouch.PTouch]:
    printer = pyPTouch.PTouch()
    try:
        printer.open()
    except:
        print("Unable to open printer")
        return None
    else:
        return printer


if __name__ == "__main__":
    printer = init()

    if printer is not None:
        try:
            test_get_tape_width_px(printer)
            test_print_image(printer)
        finally:
            printer.close()