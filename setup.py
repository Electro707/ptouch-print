# This file is partially copied from https://stackoverflow.com/questions/42585210/extending-setuptools-extension-to-use-cmake-in-setup-py
import os
import pathlib
import shutil
import sys
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)
        # super().run()

    def build_extension(self, ext):
        cwd = pathlib.Path().absolute()

        # these dirs will be created in build_py, so if you don't have
        # any python sources to bundle, the dirs will be missing
        build_temp = pathlib.Path(self.build_temp)
        shutil.rmtree(build_temp, ignore_errors=True)
        build_temp.mkdir(parents=True, exist_ok=True)
        # extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).resolve()
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        cfg = 'Debug' if self.debug else 'Release'

        # example of cmake args
        cmake_args = [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DPYTOUCH_OUTPUT_DIR={extdir}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            "-DBUILD_PYPTOUCH=1",
            f"-DPython3_EXECUTABLE={sys.executable}"
            # "--trace"
        ]

        os.chdir(str(build_temp))
        self.spawn(['cmake', str(cwd)] + cmake_args)
        self.spawn(['cmake', '--build', '.'])
        # Troubleshooting: if fail on line above then delete all possible
        # temporary CMake files including "CMakeCache.txt" in top level dir.
        os.chdir(str(cwd))


setup(
    ext_modules=[CMakeExtension('pyPTouch._libptouchSwig')],
    cmdclass={
        'build_ext': CMakeBuild,
    })
