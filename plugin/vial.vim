if exists("g:loaded_vial") || &compatible
    finish
endif

if !has("python")
    echohl ErrorMsg
    echon "vial requires python support"
    finish
endif

let g:loaded_vial = "true"

augroup autovial
    autocmd VimEnter * :python vial.init()
augroup END

function! VialEmit(event)
    python vial.event_received()
endfunction

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

