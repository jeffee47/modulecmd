from setuptools import setup
import sys

extra = {}
if sys.version_info >= (3,0):
  extra.update(use_2to3=True)

setup(
	name='modulecmd',
	version='1.0.2',
	description='modular wrapper support for environment modules',
	author='Jeff Kiser',
	url='https://github.com/jeffee47/modulecmd',
	author_email='jkiser@synopsys.com',
	py_modules=["modulecmd"],
	keywords=["environment","modules","modulecmd",],
	license="MIT License",
	classifiers=[
		"Operating System :: POSIX",
		"Operating System :: MacOS :: MacOS X",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
	],
	**extra
)
