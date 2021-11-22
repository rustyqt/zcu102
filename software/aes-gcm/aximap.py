import json
import struct

import mmap

class aximap():
    """ Class for AXI mmap based register access """
    def __init__(self, base_addr, regfile_path="./aes-gcm_regfile.json"):
        """ 
        Description:
            AXIMAP class constructor. Reads <regfile_path>.json to build up internal register map.
        
        Parameters:
            base_addr <int> : Defines physical base address of the module
            regfile_path <string> : Defines the path to the json file
        
        Return:
            aximap <aximap> : AXIMAP object returned by constructor
        """

        # Mmap devmem
        self.f_mem = open("/dev/mem", "r+b")
        self.devmem = mmap.mmap(f_mem.fileno(), 4096, offset=base_addr)
        
        # Open JSON file
        f = open(regfile_path, encoding="utf-8")
        regfile = json.load(f)
        f.close()

        # Create dictionaries
        self.map = { }
        self.len = { }
        self.access = { }
        self.rstval = { }
        self.mask = { }
        self.pos = { }
        self.dtype = { }
        self.rtype = { }
        self.desc = { }
        
        self.unit = { }
        self.rmin = { }
        self.rmax = { }
        
        self.a0 = { }
        self.a1 = { }
        self.a2 = { }
        
        
        self.actuals = { } # Actuals
        self.actdesc = { } # Description of actual
        self.actstr = { }  # String representative of actual
        
        dtype_dict = {"std_logic": "uchar",
                      "std_logic_vector": "uchar",
                      "unsigned": "uint16",
                      "signed": "int16"}
        
        cur_addr = 0
        for reg_if in regfile['interfaces']:
            for reg in reg_if['registers']:
                
                if 'fields' not in reg:
                    _regname = reg['name']
                    
                    self.rstval[_regname] = reg['reset']
                    self.dtype[_regname] = dtype_dict[reg['signal']]
                    self.rtype[_regname] = 1

                        
                    self.mask[_regname] = 0xffff_ffff
                    self.pos[_regname] = 0
                    
                    
                    if reg['address'].find(":stride:") != -1:
                        addr_array = reg['address'].split(":")
                        if addr_array[0] == "auto":
                            self.map[_regname] = cur_addr
                        else:
                            self.map[_regname] = int(addr_array[0], 0)
                        self.len[_regname] = int(addr_array[2])
                    else:
                        if reg['address'] == "auto":
                            self.map[_regname] = cur_addr
                        else:
                            self.map[_regname] = int(reg['address'], 0)
                        self.len[_regname] = 1
                    
                    self.access[_regname] = reg['access']
                    
                    # Exception for RO area
                    if self.map[_regname] >= 0x180:
                        self.access[_regname] = "RO"
                    

                    reginfo_start = reg['description'][0].find("{")
                    reginfo_end = reg['description'][0].find("}")
                    if reginfo_start != -1 and reginfo_end != -1:
                        self.desc[_regname] = [ reg['description'][0][:reginfo_start-1] ]
                        reginfo = json.loads(reg['description'][0][reginfo_start:reginfo_end+1].replace("'", "\""))
                        self.unit[_regname] = reginfo['unit']
                        self.rmin[_regname] = reginfo['rmin']
                        self.rmax[_regname] = reginfo['rmax']
        
                        self.a0[_regname] = reginfo['a0']
                        self.a1[_regname] = reginfo['a1']
                        self.a2[_regname] = reginfo['a2']
                    else:
                        self.desc[_regname] = reg['description']
                        self.unit[_regname] = ""
                        self.rmin[_regname] = ""
                        self.rmax[_regname] = ""
        
                        self.a0[_regname] = ""
                        self.a1[_regname] = ""
                        self.a2[_regname] = ""
                            
                if 'fields' in reg:
                    
                    if len(reg['fields']) > 1:
                        _regname = reg['name']
                        self.access[_regname] = reg['fields'][0]['access']
                        self.rstval[_regname] = ""
                        self.dtype[_regname] = "array"
                        self.rtype[_regname] = 1
                        if reg['address'] == "auto":
                            self.map[_regname] = cur_addr
                        else:
                            self.map[_regname] = int(reg['address'], 0)
                        #self.mask[_regname] = 0xffff_ffff
                        self.pos[_regname] = 0
                        self.len[_regname] = 1
                        self.desc[_regname] = reg['description']
                        self.unit[_regname] = ""
                        self.rmin[_regname] = ""
                        self.rmax[_regname] = ""
                        self.a0[_regname] = ""
                        self.a1[_regname] = ""
                        self.a2[_regname] = ""
                        
                        
                    for field in reg['fields']:          
                        # Define register name
                        _regname = reg['name'] + "_" + field['name']
                        if reg['address'] == "auto":
                            self.map[_regname] = cur_addr
                        else:
                            self.map[_regname] = int(reg['address'], 0)
                        self.len[_regname] = 1
                        self.desc[_regname] = field['description']
                        self.access[_regname] = field['access']
                        self.rstval[_regname] = field['reset']
                        self.dtype[_regname] = dtype_dict[field['signal']]
                        self.rtype[_regname] = 0
                            
                        if len(reg['fields']) == 1:
                            self.rtype[_regname] = 1    
                        
                        mask = 0
                        if field['position'].find(":") == -1:
                            mask = (1<<int(field['position'])) & 0xFFFF_FFFF
                            self.pos[_regname] = int(field['position'])
                        else:
                            pos_array = field['position'].split(":")
                            for i in range(int(pos_array[1]), int(pos_array[0])+1):
                                mask = mask | ((1<<i) & 0xFFFF_FFFF)
                            self.pos[_regname] = int(pos_array[1])
                            
                        self.mask[_regname] = mask
                        
                        # Add register information
                        reginfo_start = field['description'][0].find("{")
                        reginfo_end = field['description'][0].find("}")
                        if reginfo_start != -1 and reginfo_end != -1:
                            self.desc[_regname] = [ field['description'][0][:reginfo_start-1] ]
                            reginfo = json.loads(field['description'][0][reginfo_start:reginfo_end+1].replace("'", "\""))
                            self.unit[_regname] = reginfo['unit']
                            self.rmin[_regname] = reginfo['rmin']
                            self.rmax[_regname] = reginfo['rmax']
            
                            self.a0[_regname] = reginfo['a0']
                            self.a1[_regname] = reginfo['a1']
                            self.a2[_regname] = reginfo['a2']
                        else:
                            self.unit[_regname] = ""
                            self.rmin[_regname] = ""
                            self.rmax[_regname] = ""
            
                            self.a0[_regname] = ""
                            self.a1[_regname] = ""
                            self.a2[_regname] = ""        
                        
                        # Add actuals information
                        actuals_dict = { }
                        actdesc_dict = { }
                        actstr_dict = { }
                                
                        for desc in field['description']:
                            
                            desc_array = desc.split(":")
                        
                            if len(desc_array) != 1:
                                value = desc_array[0]
                                desc_array = desc_array[1].split(" - ")
                                
                                if len(desc_array) != 1:
                                    name_calib = desc_array[0].strip()
                                    
                                    actuals_dict[name_calib] = int(value, 0)
                                    actdesc_dict[name_calib] = desc_array[1]
                                    actstr_dict[int(value, 0)] = name_calib
                                    
                                    self.actuals[_regname] = actuals_dict
                                    self.actdesc[_regname] = actdesc_dict
                                    self.actstr[_regname] = actstr_dict
                
                # Keep cur_addr up-to-date
                cur_addr = cur_addr + 4*self.len[_regname]

    def help(self, name=None):
        """ 
        Description:
            Displays this message or detailed help to AXIMAP registers 
            
        Parameters: 
            name <NoneType> : None - Prints this message
            name <all> : all - prints all registers
            name <string> : '<REG_NAME>' - Prints detailed register description of REG_NAME
            
        Return:
            void
        """
        
        if name == None:
            help(self)
            print("Usage: aximap.help()               Print this help.")
            print("       aximap.help(all)            List all registers")
            print("       aximap.help('<REG_NAME>')   Print register description")
        
        if name == all:
            print("<ADDR>: <REG_NAME>")
            for reg in self.map:
                print("{0:#0{1}x}".format(self.map[reg],6) + ": " + reg)
        
        if type(name) == str:
            desc = self.desc[name]
            for line in desc:
                print(line)


    def rd(self, reg, exp_val=None, n_regs=1, actstr=True, debug=False):
        """ 
        Description:
            Read IVAE registers by addr or mnemonic 
        
        Parameters:
            reg <str> : Select register by its name
            reg <int> : Select register by its address
            
            exp_val <None> : No expected value required
            exp_val <str>  : Set register value by mnemonic
            exp_val <int>  : Set register value to integer value provided
            exp_val <list> : Set len(val) consecutive register to integers values provided in list
            
            n_regs <int> : Number of consecutive registers to be read.
            
            actstr <bool> : False: Returns integer value of register. True: Returns string mnemonic.
            
            debug <bool> : If set to true, verbose debug output is printed to console.
            
        Return:
            _ret <int> : Returns integer value of register.
            _ret <string> : Returns string mnemonic of register value.
        """
        
        if type(reg) == str and type(exp_val) == str:
            _reg = self.map[reg]
            _pos = self.pos[reg]
            _len = self.len[reg]
            #_exp_val = self.actuals[reg][exp_val]<<self.pos[reg]
            _exp_val = exp_val
            try:
                _mask = self.mask[reg]
            except:
                _mask = 0xffff
        elif type(reg) == str and type(exp_val) != str:
            _reg = self.map[reg]
            try:
                _mask = self.mask[reg]
            except:
                _mask = 0xffff
            _pos = self.pos[reg]
            _len = self.len[reg]
            if type(exp_val) == list:
                _exp_val = exp_val
            elif type(exp_val) == int:
                _exp_val = (exp_val<<self.pos[reg])&_mask
            else:
                _exp_val = None
        elif type(reg) != str and type(exp_val) == str:
            raise TypeError("If <reg> is provided as <int>, you can't provide <val> as <str>")
        else:
            _reg = reg
            _pos = 0
            _len = n_regs
            _mask = 0xffff
            _exp_val = exp_val
        
        _ret = [ ]
        __len = _len
        __reg = _reg
        while __len > 32:
            _ret += self.tmtc.get_reg(__reg, 32, debug)
            __len -= 32
            __reg += 32*2
        
        _ret += self.tmtc.get_reg(__reg, __len, debug)
                
        if _len == 1:
            _ret = ((_ret[0] & _mask) >> _pos)
            if actstr:
                if reg in self.actstr:
                    if _ret in self.actstr[reg]:
                        _ret = self.actstr[reg][_ret]
                    else:
                        #raise ValueError("Actual not corresponding to any actstr.")
                        pass
        
        if _len == 2:
            _ret = (_ret[0]<<16) + _ret[1]
            
        if debug:
            log.debug("ivae.rd(): _reg: " + "{0:#0{1}x}".format(_reg,6))
            log.debug("ivae.rd(): _ret: " + str(_ret))
        
        if exp_val != None:
            if _ret == _exp_val:
                log.error("IVAE: Register " + str(reg) + ". Expected value does match actual ( " + str(_ret) + ").")
            else:
                log.error("IVAE: Register " + str(reg) + ". Expected value ( " + str(_exp_val) + " ) does not match actual ( " + str(_ret) + ").")
            
        return _ret
    
    def wr(self, reg, val, debug=False):
        """ 
        Description:
            Write IVAE registers by addr or mnemonic.
        
        Parameters:
            reg <str> : Select register by its name
            reg <int> : Select register by its address
            
            val <str> : Set register value by mnemonic
            val <int> : Set register value to integer value provided
            val <list> : Set len(val) consecutive register to integers values provided in list
            
            debug <bool> : If set to true, verbose debug output is printed to console.
            
        Return:
            0 <int> : Success
        """
        if type(reg) == str and type(val) == str:
            _reg = self.map[reg]
            _mask = self.mask[reg]
            _val = self.actuals[reg][val]<<self.pos[reg]
        elif type(reg) == str and type(val) != str:
            _reg = self.map[reg]
            _mask = self.mask[reg]
            if type(val) == list:
                _val = val
            else:
                _val = (val<<self.pos[reg])&_mask
        elif type(reg) != str and type(val) == str:
            raise TypeError("If <reg> is provided as <int>, you can't provide <val> as <str>")
        else:
            _reg = reg
            _val = val
            _mask = 0xffff_ffff            
        
        if type(reg) == str:
            if self.rmin[reg] != "":
                if int(self.rmin[reg], 0) > _val:
                    raise ValueError("_val < rmin["+reg+"] = " + self.rmin[reg])
            if self.rmax[reg] != "":
                if int(self.rmax[reg], 0) < _val:
                    raise ValueError("_val > rmax["+reg+"] = " + self.rmax[reg])
                    
        # Read-Modify-Write
        if _mask != 0xffff_ffff:
            old_regval = 0
            old_regval = self.tmtc.get_reg(_reg)[0]
            _val |= (old_regval & ~_mask)
        
        if type(_val) == list:
            offset = 0
            for __val in _val:
                self.devmem[self.base_addr+_reg+offset:self.base_addr+_reg+offset+4] = __val
                offset = offset + 4
        elif type(_val) == bytes:
            for i in range(len(_val)/4):
                self.devmem[self.base_addr+_reg+i*4:self.base_addr+_reg+(i+1)*4] = _val[i*4:(i+1)*4]
        else:
            self.devmem[self.base_addr+_reg:self.base_addr+_reg+4] = _val
        
        return 0


    def close(self):
        f_mem.close()
        devmem.close()