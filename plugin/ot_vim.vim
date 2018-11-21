if !has("python3")
    echo "OTVim Error: vim has to be compiled with +python3"
    finish
endif

if exists('g:ot_vim_loaded')
    finish
endif


let s:otvim_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
from os.path import normpath, join
import vim
otvim_root_dir = vim.eval('s:otvim_root_dir')
python_root_dir = normpath(join(otvim_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import otvim
EOF


let g:ot_vim_loaded = 1
