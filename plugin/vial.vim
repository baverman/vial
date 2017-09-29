if exists("g:loaded_vial") || &compatible
    finish
endif

if !exists("g:vial_python")
    if has("python")
        let g:vial_python = "python"
    elseif has("python3")
        let g:vial_python = "python3"
    endif
endif

if !exists("g:vial_python") || !has(g:vial_python)
    echohl ErrorMsg
    echon "vial requires python or python3 support"
    finish
endif

let g:loaded_vial = "true"

function! VialGetKey()
    try
        if getchar(1)
            let chr = getchar()
            if chr != 0
                let chr = nr2char(chr)
            endif
        else
            let chr = ''
        endif
    catch /^Vim:Interrupt$/
        let chr = "\<esc>"
    endtry

    return chr
endfunction

if g:vial_python == "python"
augroup autovial
    autocmd VimEnter * python vial.init()
augroup END

python << EOF
import sys
import os.path
import vim
rtp = vim.eval('&runtimepath')
for p in rtp.split(','):
    if os.path.exists(os.path.join(p, 'vial', '__init__.py')):
        sys.path.insert(0, p)
        break

import vial
EOF
else
augroup autovial
    autocmd VimEnter * python3 vial.init()
augroup END

python3 << EOF
import sys
import os.path
import vim
rtp = vim.eval('&runtimepath')
for p in rtp.split(','):
    if os.path.exists(os.path.join(p, 'vial', '__init__.py')):
        sys.path.insert(0, p)
        break

import vial
EOF
endif
