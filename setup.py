from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="foodnutrition",
    version="0.1.2",
    author="XujunNoahWang",
    author_email="",
    description="A food nutrition analysis app using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XujunNoahWang/foodnutrition",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "foodnutrition=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["static/*", "*.json"],
    },
) 