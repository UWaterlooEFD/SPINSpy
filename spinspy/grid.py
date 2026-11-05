import collections
import os
import sys

import numpy as np

from errors import SillyHumanError

class Grid:

    def __init__(self, folder_path, disc_order):

        self.folder_path = folder_path

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
        self.min_x = None
        self.min_y = None
        self.min_z = None
        self.xlim = None
        self.ylim = None
        self.zlim = None
    
        # Grid types
        self.type_x = None
        self.type_y = None
        self.type_z = None

        # whether grid is mapped or not
        self.mapped_grid = None
        self.load_grid_params()
        #TODO: chebyshev needs to be worked out somehow
        self.x = np.arange(self.xlim[0]+self.Lx/self.Nx, self.xlim[1]+self.Lx/self.Nx, self.Lx/self.Nx)
        self.y = np.arange(self.ylim[0]+self.Ly/self.Ny, self.ylim[1]+self.Ly/self.Ny, self.Ly/self.Ny)
        self.z = np.arange(self.zlim[0]+self.Lz/self.Nz, self.zlim[1]+self.Lz/self.Nz, self.Lz/self.Nz)


    def load_grid_params(self):
        '''
        Updates the class attributes by reading the grid-related parameters
        in 'spins/conf'
        '''
        # Open the file for reading only.
        conf_path = '{0:s}spins.conf'.format(self.folder_path)
        f = open(conf_path, 'r')

        # List of case sensitive var names (in lowercase)
        case_sensitive_var_names = ['nx', 'ny', 'nz', 'lx', 'ly', 'lz']

        # Loop through each line.
        # Lines are assumed to be of the form:
        # key = val \n
        # Comments are preceded by '#'
        for line in f:
            # Skip blank and comment lines
            if len(line)<=0 or ((len(line) > 0) and (line[0] == '#')):
                continue

            line_split = line.split(sep="=")

            # Skip invalid lines (with complaints)
            if (len(line_split) != 2):
                #TODO: Add warning here!
                continue

            var_name = line_split[0].strip()
            var_val = line_split[1].strip()

            # Try to parse as an int, float, then string (in that order)
            try:
                if (var_val.isdecimal()):
                    var_val = int(var_val)
                else:
                    var_val = float(var_val)
            except ValueError:
                var_val = var_val

            # Check if var_name is in the list of case sensitive var names
            # Example: 'nX', 'nx', 'NX', 'Nx' should all be mapped to 'Nx'
            if var_name.lower() in case_sensitive_var_names:
                var_name = var_name.title()

            # If it is defined as a grid param, load it, otherwise skip
            if (hasattr(self, var_name)):
                setattr(self, var_name, var_val)
        f.close()

        if ((self.Nx is None) | (self.Ny is None) | (self.Nx is None)):
            self.nd = 2
        else:
            self.nd = 3

        if (self.min_x is not None):
            self.xlim = [self.min_x, self.min_x + self.Lx]
        else:
            self.xlim = [0, self.Lx]
        if (self.min_y is not None):
            self.ylim = [self.min_y, self.min_y + self.Ly]
        else:
            self.ylim = [0, self.Ly]
        if (self.min_z is not None):
            self.zlim = [self.min_z, self.min_z + self.Lz]
        else:
            self.zlim = [0, self.Lz]
        
    
    def get_dims(self):
        #TODO: this needs to be changed
        return (self.Nx, self.Ny, self.Nz)
        



