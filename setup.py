from setuptools import setup, find_packages

setup(
    name="motify",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'ttkbootstrap>=1.10.0',
        'yt-dlp>=2023.3.4',
        'mutagen>=1.46.0',
        'plyer>=2.1.0',
        'spotipy>=2.23.0',
        'watchdog>=2.3.1',
        'pillow>=9.5.0',
        'matplotlib>=3.5.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'motify=src.app:main',
        ],
    },
    author="Mosh3eb",
    author_email="your.email@example.com",
    description="A powerful music downloader and manager application",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mosh3eb/motify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    include_package_data=True,
)
