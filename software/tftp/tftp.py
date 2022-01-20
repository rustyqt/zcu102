import sys
sys.path.insert(0, '../axidma/')

import tftpy

from axidma import axidma
from axidmabuf import axidmabuf

class tftp():
    """ Class for TFTPS transfers"""
    def __init__(self, dma):
        """ 
        Description:
            TFTP class constructor.
        """
        self.dma = dma        
    
    def config(self, host : str, port : int = 69, blksize : int = 512) -> int:
        
        options = {}
        options['blksize'] = blksize
        self.client = tftpy.TftpClient(host, port, options)

        return 0

    def download(self, remote_filename : str, local_filename : str, dma : bool) -> int:
        """ 
        Description:
           Downloads remote file from TFTP Server to local file.
        
        Parameters:
            remote_filename  <str> : Remote file name (server)
            local_filename   <str> : Local file name (client)
            dma             <bool> : True  : local_filename is DMA buffer ID
                                     False : local_filename is file
        Returns:
            ret     <int> : 0 = Success
                            1 = Failed
        """
        

        if dma:
            fp = axidmabuf(self.dma, local_filename)
            self.client.download(remote_filename, fp)
        else:
            self.client.download(remote_filename, local_filename)

        return 0

    def upload(self, remote_filename : str, local_filename : str, dma : bool) -> int:
        """ 
        Description:
           Uploads local file to TFTP Server.
        
        Parameters:
            remote_filename  <str> : Remote file name (server)
            local_filename   <str> : Local file name (client)
        Returns:
            ret     <int> : 0 = Success
        """

        if dma:
            fp = axidmabuf(self.dma, local_filename)
            self.client.upload(remote_filename, fp)
        else:
            self.client.upload(remote_filename, local_filename)
        
        return 0