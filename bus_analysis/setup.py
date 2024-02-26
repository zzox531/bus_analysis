from setuptools import setup, find_packages

setup(
    name="bus_analysis",
    version="1.0",
    packages=find_packages(),
    description="Package used to analyze geolocation data of buses in Warsaw",
    author="Ignacy Kozakiewicz",
    author_email="ignacykozakiewicz@gmail.com",
    url="https://github.com/zzox531",
    install_requires=[
        "pandas",
        "requests",
        "geopy",
        "folium",
        "datetime",
    ],
)