from spinspy_classes import Params, SillyHumanError
import os
from spinspy import local_data

## Determine simulation parameters
## Purpose:
##     If spins.conf exists
##         parse spins.conf
##     Else
##         Raise error
##
## Usage:
##     data = spinspy.get_params()
##
##     data.display() prints a summary
##                    of known values
## ------
def get_params():

    param_data = Grid()
   
    if os.path.realpath(local_data.path) == local_data.conf_path:
        # We've already loaded it, so just return the stored variable
        param_data = local_data.param_data
    else:
        # Check if a spins.conf file exists,
        # if it does, parse it.
        conf_path = '{0:s}spins.conf'.format(local_data.path)
        if os.path.isfile(conf_path):
            try:
                param_data = spinsconf_parser(param_data)
            except:
                msg = 'Failed to read parameters from spins.conf. Put grid parameters in spins.conf.'
                raise SillyHumanError(msg)
        else:
            msg = 'Cannot locate {0:s}. Create a spins.conf and try again.'.format(conf_path)
            raise SillyHumanError(msg)

        # Store for future reference
        local_data.conf_path = os.path.realpath(local_data.path)
        local_data.param_data = param_data

    return param_data
## ------


## Parser for spins.conf
## ------
def spinsconf_parser(param_data):
    # Open the file for reading only.
    conf_path = '{0:s}spins.conf'.format(local_data.path)
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

            setattr(param_data, var, val)

    # Close the file.
    f.close()

    # Double check that Nx, Ny, Nz have been assigned. If not, make them 1.
    if not(hasattr(param_data,'Nx')):
        setattr(param_data,'Nx',1)
    if not(hasattr(param_data,'Ny')):
        setattr(param_data,'Ny',1)
    if not(hasattr(param_data,'Nz')):
        setattr(param_data,'Nz',1)

    param_data.Nx = int(param_data.Nx)
    param_data.Ny = int(param_data.Ny)
    param_data.Nz = int(param_data.Nz)

    # Determine the number of dimensions
    # We're going to assume you aren't doing
    # a 1D simulation, so if any dimension
    # is a singleton, then it's a 2D simulation.

    if ((param_data.Nx == 1) |
        (param_data.Ny == 1) |
        (param_data.Nz == 1)):
    
        param_data.nd = 2
    
        # Also, Nz should be 1, not Ny
        #if param_data.Ny == 1:
        #    param_data.Ny = param_data.Nz
        #    param_data.Nz = 1
    else:
        param_data.nd = 3
    
    # Convert min_x,y,z to x,y,zlim
    for dim in ['x', 'y', 'z']:
        if (hasattr(param_data, 'min_'+dim) &\
            hasattr(param_data, 'L'+dim)):
            setattr(param_data,dim+'lim',\
                    [getattr(param_data,'min_'+dim),\
                     getattr(param_data,'min_'+dim) + \
                     getattr(param_data,'L'+dim)])

    return param_data
## ------
