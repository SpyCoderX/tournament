from setuptools import setup

setup(

app=['Main.py'],

options={'py2app': {'argv_emulation': True}},

setup_requires=['py2app'],

)