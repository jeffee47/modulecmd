#!/usr/bin/env python
  
"""
	Python wrapper to system environment modules.  Basic functions
	include:
		load,unload,purge,list,switch,use,unuse

	To use:
		from modulecmd import Modulecmd
		
		m = Modulecmd()
		m.use("/some/custom/path") # will append to existing
		# load/unload can be called with either a single
		# argument (string) or tuple/list
		m.load("mymod")
		m.load(("mod2","mod3"))
		m.unload("mod2")
		m.switch("mod3","mod3/dev")
		m.list() # shows currently loaded modules
		m.purge() # unloads everything
"""

import os
import sys
import getopt
import traceback

class Modulecmd:

  def __init__(self,modulecmd=None,modulepath=[],verbose=False,modulehome="/global/etc/modules/default"):
    """
	Modulecmd(<attributes>)

	attributes:
		modulecmd=<full path to modulecmd>
			if not provided, it will try to find it with $PATH
		modulepath=<path>
			path(s) to add to modulepath.  Can also change
			this on the fly with use/unuse
		verbose=True|False
			Default is False
		modulehome=<path>
			path where MODULEHOME typically resides.  This 
			relies on $MODULEHOME/bin/platform to exist
			to guess the best utility for the current
			platform it is being called from
    """
    self.verbose = verbose
    if modulecmd:
      self.modulecmd = modulecmd
    else:
      self.modulecmd = self._which('modulecmd')
    if not self.modulecmd:
      if modulehome is not None:
        mod_dir = os.path.join(modulehome,"bin")
        if os.path.exists(mod_dir):
          mod_platform = self._runsystem(os.path.join(mod_dir,"platform"))
          if self.verbose:
            print "Looking for platform under %s" % mod_dir
            print "Found it to be %s" % mod_platform
          if os.path.exists(os.path.join(mod_dir,"modulecmd.%s" % mod_platform)):
            self.modulecmd = os.path.join(mod_dir,"modulecmd.%s" % mod_platform)
    if not self.modulecmd:
      raise Exception("No modulecmd could be found to leverage")
    if modulepath:
      modulepath.reverse()
    if modulepath: self.use(modulepath)
    if self.verbose:
      print "Using modulecmd %s" % self.modulecmd

  def modulepaths(self):
    """
	Usage:
		m.modulepaths()
	Returns:
		list of paths

	Returns a list of directories that will be traversed to look for modules.  
	The environment variable $MODULEPATH is used to find this.  This can
	be altered on the fly either by:
		1) Altering $MODULEPATH environment variable (not recommended)
		2) using the use/unuse methods of this class (recommended)
    """
    try:
      return os.environ.get('MODULEPATH',"").split(os.pathsep)
    except Exception,e:
      return []
  
  def show(self,mod):
    """
	Usage:
		m.show(<module>)
	Returns:
		String with information about module.  Doesn't affect environment, directly.

	Shows information about a given module and the setup that would be taken
	if a load is called on it.
    """
    return self._modulecmd("%s python show %s" % (self.modulecmd,mod))
  
  def unuse(self,modulepath):
    """
	Usage:
		m.unuse(<path>)
		m.unuse([<path1>,<path2>,etc.])
	Returns:
		None
	
	Alters the $MODULEPATH environment variable by removing paths.  To remove all paths
	you can say:

		m.unuse(m.modulepaths())

    """
    if type(modulepath) is type(""):
      tmp = modulepath
      modulepath = [tmp]
    modulepath.reverse()
    for modpath in modulepath:
      if modpath.strip() == "": continue
      self._modulecmd("%s python unuse %s" % (self.modulecmd,modpath))
    
  def use(self,modulepath):
    """
	Usage:
		m.use(<path>)
		m.use([<path1>,<path2>,etc.])
	Returns:
		None
	
	Alters the $MODULEPATH environment variable by adding paths.
    """
    if type(modulepath) is type(""):
      tmp = modulepath
      modulepath = [tmp]
    modulepath.reverse()
    for modpath in modulepath:
      self._modulecmd("%s python use %s" % (self.modulecmd,modpath))
      

  def _which(self,cmd):
    try:
      realcmd = cmd.strip().split()[0]
      for tmpdir in os.environ['PATH'].split(os.pathsep):
        try:
          testpath = os.path.join(tmpdir,realcmd)
          if os.path.isfile(testpath) or os.path.islink(testpath):
            return testpath
        except Exception,e:
          traceback.print_exc()
    except Exception,e:
      traceback.print_exc()
    return None

  def list(self):
    """
	Usage:
		m.list()
	Returns:
		list of all environment modules currently loaded
    """
    try:
      return os.environ['LOADEDMODULES'].split(os.pathsep)
    except Exception,e:
      return []

  def purge(self):
    """
	Usage: 
		m.purge()
	Returns:
		None

	Used to unload ALL modules from the current environment
    """
    self._modulecmd("%s python purge" % self.modulecmd)

  def load(self,mods):
    """
	Usage:
		m.load(<module>)
		m.load([<mod1>,<mod2>,etc.])
	Returns:
		None
	
	Used to add module(s) to current environment.  Input arguments can be either:
		1) String (single module add)
		2) Tuple/List (multiple module add)
    """
    if type(mods) is type(""):
      tmpmod = mods
      mods = [tmpmod,]
    for m in mods:
      self._modulecmd("""%s python load %s""" % (self.modulecmd,m))

  def add(self,*args,**kwargs):
    """
	Alias to m.load method
    """
    return self.load(*args,**kwargs)

  def switch(self,m1,m2):
    """
	Usage:
		m.switch(<mod1>,<mod1a>)
	Returns:
		None

	Switches the version of a particular module
    """
    self._modulecmd("""%s python switch %s %s""" % (self.modulecmd,m1,m2))

  def unload(self,mods):
    """
	Usage:
		m.unload(<module>)
		m.unload([<mod1>,<mod2>,etc.])
	Returns:
		None
	
	Used to remove module(s) from current environment.  Input arguments can be either:
		1) String (single module add)
		2) Tuple/List (multiple module add)
    """
    if type(mods) is type(""):
      tmpmod = mods
      mods = [tmpmod,]
    for m in mods:
      self._modulecmd("""%s python unload %s""" % (self.modulecmd,m))
     
  def rm(self,*args,**kwargs):
    """
	Alias for m.unload method
    """
    return self.unload(*args,**kwargs)
 
  def swap(self,*args,**kwargs):
    """
	Alias for m.switch method
    """
    return self.switch(*args,**kwargs)

  def display(self,*args,**kwargs):
    """
	Alias for m.show method
    """
    return self.show(*args,**kwargs)

  def _runsystem(self,cmd):
    nosubprocess = False
    try:
      import subprocess
    except Exception,e:
      nosubprocess = True
    try:
      out = subprocess.check_output(
		cmd,
		stderr=subprocess.STDOUT,
		shell=True)
    except Exception,e:
      try:
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
        out = p.stdout.read()
      except Exception,e:
        try:
          i,o,e = os.popen3(cmd)
          out = o.read()
        except Exception,e:
          if self.verbose:
            print "Could not read output from '%s'" % cmd
            traceback.print_exc()
    if out: 
      out = out.strip()
      if type(out) is not type(""):
        out = out.decode('utf-8')
    return out

  def _modulecmd(self,cmd):
    out = None
    cmdtype = None
    noout_cmds = ["list","show",]
    try:
      cmdtype = cmd.strip().split()[2]
    except Exception,e:
      if self.verbose:
        traceback.print_exc()
      cmdtype = None

    try:
      out = self._runsystem(cmd)
    except Exception,e:
      if self.verbose:
        traceback.print_exc()
    if out: 
      if cmdtype not in noout_cmds:
        if self.verbose:
          print "Calling eval on %s" % out
        exec(out)
    elif self.verbose:
      print "No output from '%s'" % cmd
    return out
  
if __name__ == "__main__":
  m = Modulecmd(verbose=True)
  print m.list()
