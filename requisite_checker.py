"""
Class & methods to check if programs & modules exist on user's computer.
"""


import imp  # For testing if modules exist
from distutils.spawn import find_executable


def check_program_exists(program):
    """Test if external program runs."""
    if find_executable(program):
        return True
    else:
        print "!!! Cannot find program \"" + program + \
              "\", or missing from PATH"
        return False


def check_module_exists(module):
    """Test if Python module exists."""
    try:
        imp.find_module(module)
    except ImportError:
        print "!!! Module \"" + module + "\" doesn't exist"
        return False
    return True


class RequisiteChecker():
    """Class to handle checking of modules/programs.

    Queryable for program/module name via the results dictionary.
    Or to check all exist, use self.all_exist.
    """

    def __init__(self, modules=None, programs=None):
        self.modules = [] if not modules else modules
        self.programs = [] if not programs else programs

        self.results = dict()
        for mod in self.modules:
            self.results[mod] = check_module_exists(mod)
        for prog in self.programs:
            self.results[prog] = check_program_exists(prog)

    def __repr__(self):
        mod_str = ', '.join(self.modules)
        pro_str = ', '.join(self.programs)
        return '%s.%s(modules=[%r], programs=[%r])' % (self.__module__,
                                                       self.__class__.__name__,
                                                       mod_str,
                                                       pro_str)

    def __str__(self):
        return "RequisiteChecker: %s" % str(self.results)


    def all_exist(self):
        """Check if all modules and programs passed in constructor exist"""
        return all(list(self.results.values()))

    def check(self, name):
        """Check if particular module or program passed in constructor exist"""
        return self.results[name]


# def check_program_exists_old(program):
#     """Test if external program runs."""
#     # Old, not so great version that relied on program having a -h option
#     try:
#         # Storing in string stifles output
#         prog_out = subprocess.check_output([program, "-h"],
#                                            stderr=subprocess.STDOUT)
#     except subprocess.CalledProcessError as cpe:
#         print(cpe.returncode)
#         print(cpe.output)
#         return False
#     except OSError as e:
#         if e.errno == os.errno.ENOENT:
#             print "!!! You need to install program \"" + program + \
#                   "\" or add it to PATH variable"
#             print(e)
#         else:
#             # Something else went wrong while trying to run
#             print(e)
#         return False
#     return True
