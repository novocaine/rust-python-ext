from setuptools import setup
from rust_ext import build_rust_cmdclass, install_lib_including_rust

setup(name='hello-rust',
    version='1.0',
    cmdclass={
        'build_rust': build_rust_cmdclass('extensions/cargo.toml'),
        'install_lib': install_lib_including_rust
    },
    packages=['hello_rust'],
    zip_safe=False
)
