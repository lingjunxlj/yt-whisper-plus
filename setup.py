from setuptools import setup, find_packages

setup(
    version="1.0",
    name="yt_whisper_plus",
    packages=find_packages(),
    py_modules=["yt_whisper_plus"],
    author="lingjunxlj",
    install_requires=[
        "yt-dlp",
        "whisper",
    ],
    description="Generate subtitles for YouTube videos using Whisper",
    entry_points={
        "console_scripts": ["yt_whisper_plus=yt_whisper_plus.cli:main"],
    },
    include_package_data=True,
)
