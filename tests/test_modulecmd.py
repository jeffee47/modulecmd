import unittest
import os
from modulecmd import Modulecmd
import six

def is_exe(fpath):
    import re

    iswin = False
    if six.PY2:
        uname = os.uname()[0].lower().strip()
    else:
        uname = os.uname().sysname.lower().strip()
    if re.search(r'(?i)win|nt', uname):
        iswin = True
    if iswin:
        return os.path.isfile(fpath)
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

class TestEnvironmentReady(unittest.TestCase):

    def test_have_modulecmd(self):
        mcmd = None
        for epath in os.environ.get('PATH', '').split(os.pathsep):
            efile = os.path.join(epath, "modulecmd")
            if is_exe(efile):
                mcmd = efile
                break
        self.assertEqual(
            isinstance(mcmd, str),
            True,
            "No modulecmd utility was found in $PATH",
        )

class TestModulecmdFunctionality(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestModulecmdFunctionality, self).__init__(*args, **kwargs)
        self.module_dir = None
        self.topmod = "mcmdtest"
        self.path_add = '/not/real/path'
        self.modules = []
        self.setup_ok = False
        self.mobj = None

    def setUp(self):
        import tempfile
        import traceback

        self.module_dir = tempfile.mkdtemp()
        modfile_contents = """#%%Module1.0#####################################################################
set list [ split $ModulesCurrentModulefile / ]
set global(install,abbr_app_name) [ lindex $list end-1 ]
set global(install,version_number) [ lindex $list end-0 ]
switch -regex $global(install,version_number) {
	{^1} {
		prepend-path {__TEST_MODULECMD_VERSION__} "1"
	} {^\d+} {
		prepend-path {__TEST_MODULECMD_VERSION__} "[expr { int($global(install,version_number)) }]"
	} default {
		puts stderr "You must specify a numeric version!"
	}
}
setenv __TEST_MODULECMD_DUMMY__ {dummy}
append-path PATH {%s}""" % (self.path_add)

        vfile_contents = '''#%Module1.0
set ModulesVersion "1"'''

        version_files = ["1", "2", "3.1"]
        tmpdir = os.path.join(self.module_dir, self.topmod)
        try:
            os.makedirs(tmpdir)
            for vfile in version_files:
                with open(os.path.join(tmpdir, vfile), "w") as vfh:
                    vfh.write(modfile_contents)
                    self.modules.append("%s/%s" % (self.topmod, vfile))
            with open(os.path.join(tmpdir, ".version"), "w") as version_fh:
                version_fh.write(vfile_contents)
            self.mobj = Modulecmd()
            self.mobj.use(self.module_dir)
            self.setup_ok = True
        except OSError as os_err:
            traceback.print_exc()

    def tearDown(self):
        import shutil
        if self.module_dir:
            self.mobj.unuse(self.module_dir)
            mdir = os.path.join(self.module_dir,self.topmod)
            rmfiles = [os.path.join(mdir,x) for x in os.listdir(mdir)]
            for tmpfile in rmfiles:
                os.remove(tmpfile)
            shutil.rmtree(mdir)
            shutil.rmtree(self.module_dir)
            
    def test_setup(self):
        self.assertEqual(self.setup_ok,True,"Could not setup properly")

    def test_use(self):
        firstpath = os.environ['MODULEPATH'].split(os.pathsep)[0]
        self.assertEqual(
            firstpath,
            self.module_dir,
            "module use is failing to update environment")

    def test_switch(self):
        import random
        self.mobj.load(self.topmod)

        for x in range(0,10):
            nextmod = self.modules[random.randint(
                                       0,
                                       len(self.modules) -1,
                                   )]
            self.mobj.switch(self.topmod,nextmod)
            tmp_version = int(float(os.path.basename(nextmod)))
            self.assertEqual(
                tmp_version,
                int(float(os.environ['__TEST_MODULECMD_VERSION__'])),
                "Envrionment version is wrong with switch to %s" % nextmod
            )

    def test_load_unload(self):
        import random
        ### pick random submodule to load
        for x in range(0,10):
            nextmod = self.modules[random.randint(
                                       0,
                                       len(self.modules) -1,
                                   )]
            self.mobj.load(nextmod)
            version = int(float(os.path.basename(nextmod)))
            self.assertEqual(
                version, 
                int(os.environ['__TEST_MODULECMD_VERSION__']),
                "%s version bad for module %s" % (version,nextmod)
            )
            self.assertEqual(
                self.path_add,
                os.environ['PATH'].split(os.pathsep)[-1],
                True
            )
            self.mobj.unload("%s" % (nextmod))
            path_back = self.path_add not in os.environ['PATH'].split(os.pathsep)
            self.assertEqual(
                path_back,
                True,
                "$PATH did not revert after unload of %s" % (nextmod)
            )
            cmdver = os.environ.get('__TEST_MODULECMD_VERSION__',None)
            self.assertEqual(
                cmdver,
                None,
                "VERSION did not remove itself after unload of %s" % (nextmod)
            )
                
        
if __name__ == "__main__":
    unittest.main()

