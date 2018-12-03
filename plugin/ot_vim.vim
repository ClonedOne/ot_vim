if !has("python3")
    echo "OTVim Error: vim has to be compiled with +python3"
    finish
endif

if exists('g:ot_vim_loaded')
    finish
endif


let s:otvim_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

com! -nargs=* OTVim py3 otv_plugin.start(<f-args>)
com! OTVimStop py3 otv_plugin.stop()

python3 << EOF
import sys
from os.path import normpath, join
import vim

otvim_root_dir = vim.eval('s:otvim_root_dir')
python_root_dir = normpath(join(otvim_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)

import otvim


class OTVimPlugin:

    def __init__(self):
        self._otv = otvim.OTVim(
            vim=vim,
            autocmds=self.autocommands
        )

    def autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd TextChangedI <buffer> python3 otv_plugin.check_buffer_wrap()')
        # vim.command('autocmd TextChanged <buffer> python3 otv_plugin.check_buffer_wrap()')
        vim.command('autocmd VimLeave * python3 otv_plugin.stop()')

    def check_buffer_wrap(self):
        self._otv.check_buffer()

    def start(self, name, host, port):
        self._otv.start(name, host, port)

    def stop(self):
        self._otv.stop()



otv_plugin = OTVimPlugin()


EOF


let g:ot_vim_loaded = 1
