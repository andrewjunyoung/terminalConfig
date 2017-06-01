"VUNDLE
set nocompatible              " be iMproved, required
filetype off                  " required

filetype plugin indent on

let &t_SI = "\<Esc>]50;CursorShape=1\x7"
let &t_SR = "\<Esc>]50;CursorShape=2\x7"
let &t_EI = "\<Esc>]50;CursorShape=0\x7"

" POWERLINE
set rtp+=/usr/local/lib/python2.7/site-packages/powerline/bindings/vim

if has("gui_running")
           let s:uname = system("uname")
              if s:uname == "Darwin\n"
                            set guifont=Meslo\ LG\ S\ for\ Powerline
                               endif
                       endif

syntax on

" recolor background past right margin
highlight ColorColumn ctermbg=235 guibg=#2c2d27
let &colorcolumn=join(range(81,999),",")
let &colorcolumn="80,".join(range(120,999),",")

" 'set'-commands (listed alphabetically)
" C
set cursorline
hi CursorLine term=bold cterm=bold ctermbg=235

set cursorcolumn
hi CursorColumn ctermbg=235

" E
set expandtab
set exrc

" H
set hlsearch

" I
set incsearch

" N
set number

" R
set ruler

" S
set softtabstop=4
set secure

" T
set tabstop=4
