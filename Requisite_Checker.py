import imp  # For testing if modules exist
import os
import subprocess


class Requisite_Checker():
    """
    Class to handle checking of modules/programs.
    Queryable for program/module name via the self.check dictionary.
    """

    def __init__(self, modules=None, programs=None):
        modules = [] if not modules else modules
        programs = [] if not programs else programs
        self.check = dict()

        for mod in modules:
            self.check[mod] = self.check_module_exists(mod)
        for prog in programs:
            self.check[prog] = self.check_program_exists(prog)

    def check_program_exists(self, program):
        """Test if external program runs."""
        try:
            # Storing in string stifles output
            prog_out = subprocess.check_output([program, "-h"],
                                               stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            print(cpe.returncode)
            print(cpe.output)
            return False
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "!!! You need to install \"" + program + \
                      "\" or add it to PATH variable"
                print(e)
            else:
                # Something else went wrong while trying to run
                print(e)
            return False
        return True

    def check_module_exists(self, module):
        """Test if Python module exists."""
        try:
            imp.find_module(module)
        except ImportError:
            print "!!! Module \"" + module + "\" doesn't exist"
            return False
        return True
