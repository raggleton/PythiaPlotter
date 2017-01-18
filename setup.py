from setuptools import setup, find_packages
from pythiaplotter import __VERSION__


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


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
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'PythiaPlotter=pythiaplotter.PythiaPlotter:main'
        ]
    },
    package_data={
        'pythiaplotter': ['particledata/*.tex', 'particledata/*.xml',
                          'printers/*.json']
    },
    classifiers=[
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7'
    ]
)
