from setuptools import setup, find_packages

setup(
    name="PythiaPlotter",
    version="0.2.0",
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