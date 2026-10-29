import collections
import os
import sys

import numpy as np

from errors import SillyHumanError

class Grid:

    def __init__(self, folder_path, disc_order):
        #TODO: change it back
        self.folder_path = folder_path
        self.disc_order = disc_order
        # Number of dimensions
        self.nd = None

        # Number of gridpoints
        self.Nx = None
        self.Ny = None
        self.Nz = None
    
        # Domain lengths
        self.Lx = None
        self.Ly = None
        self.Lz = None
    
        # Domain limits [min, max]
        self.xlim = None
        self.ylim = None
        self.zlim = None
    
        # Grid types
        self.type_x = None
        self.type_y = None
        self.type_z = None

        # Grid Arrays
        self.x = None
        self.y = None
        self.z = None

        # whether grid is mapped or not
        self.mapped_grid = None
        self.load_params(folder_path)
        self.load_arrays(folder_path)

    def load_arrays(self, folder_path, style='vector'): 
        if self.nd == 2:
            sel1 = ([0,-1],0)
            sel2 = (0,[0,-1])
            sel3 = ([0,-1], [0,-1])
            if style == 'vector':
                if isdim('x'):
                    X1 = self.reader('x', *sel1)
                    if isdim('y'):
                        X2 = self.reader('y', *sel2)
                    elif isdim('z'):
                        X2 = self.reader('z', *sel2)
                else:
                    X1 = self.reader('y', *sel1)
                    X2 = self.reader('z', *sel2)
            elif style == 'full':
                if isdim('x'):
                    X1 = self.reader('x',*sel3)
                    if isdim('y'):
                        X2 = self.reader('y', *sel3)
                    elif isdim('z'):
                        X2 = self.reader('z', *sel3)
                else:
                    X1 = self.reader('y', *sel3)
                    X2 = self.reader('z', *sel3)
            if isdim('x'):
                x = X1
                if isdim('y'):
                    y = X2
                else:
                    z = X2
            else:
                y = X1
                z = X2
        elif self.nd == 3:
            if style == 'vector':
                x = self.reader('x', [0,-1],0,0)
                y = self.reader('y', 0,[0,-1],0)
                z = self.reader('z', 0,0,[0,-1])
            elif style == 'full':
                x = self.reader('x', [0,-1],[0,-1],[0,-1])
                y = self.reader('y', [0,-1],[0,-1],[0,-1])
                z = self.reader('z', [0,-1],[0,-1],[0,-1])

        if self.nd == 2:
            #TODO: look into this
            self.X1 = X1
            self.X2 = X2
        elif self.nd == 3:
            self.x = x
            self.y = y
            self.z = z

    def load_params(self, folder_path):
        # Open the file for reading only.
        conf_path = '{0:s}spins.conf'.format(folder_path)
        f = open(conf_path, 'r')

        # Loop through each line, parsing as we go.
        # Each line is assumed to be of the form
        # key = val \n
        # Comments are preceded by '#'

        for line in f:
            # Find the lenght of the variable name
            var_len = 0
            line_len = len(line)

            if (line_len > 0) and (line[0] != '#'):

                for char in line:
                    if char == '=':
                        break
                    else:
                        var_len = var_len + 1
            
                # strip removes any leading and trailing whitespace
                var = line[0:var_len].strip()
                try:
                    val = float(line[var_len+1:line_len-1].strip())
                except:
                    val = line[var_len+1:line_len].strip()

                # This is where we deal with the case-sensitive for nx,Nx,nX,NX,etc
                if var == 'nx' or var == 'NX' or var == 'nX':
                    var = 'Nx'
                if var == 'ny' or var == 'NY' or var == 'nY':
                    var = 'Ny'
                if var == 'nz' or var == 'NZ' or var == 'nZ':
                    var = 'Nz'
                if var == 'lx' or var == 'LX' or var == 'lX':
                    var = 'Lx'
                if var == 'ly' or var == 'LY' or var == 'lY':
                    var = 'Ly'
                if var == 'lz' or var == 'LZ' or var == 'lZ':
                    var = 'Lz'

                setattr(self, var, val)

        # Close the file.
        f.close()

        # Double check that Nx, Ny, Nz have been assigned. If not, make them 1.
        if not(hasattr(self,'Nx')):
            setattr(self,'Nx',1)
        if not(hasattr(self,'Ny')):
            setattr(self,'Ny',1)
        if not(hasattr(self,'Nz')):
            setattr(self,'Nz',1)

        self.Nx = int(self.Nx)
        self.Ny = int(self.Ny)
        self.Nz = int(self.Nz)

        # Determine the number of dimensions
        # We're going to assume you aren't doing
        # a 1D simulation, so if any dimension
        # is a singleton, then it's a 2D simulation.

        if ((self.Nx == 1) |
            (self.Ny == 1) |
            (self.Nz == 1)):
        
            self.nd = 2
        
            # Also, Nz should be 1, not Ny
            #if self.Ny == 1:
            #    self.Ny = self.Nz
            #    self.Nz = 1
        else:
            self.nd = 3
        
        # Convert min_x,y,z to x,y,zlim
        for dim in ['x', 'y', 'z']:
            if (hasattr(self, 'min_'+dim) & hasattr(self, 'L'+dim)):
                min_ = getattr(self,'min_'+dim)
                max_ = getattr(self,'min_'+dim) + getattr(self,'L'+dim)
                setattr(self,dim+'lim', [min_, max_])
                


    def reader(self, var, *args, **kwargs):
        # This is a python version of the *_self.reader.m files
        # produced my SPINS for the purpose of parsing SPINS
        # outputs. The input arguments and usage are as follows:
        
        # var:
        #       type = str
        #       purpose: the variable to be loaded
        #       examples: 'rho', 'u', 'x'
        
        # seq:
        #       type = int (or integer-valued float)
        #       purpose: the time-step index
        #       examples: var = 'u', seq = 15 loads u.15
        
        # xs,ys,zs:
        #       type = int or list of ints
        #       purpose: slices the data at the appropriate indices
        #           if int (or 1-element list)
        #               - slices a single index
        #           if 2-element list [a,b]
        #               - shorthand for a:b-1
        #               - [0,-1] gets everything
        #           else
        #               - selects at the given indices
        
        # type (optional):
        #       type = str
        #       default = 'ndarray'
        #       purpose: Allows the user to choose if the output should
        #                be a numpy ndarray or the memory map object.
        #       options:
        #           'ndarray' (default): produces a numpy ndarray
        #           'memmap': returns the memory map
        
        # ordering (optional):
        #       type = str
        #       default = 'natural'
        #       purpose: Allows the user to choose natural (x,y,z) ordering,
        #                or MATLAB ordering (y,x,z).
        #       options:
        #           'natural' (default): [x,y,z] ordering
        #           'matlab': [y,x,z] ordering

        # Parse args
        nargs = len(args)
        if (var == 'x') | (var == 'y') | (var == 'z'):
            # Grids don't have seq arguments, only xs, ys, and zs.
            xs = args[0]
            ys = args[1]
            if nargs == 3:
                # 3 -> 3D
                zs = args[2]
            elif nargs == 2:
                # 2 -> 2D
                pass
            seq = 0
        else:
            seq = args[0]
            if nargs == 1:
                # If only gave var and seq, assume full domain
                xs = [0,-1]
                ys = [0,-1]
                if self.nd == 3:
                    zs = [0,-1]
            else:
                xs = args[1]
                ys = args[2]
                if nargs == 4:
                    # 4 -> 3D (less one for seq)
                    zs = args[3]
                elif nargs == 3:
                    # 3 -> 2D (less one for seq)
                    pass

        # Parse kwargs
        # We just need to check which keywords arguments
        # have been set and then set any missing ones.
        if 'ordering' in kwargs:
            ordering = kwargs['ordering']
        else:
            ordering = 'natural'

        if 'type' in kwargs:
            out_type = kwargs['type']
        else:
            out_type = 'ndarray'

        if 'force_name' in kwargs:
            force_name = kwargs['force_name']
        else:
            force_name = (seq < 0)

        # If 2D, get dimensions
        if self.nd == 2:
            if self.Nz == 1:
                dim1_len = self.Nx
                dim2_len = self.Ny
            if self.Ny == 1:
                dim1_len = self.Nx
                dim2_len = self.Nz
            if self.Nx == 1:
                dim1_len = self.Ny
                dim2_len = self.Nz

        # Parse the indexes
        if self.nd == 3:
            xs = Parse_Index(xs,0,self.Nx) # Defined at bottom of file
            ys = Parse_Index(ys,0,self.Ny)
            zs = Parse_Index(zs,0,self.Nz)
        elif self.nd == 2:
            xs = Parse_Index(xs,0,dim1_len)
            ys = Parse_Index(ys,0,dim2_len)

        # File to load
        if (var == 'x') | (var == 'y') | (var == 'z'):
            fname = '{0:s}{1:s}grid'.format(self.folder_path,var)
        else:
            if force_name:
                fname = '{0:s}{1:s}'.format(self.folder_path,var)
            else:
                fname = '{0:s}{1:s}.{2:d}'.format(self.folder_path,var,seq)

        # Does the requested file exist?
        if not(os.path.isfile(fname)):
            err_msg = 'The requested file, {0:s}, does not exist.'.format(fname)
            raise SillyHumanError(err_msg)

        # Determine endianness
        endian = sys.byteorder
        if endian == 'little':
            dt = np.dtype('<d')
        else:
            dt = np.dtype('>d')

        # Create the memory map
        if self.disc_order == 'xzy':
            the_shape = (self.Nx, self.Nz, self.Ny)
        elif self.disc_order == 'xyz':
            the_shape = (self.Nx, self.Ny, self.Nz)
        elif self.disc_order == 'zyx':
            the_shape = (self.Nz, self.Ny, self.Nx)
        elif self.disc_order == 'zxy':
            the_shape = (self.Nz, self.Nx, self.Ny)
        elif self.disc_order == 'yxz':
            the_shape = (self.Ny, self.Nx, self.Nz)
        elif self.disc_order == 'yzx':
            the_shape = (self.Ny, self.Nz, self.Nx)


        if self.nd == 3:
            m = np.memmap(fname, dtype=dt, mode='r',shape=the_shape)

            if self.disc_order == 'xzy':
                m = np.swapaxes(m, 1, 2) # Order to [x,y,z]
            elif self.disc_order == 'xyz':
                pass
            elif self.disc_order == 'zyx':
                m = np.swapaxes(m, 0, 2) 
            elif self.disc_order == 'zxy':
                m = np.swapaxes(m, 0, 2) 
                m = np.swapaxes(m, 0, 1) # Order to [x,y,z]
            elif self.disc_order == 'yxz':
                m = np.swapaxes(m, 0, 1) 
            elif self.disc_order == 'yzx':
                m = np.swapaxes(m, 1, 2)
                m = np.swapaxes(m, 0, 1)

            m = m[xs,:,:][:,ys,:][:,:,zs]
            m = np.squeeze(m)
            if ordering == 'matlab':
                m = np.swapaxes(m, 0, 1) # Order to [y,x,z] if desired.
            elif ordering != 'natural':
                # There are no other options, silly human.
                raise SillyHumanError('Ordering choice ({0:s}) not recognized.'.format(ordering))
        elif self.nd == 2:
            m = np.memmap(fname, dtype=dt, mode='r',
                        shape=(dim1_len,dim2_len))
            m = m[xs,:][:,ys]
            m = np.squeeze(m)
            if (ordering == 'matlab') and (self.Nz == 1):
                m = np.swapaxes(m, 0, 1) # Order to [y,x] if desired.
            elif ordering != 'natural':
                # There are no other options, silly human.
                raise SillyHumanError('Ordering choice ({0:s}) not recognized.'.format(ordering))


        if out_type == 'ndarray':
            m=m.view(type=np.ndarray)
        elif out_type == 'memmap':
            # Nothing to do
            pass
        else:
            # Raise an error .
            raise SillyHumanError('Requestion output type "{0:s}" is unknown.'.format(out_type))

        return m

def Parse_Index(ind, lb, ub):
    
    if isinstance(ind, collections.abc.Sequence):
    # If the input was a list (or tuple), then work with that
        if len(ind) == 1:
            # If it's a one-element list, treat that as a single slice request
            ind = [ind[0]]
        elif len(ind) == 2:
            # A 2-element list is short-hand. [a,b] -> a:b-1
            # Negative values are permitted, and refer to distance from end.
            if (ind[0] < lb):
                ind[0] = (ind[0] % ub) + 1
            if (ind[1] > ub):
                warnings.warn('Requested index exceeds size. Truncating request.')
                ind[1] = ub
            elif (ind[1] < 0):
                ind[1] = (ind[1] % ub) + 1
            ind = range(ind[0],ind[1])
    else:
        ind = [ind]


    return ind
## ------
