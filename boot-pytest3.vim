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

let g:vial_python = "python3"
py3file ./boot-pytest.py
quitall!
