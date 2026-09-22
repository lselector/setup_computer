# .git-completion.zsh - git completion for zsh.
# Sourced by ~/.mygit; ~/.zshrc runs compinit after it.
# Uses Homebrew git's matched pair (updated by brew upgrade):
#   _git                    zsh wrapper, found via fpath
#   git-completion.bash     the engine _git loads
HB=/opt/homebrew
zstyle ':completion:*:*:git:*' script \
    $HB/etc/bash_completion.d/git-completion.bash
fpath=($HB/share/zsh/site-functions $fpath)
unset HB
