from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='gme_etl',
    version='1.0',
    description='packages for ETLs',
    license="MIT",
    long_description=long_description,
    author='Dmitry V',
    author_email='dveselov.phd@gmail.com',
    python_requires='>3.9',
    packages=['gme_etl'],  # same as name
    install_requires=['pandas', 'pyppeteer', 'redis', 'plotly', 'dash', 'sqlalchemy==1.4.48', 'psycopg2-binary'],
    extras_require={'formatting': ['black', 'pylint']},  # external packages as dependencies
)
