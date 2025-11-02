#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="pretalx-oidc",
    version="1.0.0",
    description="OIDC authentication plugin for pretalx",
    long_description="Provides OpenID Connect (OIDC) authentication for pretalx",
    url="https://github.com/yourusername/pretalx-oidc",
    author="Your Name",
    author_email="your.email@example.com",
    license="Apache",
    install_requires=[
        "mozilla-django-oidc>=3.0.0",
        "requests>=2.25.0",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    entry_points={
        "pretalx.plugin": [
            "pretalx_oidc = pretalx_oidc:PretalxOIDCPlugin",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
