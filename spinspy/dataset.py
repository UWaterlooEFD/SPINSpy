import collections
import os
import sys
import warnings

import numpy as np

from errors import SillyHumanError
from grid import Grid

class Dataset:

    def __init__(self, folder_path, disc_order: str='xzy'):

        self.disc_order = disc_order
        self.folder_path = folder_path
        self.grid = Grid(self.folder_path, disc_order)
        self.vars = {}

    
    def load_var(self, var: str):
        '''
        Creates a memory map to the variable file path
        Loads the variable into the dictionary "self.vars"

        Parameters
        ----------
        var: str
            one of 'x', 'y', 'z', 'u', 'v', 'w', 't', 's', 'rho'
            TODO: make sure there aren't more allowed inputs
        '''
    
        # Determine endianness
        endian = sys.byteorder
        if endian == 'little':
            dt = np.dtype('<d')
        else:
            dt = np.dtype('>d')
        
        the_shape = self.grid.get_dims()
        fname = self.folder_path + var +'.1'
        self.vars[var] = np.memmap(fname, dtype=dt, mode='r',shape=the_shape)