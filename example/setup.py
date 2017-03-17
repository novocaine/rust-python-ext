from setuptools import setup
from rust_ext import build_rust_cmdclass, install_lib_including_rust, \
    develop_including_rust

setup(name='hello-rust',
    version='1.0',
    cmdclass={
        # This enables 'setup.py build_rust', and makes it run
        # 'cargo extensions/cargo.toml' before building your package.
        'build_rust': build_rust_cmdclass('extensions/Cargo.toml', 
                                          ext_name="hello_rust.helloworld"),
        # This causes your rust binary to be automatically installed
        # with the package when install_lib runs (including when you 
        # run 'setup.py install'.
        'install_lib': install_lib_including_rust,
        # This supports development mode for your rust extension by 
        # causing the ext to be built in-place, according to its ext_name
        'develop': develop_including_rust
    },
    packages=['hello_rust'],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False
)
