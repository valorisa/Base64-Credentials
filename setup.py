from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="base64-credentials",
    version="0.3.0",
    description="Gestionnaire de credentials Base64 — encode/décode username:password",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="valorisa",
    url="https://github.com/valorisa/Base64-Credentials",
    py_modules=["credentials_manager"],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "credentials-manager=credentials_manager:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    license="MIT",
)
