"""Django Admin Plus setuptools configuration."""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="admin_plus",
    description="Django admin panel extension.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Andrey Shpak",
    author_email="ashpak@ashpak.ru",
    url="https://github.com/insspb/django-admin-plus",
    zip_safe=False,
    python_requires=">=3.7",
    platforms="any",
    packages=find_packages(),
    version="0.1.0",
    install_requires=["django>=3.0"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=[
        "django",
        "django-filters",
        "django-admin",
        "django-admin-plus",
    ],
    project_urls={
        "Source": "",
        "Changelog": "",
    },
)
