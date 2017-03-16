from __future__ import print_function
import sys
import subprocess
import os.path
import glob
from distutils.cmd import Command
from distutils.command.install_lib import install_lib
from setuptools.command.develop import develop
from distutils.file_util import copy_file


class RustBuildCommand(Command):
    """ 
    Command for building rust crates via cargo.

    Don't use this directly; use the build_rust_cmdclass
    factory method.
    """

    description = "build rust crates into Python extensions"

    user_options = [
        ('inplace', 'i',
         "ignore build-lib and put compiled extensions into the source "
             "directory alongside your pure Python modules"),
    ]

    boolean_options = ['inplace']

    def _unpack_classargs(self):
        for k, v in self.__class__.args.items():
            setattr(self, k, v)

    def initialize_options(self):
        self._unpack_classargs()
        self.inplace = 0

    def finalize_options(self):
        pass

    def features(self):
        version = sys.version_info
        if (2,7) < version < (2,8):
            return "python27-sys"
        elif (3,3) < version:
            return "python3-sys"
        else:
            raise ValueError("Unsupported python version: %s" % sys.version)

    def run(self):
        # Make sure that if pythonXX-sys is used, it builds against the current 
        # executing python interpreter.
        bindir = os.path.dirname(sys.executable)

        env = os.environ.copy()
        env.update({
            # disables rust's pkg-config seeking for specified packages,
            # which causes pythonXX-sys to fall back to detecting the 
            # interpreter from the path.
            "PYTHON_2.7_NO_PKG_CONFIG": "1",
            "PATH":  bindir + os.pathsep + os.environ.get("PATH", "")
        })

        # Execute cargo.
        try:
            args = (["cargo", "build", "--manifest-path", self.cargo_toml_path,
                "--features", self.features()] + list(self.extra_cargo_args or []))
            if not self.debug:
                args.append("--release")
            if not self.quiet:
                print(" ".join(args), file=sys.stderr)
            output = subprocess.check_output(args, env=env)
        except subprocess.CalledProcessError as e:
            msg = "cargo failed with code: %d\n%s" % (e.returncode, e.output)
            raise Exception(msg)
        except OSError:
            raise Exception("Unable to execute 'cargo' - this package " 
                "requires rust to be installed and cargo to be on the PATH")

        if not self.quiet:
            print(output, file=sys.stderr)

        # Find the shared library that cargo hopefully produced and copy 
        # it into the build directory as if it were produced by build_cext.
        if self.debug:
            suffix = "debug"
        else:
            suffix = "release"

        target_dir = os.path.join(os.path.dirname(self.cargo_toml_path), 
            "target/", suffix)

        if sys.platform == "win32":
            wildcard_so = "*.dll"
        elif sys.platform == "darwin":
            wildcard_so = "*.dylib"
        else:
            wildcard_so = "*.so"

        try:
            dylib_path = glob.glob(os.path.join(target_dir, wildcard_so))[0]
        except IndexError:
            raise Exception("rust build failed; unable to find any shared "
                            "library in %s" % target_dir)

        # Ask build_ext where the shared library would go if it had built it,
        # then copy it there.
        build_ext = self.get_finalized_command('build_ext')
        build_ext.inplace = self.inplace
        if self.ext_name:
            target_fname = self.ext_name
        else:
            target_fname = os.path.splitext(os.path.basename(dylib_path)[3:])[0]
        ext_path = build_ext.get_ext_fullpath(os.path.basename(target_fname))

        try:
            os.makedirs(os.path.dirname(ext_path))
        except OSError:
            pass

        copy_file(dylib_path, ext_path, verbose=self.verbose,
                dry_run=self.dry_run)


def build_rust_cmdclass(cargo_toml_path, debug=False, 
                        extra_cargo_args=None, quiet=False,
                        ext_name=None):
    """
    Args:
        cargo_toml_path (str)   The path to the cargo.toml manifest
                                (--manifest)
        debug (boolean)         Controls whether --debug or --release is 
                                passed to cargo.
        extra_carg_args (list)  A list of extra argumenents to be passed to 
                                cargo.
        quiet (boolean)         If True, doesn't echo cargo's output.
        ext_name (str)          Name of the extension, including package names.
                                If not provided, will be the name of the
                                library built by cargo with 'lib' removed

    Returns:
        A Command subclass suitable for passing to the cmdclass argument
        of distutils.
    """

    # Manufacture a once-off command class here and set the params on it as
    # class members, which it can retrieve later in initialize_options.
    # This is clumsy, but distutils doesn't give you an appropriate
    # hook for passing params to custom command classes (and it does the
    # instantiation).

    _args = locals()

    class RustBuildCommand_Impl(RustBuildCommand):
        args = _args

    return RustBuildCommand_Impl


class install_lib_including_rust(install_lib):
    """
    A replacement install_lib cmdclass that remembers to build_rust
    during install_lib.

    Typically you want to use this so that the usual 'setup.py install'
    just works.
    """

    def build(self):
        install_lib.build(self)
        if not self.skip_build:
            self.run_command('build_rust')


class develop_including_rust(develop):
    """
    A replacement develop cmdclass that remembers to build_rust
    inplace=1 (develop already does build_ext inplace=1)
    """

    def run(self):
        develop.run(self)
        self.reinitialize_command('build_rust', inplace=1)
        self.run_command('build_rust')
