# rust-python-ext

[![Build Status](https://travis-ci.org/novocaine/rust-python-ext.svg?branch=master)](https://travis-ci.org/novocaine/rust-python-ext)

Setuptools helpers for rust Python extensions.

Compile and distribute Python extensions written in rust as easily as if they were written in C. 

Well, maybe easier - it's rust.

## Example

### setup.py

```python
from setuptools import setup
from rust_ext import build_rust_cmdclass, install_lib_including_rust

setup(name='hello-rust',
    version='1.0',
    cmdclass={
        # This enables 'setup.py build_rust', and makes it run 
        # 'cargo extensions/cargo.toml' before building your package.
        'build_rust': build_rust_cmdclass('extensions/cargo.toml'),
        # This causes your rust binary to be automatically installed
        # with the package when install_lib runs (including when you 
        # run 'setup.py install'.
        'install_lib': install_lib_including_rust
    },
    packages=['hello_rust'],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False
)
```

You can optionally pass additional arguments to cargo through build_rust_cmdclass - see 
https://github.com/novocaine/rust-python-ext/blob/master/rust_ext/__init__.py.

### Result:

```
➜  example git:(master) ✗ python setup.py install

.. yada yada yada ..

running build_rust
cargo build --manifest-path extensions/cargo.toml --release
    Updating registry `https://github.com/rust-lang/crates.io-index`
    Updating git repository `https://github.com/alexcrichton/pkg-config-rs.git`
 Downloading regex v0.1.38
   Compiling pkg-config v0.3.5 (https://github.com/alexcrichton/pkg-config-rs.git#42f1704b)
   Compiling regex-syntax v0.1.2
   Compiling rustc-serialize v0.3.15
   Compiling memchr v0.1.3
   Compiling aho-corasick v0.2.1
   Compiling regex v0.1.38
   Compiling python27-sys v0.0.6 (file:///Users/jsalter/dev/rust-cpython/python27-sys)
   Compiling num v0.1.25
   Compiling cpython v0.0.1 (file:///Users/jsalter/dev/rust-cpython)
   Compiling hello-world v0.0.1 (file:///Users/jsalter/Documents/dev/rust-ext/example/extensions)

.. yada yada yada ..

Installed /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/hello_rust-1.0-py2.7.egg
Processing dependencies for hello-rust==1.0
Finished processing dependencies for hello-rust==1.0

➜  example git:(master) ✗ python
Python 2.7.9 (v2.7.9:648dcafa7e5f, Dec 10 2014, 10:10:46)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information
>>> import hello_rust
>>> hello_rust.hello()
Rust says: Hello Python!
```

## Notes

* Unlike distutils, rust-python-ext delegates all rust build decisions to cargo. 
So you can't pass compiler args to the compiler from setup.py. This is by design. Cargo's awesome - use that. 
You can however pass args to cargo which might then influence what it does.

* If you want to access the python C API from rust, use https://github.com/dgrunwald/rust-cpython. 
The example dir contains a project that shows how this is done.

* Tested on Homebrew python 2.7.9 on OS X - it should not be hard to get this to work on python 3, but I have not tested it yet.

* This should interop just fine with other C-exts or cython being in the package, although I haven't tested it. 
The cmdclass approach is minimally invasive and is how, I believe, the setuptools god intends things to be.

## TODO

* Test on more platforms incl windows


