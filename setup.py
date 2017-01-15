from setuptools import setup, find_packages
from pythiaplotter import __VERSION__


setup(
    name="PythiaPlotter",
    version=__VERSION__,
    description="Generate diagram of particles in the event tree from a "
                "High-Energy Physics Monte Carlo event generator.",
    long_description="SOMETHING HERE",
    author="Robin Aggleton",
    author_email="robinaggleton@gmail.com",
    url="https://github.com/raggleton/PythiaPlotter",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'PythiaPlotter=PythiaPlotter:main'
        ]
    },
    package_data={
        'pythiaplotter': ['particledata/*.tex', 'particledata/*.xml',
                          'printers/*.json']
    }
)