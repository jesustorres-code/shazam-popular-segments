from setuptools import find_packages, setup


setup(
    name="shazam-popular-segments",
    version="0.1.0",
    description="CLI prototype for extracting Shazam Popular Segments clips.",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "shazam-segment=shazam_segments.cli:main",
        ]
    },
)
