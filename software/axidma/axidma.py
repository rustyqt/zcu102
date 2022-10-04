import ctypes

class axidma_dev(ctypes.Structure):
    _fields_ = []

class array(ctypes.Structure):
    _fields_=[("len", ctypes.c_int),
              ("data", ctypes.POINTER(ctypes.c_int))]

class axidma():
    """ Class for AXIDMA transfers"""
    def __init__(self):
        """ 
        Description:
            AXI DMA class constructor.
        """

        # Send data to AES GCM via AXI DMA
        self.clib = ctypes.CDLL("/home/root/software/axidma/lib/libaxidma.so")

        # Define return types
        self.clib.axidma_init.restype            = ctypes.POINTER(axidma_dev)
        self.clib.axidma_get_dma_tx.restype      = ctypes.POINTER(array)
        self.clib.axidma_get_dma_rx.restype      = ctypes.POINTER(array)      
        self.clib.axidma_malloc.restype          = ctypes.POINTER(ctypes.c_char)
        self.clib.axidma_twoway_transfer.restype = ctypes.c_int
        self.clib.axidma_oneway_transfer.restype = ctypes.c_int
        
        # Dictionaries for storing buffers and their sizes created with malloc()
        self.buf = {}
        self.size = {}

        # AXI DMA Init
        print("AXI DMA Init")
        self.dev = self.clib.axidma_init()
        assert self.dev != None, "Error: Failed to initialize the AXI DMA device."
        
        tx_ch_arr = self.clib.axidma_get_dma_tx(self.dev)
        rx_ch_arr = self.clib.axidma_get_dma_rx(self.dev)

        print("Found " + str(tx_ch_arr.contents.len) + " TX DMA channel(s).")
        print("Found " + str(rx_ch_arr.contents.len) + " RX DMA channel(s).")
        
        assert tx_ch_arr.contents.len >= 1, "Error: No TX DMA channel found."
        assert rx_ch_arr.contents.len >= 1, "Error: No RX DMA channel found."

        self.tx_ch = []
        for i in range(tx_ch_arr.contents.len):
            self.tx_ch.append(tx_ch_arr.contents.data[i])
        
        self.rx_ch = []
        for i in range(rx_ch_arr.contents.len):
            self.rx_ch.append(rx_ch_arr.contents.data[i])

        print("TX DMA channel number(s): " + str(self.tx_ch))
        print("RX DMA channel number(s): " + str(self.rx_ch))

    def malloc(self, buf_id : str, size : int) -> int:
        """ 
        Description:
           Allocates physical memory for DMA purposes
        
        Parameters:
            buf_id  <str> : Unique Buffer ID
            size    <int> : Size of allocated buffer in bytes
        Returns:
            ret     <int> : 0 = Success
                            1 = Failure
        """
        assert buf_id not in self.buf, "Error: DMA Buffer ID already exists"
        assert buf_id not in self.size, "Error: DMA Buffer ID already exists"
        
        # Allocate Memory for DMA buffer
        self.buf[buf_id]  = self.clib.axidma_malloc(self.dev, size)
        assert self.buf[buf_id] != None, "Error: Failed to allocate DMA output buffer"
        
        # Store size of new DMA buffer
        self.size[buf_id] = size
        
        return 0
    
    def free(self, buf_id : str) -> int:
        """ 
        Description:
           Frees physical memory for DMA purposes
        
        Parameters:
            buf_id  <str> : Unique Buffer ID
        Returns:
            ret     <int> :  0 = Success
                            -1 = DMA Buffer is not allocated
                            -2 = DMA Buffer not found
                            -3 = No DMA Device found
        """
        # Cleanup Resources
        if self.dev != None:
            # Free memory
            if buf_id in self.buf:
                if self.buf[buf_id] != None:
                    self.clib.axidma_free(self.dev, self.buf[buf_id], self.size[buf_id])
                    del(self.buf[buf_id])
                    del(self.size[buf_id])
                    return 0
                else:
                    return -1
            else:
                return -2
        else:
            return -3



    def oneway_transfer(self, dir : int, ch_id : int, buf_id : str, buf_len : int) -> int:
        """ 
        Description:
            Performs one-way DMA transfer
        
        Parameters:
            dir     <int> : 0 = TX (PS -> PL)
                            1 = RX (PL -> PS)
            ch_id   <int> : Selects channel
            buf_id  <str> : DMA buffer ID specified at malloc() call
            buf_len <int> : Data in bytes to be transferred
        """
        print("Run AXI DMA one-way transfer")
        if dir == 0:
            channel = self.tx_ch[ch_id]
        else:
            channel = self.rx_ch[ch_id]
        
        ret = self.clib.axidma_oneway_transfer(self.dev, channel, self.buf[buf_id], buf_len, True)

        assert ret == 0, "Error: AXI DMA one-way transfer failed!"
        return 0

    def twoway_transfer(self,   tx_ch_id : int, tx_buf_id : str, tx_buf_len : int, 
                                rx_ch_id : int, rx_buf_id : str, rx_buf_len : int, wait : bool = True) -> int:
        """ 
        Description:
            Performs two-way DMA transfer, from self.ibuf and to self.obuf.
        
        Parameters:
            tx_ch_id    <int> : TX Channel ID
            tx_buf_id   <str> : TX DMA buffer ID
            tx_buf_len  <int> : Data in bytes to be send
            rx_ch_id    <int> : RX Channel ID
            rx_buf_id   <str> : RX DMA buffer ID
            rx_buf_len  <int> : Data in bytes to be received
        """
        print("Run AXI DMA two-way transfer")
        assert self.size[tx_buf_id] >= tx_buf_len, "Error: TX DMA buffer size not large enough."
        assert self.size[rx_buf_id] >= rx_buf_len, "Error: RX DMA buffer size not large enough."

        tx_channel = self.tx_ch[tx_ch_id]
        rx_channel = self.rx_ch[rx_ch_id]

        # Run AXI DMA two-way transfer
        ret = self.clib.axidma_twoway_transfer(self.dev, \
                                        tx_channel, self.buf[tx_buf_id], tx_buf_len, None, \
                                        rx_channel, self.buf[rx_buf_id], rx_buf_len, None, wait)
        
        assert ret == 0, "Error: AXI DMA two-way transfer failed!"
        return 0
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Description:
            Print exceptions and clean-up resources
        """
        # Print Exception
        if exception_type != None:
            print(str(exception_type) + ": " + str(exception_value))
            print(str(exception_traceback))
        
        # Cleanup Resources
        if self.dev != None:
            # Free memory
            for buf_id in self.buf:
                if self.buf[buf_id] != None:
                    self.clib.axidma_free(self.dev, self.buf[buf_id], self.size[buf_id])
            
            # Destroy device
            self.clib.axidma_destroy(self.dev)
            del(self.dev)
