# Path to your oh-my-zsh installation.
export ZSH=/Users/jun/.oh-my-zsh

# Name of the theme to load. See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="xun-zsh"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# How often to auto-update (in days).
export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# HIST_STAMPS="yyyy-mm-dd"

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git)

source $ZSH/oh-my-zsh.sh

################################################################################

# hist lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory beep extendedglob nomatch
bindkey -v
# end of lines configured by zsh-newuser-install

# theme

ZSH_THEME="powerlevel9k/powerlevel9k"

autoload -Uz compinit
compinit

# alias

alias "c"="clear"
alias "g"="git"
alias "l"="ls -Ap"
alias "refresh"="clear; list"
alias "show"="ls -ApR | grep ":$" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/ /' -e 's/-/|/'"
alias "up"="cd .."

alias "restart"="exec zsh"

# export

docs=~/Documents
dl=~/Downloads
pics=~/Pictures
code=~/Documents/code
scripts=~$code/scripts
public=~/Documents/public
private=~/Documents/private
ic=~/Documents/ic
cs=$ic/cs
math=$ic/math
lib=~/Documents/archive/lib
org=$private/org
revision=$ic/revision

# prompt

## zsh-git-prompt

source .zsh/zsh-git-prompt/zshrc.sh

function prompt_char {
    git branch >/dev/null 2>/dev/null && echo '±' && return
    echo '>'
}

PROMPT='[%B%h%b | %F{cyan}%m%f.%F{green}%n%f | %D %* | $(git_super_status) | %F{blue}%B%U%3c%u%b%f]
> '
TMOUT=1

TRAPALRM() {
    zle reset-prompt
}

# colors

# Set clicolor if you want ansi colors in iterm
export CLICOLOR=1
# set colors for iterm2
export TERM=xterm-256color
# ls colors
LS_COLORS=$LS_COLORS:'di=0;32:' ; export LS_COLORS
# stderr
exec 2>>( while read X; do print "\e[91m${X}\e[0m" > /dev/tty; done & )

# tmux

# Run on startup
# if [ "$TMUX" = "" ]; then tmux; fi

# rbenv (ruby environment)
##
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

# zsh-autosuggestions

source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

# zsh-syntax-highlighting

source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# day/night background

night() {
    # macOS trick explained in readme
    rm ~/Pictures/desktop/current/day.jpeg 2> /dev/null
    cp ~/Pictures/desktop/night.jpeg ~/Pictures/desktop/current/night.jpeg
}

day() {
    # macOS trick explained in readme
    rm ~/Pictures/desktop/current/night.jpeg 2> /dev/null
    cp ~/Pictures/desktop/day.jpeg ~/Pictures/desktop/current/day.jpeg
}
