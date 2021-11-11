# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 16:20:30 2021

@author: julian.sarcher
"""

import struct

import numpy as np
import logging as log
from progressbar import progressbar, Bar, Percentage, ETA
from functools import reduce
import operator

def prbs7(shape, seed=0x7F, fromfile=False):
    """ Calculates a PRBS7 sequence """
    log.info("PRBS: Generate PRBS7 sequence (seed = " + hex(seed) + ", shape = " + str(shape) + ")" )
    
    if fromfile:
        filename = "data/prbs7_" + str(shape).replace(", ","_").replace("[","").replace("]","") + "_" + hex(seed) + ".raw"
    else:
        filename = None
    
    # If PRBS sequence has been generated already read from file, else generate the PRBS sequence.
    try:
        ret = np.fromfile(filename, dtype=">u2")
        ret.shape = shape
    except:
        ret = prbs(7, 6, False, shape, 16, seed, filename)
        
    return ret
        
def prbs15(shape, seed=0x7FFF, fromfile=False):
    """ Calculates PRBS15 sequence """
    log.info("PRBS: Generate PRBS15 sequence (seed = " + hex(seed) + ", shape = " + str(shape) + ")" )
    
    if fromfile:
        filename = "data/prbs15_" + str(shape).replace(", ","_").replace("[","").replace("]","") + "_" + hex(seed) + ".raw"
    else:
        filename = None
    
    # If PRBS sequence has been generated already read from file, else generate the PRBS sequence.
    try:
        ret = np.fromfile(filename, dtype=">u2")
        ret.shape = shape
    except:
        ret = prbs(15, 14, True, shape, 16, seed, filename)
        
    return ret
    
def prbs(poly_len, poly_tap, inv_pattern, shape, dwidth, seed, filename=None):
    """ Calculates any PRBS sequence by specifying poly_len, poly_tap, inversion, seq_len, data width and initial seed. 
        Warning: This function is computational intensive. """
    
    # Use seed as initial code
    code = seed
    
    if type(shape) == list:
        seq_len = reduce(operator.mul, shape, 1)
    elif type(shape) == int:
        seq_len = shape
    uint_mask = pow(2,dwidth)-1
    
    prbs_sequence = []
    
    if seq_len < 100000:
        it = range(seq_len)
    else:
        it = progressbar(range(seq_len), widgets=[Percentage(), ' ', Bar(), ' ', ETA()])
        
    # Generate PRBS sequence
    for i in it:
        prbs_word = 0
        for ii in range(dwidth):
            #Calculate PRBS bit
            code = ((code<<1) | (((code>>(poly_len-1)) ^ (code>>(poly_tap-1))) & 0x01)) & 0xFFFF
            
            # Construct PRBS word (least significant bit transmitted first)
            prbs_word |= (code&0x01)<<ii
            
        if inv_pattern:
            prbs_word_out = ~prbs_word & uint_mask
        else:
            prbs_word_out = prbs_word
            
        prbs_sequence.append(prbs_word_out)

    # Convert to numpy array
    seq = np.array(prbs_sequence, dtype=">u2")
    seq.shape = shape
    
    # Write to file if requested
    if filename != None:
        seq.tofile(filename)
    
    # Return PRBS sequence
    return seq


