# modulecmd
Python wrapper around environment module interface

modulecmd enables direct use/integration of UNIX environment inside of python scripts.  It is similar, in spirit,
to Perl's Env::Modulecmd CPAN module.  

In order to use it, effectively, you should already have environment modules (modulecmd) setup in your basic 
shell environment.  Then, to take advantage of them from within a python script, just say:

from modulecmd import Modulecmd

mcmd = Modulecmd()
mcmd.use('/my/local/modules/repo')
mcmd.load('gcc/7.4.0') # assuming this module is defined
### do some stuff
### change gcc to a different version
mcmd.switch('gcc','gcc/7.2')
### do some more stuff
mcmd.unload('gcc')
### environment is clean again

All of the basic command from modulecmd are implemented in this module; such as,

load
unload
switch
purge
use
unuse
etc.etc.
