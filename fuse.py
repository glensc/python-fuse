#@+leo-ver=4
#@+node:@file fuse.py
#
#    Copyright (C) 2001  Jeff Epler  <jepler@unpythonic.dhs.org>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#


#@@language python
#@+others
#@+node:imports
# suppress version mismatch warnings
try:
    import warnings
    warnings.filterwarnings('ignore',
                            'Python C API version mismatch',
                            RuntimeWarning,
                            )
except:
    pass
 
from _fuse import main, FuseGetContext, FuseInvalidate
from string import join
import sys
from errno import *

#@-node:imports
#@+node:class ErrnoWrapper
class ErrnoWrapper:
    #@	@+others
    #@+node:__init__
    def __init__(self, func):
    	self.func = func
    #@-node:__init__
    #@+node:__call__
    def __call__(self, *args, **kw):
    	try:
    		return apply(self.func, args, kw)
    	except (IOError, OSError), detail:
    		# Sometimes this is an int, sometimes an instance...
    		if hasattr(detail, "errno"): detail = detail.errno
    		return -detail
    #@-node:__call__
    #@-others
#@-node:class ErrnoWrapper
#@+node:class Fuse
class Fuse:

    #@	@+others
    #@+node:attribs
    _attrs = ['getattr', 'readlink', 'getdir', 'mknod', 'mkdir',
    	  'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
    	  'chown', 'truncate', 'utime', 'open', 'read', 'write', 'release',
          'statfs', 'fsync']
    
    flags = 0
    multithreaded = 0
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, *args, **kw):
    
        # default attributes
        if args == ():
            # there is a self.optlist.append() later on, make sure it won't
            # bomb out.
            self.optlist = []
        else:
            self.optlist = args
        self.optdict = kw

        if len(self.optlist) == 1:
            self.mountpoint = self.optlist[0]
        else:
            self.mountpoint = None
        
        # grab command-line arguments, if any.
        # Those will override whatever parameters
        # were passed to __init__ directly.
        argv = sys.argv
        argc = len(argv)
        if argc > 1:
            # we've been given the mountpoint
            self.mountpoint = argv[1]
        if argc > 2:
            # we've received mount args
            optstr = argv[2]
            opts = optstr.split(",")
            for o in opts:
                try:
                    k, v = o.split("=", 1)
                    self.optdict[k] = v
                except:
                    self.optlist.append(o)

    def GetContext(self):
	return FuseGetContext(self)

    def Invalidate(self, path):
        return FuseInvalidate(self, path)

    #@-node:__init__
    #@+node:main
    def main(self):

        d = {'mountpoint': self.mountpoint}
        d['multithreaded'] = self.multithreaded
        if hasattr( self, 'debug'):
            d['lopts'] = 'debug';

        k=[]
        if hasattr(self,'allow_other'):
                k.append('allow_other')

        if hasattr(self,'kernel_cache'):
                k.append('kernel_cache')

	if len(k):
                d['kopts'] = join(k,',')
	
    	for a in self._attrs:
    		if hasattr(self,a):
    			d[a] = ErrnoWrapper(getattr(self, a))
    	apply(main, (), d)
    #@-node:main
    #@-others
#@-node:class Fuse
#@-others
#@-node:@file fuse.py
#@-leo