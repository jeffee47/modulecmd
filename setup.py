import setuptools
import sys
import unittest
import codecs

### workaround addition for bdist_wininst to work on pypi
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True:enc}.get(name=='mbcs')
    codecs.register(func)
### end of workaround addition

extra = {}
if sys.version_info >= (3,0):
  extra.update(use_2to3=True)

    
def run_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

def main():
    setuptools.setup(
	name='modulecmd',
	version='1.1.2',
	description='modular wrapper support for environment modules',
	author='Jeff Kiser',
	url='https://github.com/jeffee47/modulecmd',
	author_email='jkiser@synopsys.com',
	package_dir={'modulecmd' : 'modulecmd'},
	include_package_data=True,
	python_requires=">=2.7",
	keywords=["environment","modules","modulecmd",],
	license="MIT License",
	zip_safe=True,
	packages=["modulecmd"],
	test_suite='setup.run_test_suite',
	classifiers=[
		"Operating System :: POSIX",
		"Operating System :: MacOS :: MacOS X",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
	],
	**extra
    )

if __name__ == "__main__":
    main()
