"""Build or install the standard-interface-template package."""
# 1. Standard python modules
import os

# 2. Third party modules
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

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

# Use plain-text XML definition if develop installing. Eliminates need to manually add XML to
# <path to XMS installation>/DynamicXML/dmi_xml_definitions.txt
classifier = ['XMS DMI Definition :: XML :: standard_interface_template/StandardInterfaceTemplate.xml']
ext_modules_list = []
cmdclass = {}
packages = find_packages()

setup(
    name='standard_interface_template',
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
        'xms.dmi.interfaces': 'StandardInterfaceTemplate = standard_interface_template'
    },
    # Define a classifier pointing to the definition file. Must be relative from import location (usually site-packages)
    classifiers=classifier
)
