class axidmabuf():
    """File-like object for DMA buffers.

    For loading read(), tell() and seek() have to be implemented. "name"
    is optional.

    For saving/deleting write(), flush() and truncate() have to be
    implemented in addition. fileno() is optional.
    """

    def __init__(self, dma, buf_id : str):
        """ 
        Description:
            AXI DMA class constructor.
        """
        self.dma = dma
        self.buf_id = buf_id
        self.offset = 0
        self.closed = False

    def close(self):
        self.closed = True

    def tell(self):
        """Returns he current offset as int. Always >= 0.

        Raises IOError in case fetching the position is for some reason
        not possible.
        """

        raise NotImplementedError

    def read(self, size=-1):
        """Returns 'size' amount of bytes or less if there is no more data.
        If no size is given all data is returned. size can be >= 0.

        Raises IOError in case reading failed while data was available.
        """

        assert self.buf_id in self.dma.buf, "DMA Buffer ID not found."
        assert self.buf_id in self.dma.size, "DMA Buffer ID not found."
        
        if size == -1:
            size = self.dma.size[self.buf_id]
        else:
            if self.dma.size[self.buf_id] < self.offset+size:
                _size = self.dma.size[self.buf_id] - self.offset
            else:
                _size = size

        data = self.dma.buf[self.buf_id][self.offset:self.offset+_size]
        self.offset += size
        return data


    def seek(self, offset, whence=0):
        """Move to a new offset either relative or absolute. whence=0 is
        absolute, whence=1 is relative, whence=2 is relative to the end.

        Any relative or absolute seek operation which would result in a
        negative position is undefined and that case can be ignored
        in the implementation.

        Any seek operation which moves the position after the stream
        should succeed. tell() should report that position and read()
        should return an empty bytes object.

        Returns Nothing.
        Raise IOError in case the seek operation asn't possible.
        """

        raise NotImplementedError

    # For loading, but optional

    @property
    def name(self):
        """Should return text. For example the file name.

        If not available the attribute can be missing or can return
        an empty string.

        Will be used for error messages and type detection.
        """

        raise NotImplementedError

    # For writing

    def write(self, data):
        """Write data to the file.

        Returns Nothing.
        Raises IOError
        """
        
        assert self.dma.size[self.buf_id] >= len(data), "Error: DMA buffer size not large enough." 
        assert self.buf_id in self.dma.buf, "DMA Buffer ID not found."
        
        #TODO: Improve Performance of this for loop!
        for i in range(len(data)):
            self.dma.buf[self.buf_id][self.offset+i] = data[i]

        self.offset += len(data)

    def truncate(self, size=None):
        """Truncate to the current position or size if size is given.

        The current position or given size will never be larger than the
        file size.

        This has to flush write buffers in case writing is buffered.

        Returns Nothing.
        Raises IOError.
        """

        raise NotImplementedError

    def flush(self):
        """Flush the write buffer.

        Returns Nothing.
        Raises IOError.
        """

        raise NotImplementedError

    # For writing, but optional

    def fileno(self):
        """Returns the file descriptor (int) or raises IOError
        if there is none.

        Will be used for low level operations if available.
        """

        raise NotImplementedError