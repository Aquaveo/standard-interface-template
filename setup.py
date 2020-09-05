"""Build or install the standard-interface-template package."""
# 1. Standard python modules
import fnmatch
import os
import sys

# 2. Third party modules
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

packaging = 'bdist_wheel' in sys.argv
if packaging:
    from Cython.Build import cythonize
    from xmsapi.packaging.cython_extensions import generate_cython_extensions

try:  # Only really need correct version when packaging on CI.
    from version_generator import get_version_string
    version = get_version_string(strict=False)
except Exception:
    version = '99.99.99'

requires = [
    'gdal>=2.4.1',
    'xmsapi>=2.1.0',
    'xmscomponents>=1.0.0',
    'xmsconstraint>=1.7.0',
    'xmscore>=3.2.0',
    'xmscoverage>=0.0.8',
    'xmsdatasets>=0.0.1',
    'xmsguipy>=2.4.0',
    'xmssnap>=2.0.4',
    'h5py',
    'matplotlib<=3.3.0',  # TODO remove once windows version is working
    'numpy',
    'orjson',
    'pandas',
    'xarray',
    'PySide2<5.15.0',  # Another broken PySide2
]
test_requirements = requires
test_requirements.extend([
    'testfixtures',
])


cython_excludes = [
    '**/__init__.py',
    'standard-interface-template/__main__.py',
]


def not_cythonized(tup):
    """Determine if a pure Python module should be included in the package.

    Args:
        tup (tuple): package name, module name, filepath

    Returns:
        bool: True if the module should be included.
    """
    (package, module, filepath) = tup
    return any(fnmatch.fnmatch(filepath, pat=pattern) for pattern in cython_excludes)


class PydBuilder(build_py):
    """Implementation of build_py to allow mix of pure Python and Cython pyd extensions."""
    def find_package_modules(self, package, package_dir):
        """Include any pure Python modules that have been specified in cython_excludes.

        Args:
            package (str): Name of the package
            package_dir (str): Location of the pockage source

        Returns:
            list: List of the pure Python modules that should be included in the package
        """
        modules = super().find_package_modules(package, package_dir)
        return filter(not_cythonized, modules)


# Use plain-text XML definition if develop installing. Eliminates need to manually add XML to
# <path to XMS installation>/DynamicXML/dmi_xml_definitions.txt
classifier = ['XMS DMI Definition :: DIN :: standard-interface-template/copy-protected.din',
              ] if packaging else \
             ['XMS DMI Definition :: XML :: standard-interface-template/StandardInterfaceTemplate.xml',
              ]
cythonize_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'standard-interface-template')
ext_modules_list = cythonize(generate_cython_extensions(cythonize_path, cython_excludes), language_level="3") \
    if packaging else []
cmdclass = {'build_py': PydBuilder} if packaging else {}
packages = ['standard-interface-template'] if packaging else find_packages()

setup(
    name='standard-interface-template',
    version=version,
    packages=packages,
    include_package_data=True,
    license='BSD 2-Clause License',
    description='',
    author='Aquaveo',
    setup_requires=['wheel'],
    install_requires=requires,
    tests_require=test_requirements,
    extras_require={
        'tests': [],
    },
    dependency_links=[
        'https://aquapi.aquaveo.com/aquaveo/stable/',
    ],
    ext_modules=ext_modules_list,
    cmdclass=cmdclass,
    entry_points={  # Register an entry point so XMS can find the package on startup.
        'xms.dmi.interfaces': 'StandardInterfaceTemplate = standard-interface-template'
    },
    # Define a classifier pointing to the definition file. Must be relative from import location (usually site-packages)
    classifiers=classifier
)
