from setuptools import setup, find_packages

setup(
    name = "rust-ext",
    version = "0.1",
    packages = ["rust_ext"],

    # metadata for upload to PyPI
    author = "James Salter",
    author_email = "iteration@gmail.com",
    description = "Distutils helpers for rust Python extensions",
    license = "BSD",
    keywords = "rust python extensions"
)
