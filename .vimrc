set tw=0
au BufNew,BufRead *.md setlocal spell spelllang=ru_ru
au BufNew,BufRead input/plan/index.md setlocal ft=html

map <F6> :!make deploy<CR>
