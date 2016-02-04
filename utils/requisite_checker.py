"""
Class & methods to check if programs & modules exist on user's computer.

+TODO: maybe this should be redesigned more like a module e.g.
+But what if we want to query? better to have
+
+if "vim" in results.programs:
+    # failed
+else:
+    # carry on
+or
+
+if not results.programs["vim"]:
+    # failed
+else:
+    # carry on
+
+or something like:
+
+import requisite_checker
+failed = requisite_checker.check(modules=["os"], programs=["vim"])
+# failed = None if all OK, otherwise namedtuple of those failing
+if failed:
+    print "Missing modules %s and programs %s" % failed.modules, failed.programs
+
"""


import logging_config
import logging
import imp  # For testing if modules exist
from distutils.spawn import find_executable


log = logging.getLogger(__name__)


def check_program_exists(program):
    """Test if external program runs."""
    if find_executable(program):
        return True
    else:
        # log.error("Error: cannot find program \"" + program + \
        #           "\", or missing from PATH")
        return False


def check_module_exists(module):
    """Test if Python module exists."""
    try:
        imp.find_module(module)
    except ImportError:
        # log.error("Error: module \"" + module + "\" doesn't exist")
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
