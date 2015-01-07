set tw=0
au BufNew,BufRead input/plan/index.md setlocal ft=html

map <F6> :!make push-docs<CR>
