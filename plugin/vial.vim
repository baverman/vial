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
    " autocmd FileType * :python vial.filetype_changed()
augroup END

function! VialEmit(event)
    python vial.event_received()
endfunction

function! VialGetKey()
    if getchar(1)
	let chr = getchar()
        if chr != 0
            let chr = nr2char(chr)
        endif
    else
        let chr = ''
    endif
    return chr
endfunction

python import vial

