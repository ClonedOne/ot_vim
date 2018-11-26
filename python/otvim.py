print ("Hello from Python source code!")

class OTVim:
    def __init__(self, vim, autocmds=lambda: None):
        self._vim = vim
        self._autocmds = autocmds


    def start(self):
        self._buffer = self._vim.current.buffer

        self._autocmds()


    def stop(self):
        pass

    def check_buffer(self):
        pass
