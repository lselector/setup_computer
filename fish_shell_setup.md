<b>Fish Shell Installation and Configuration Instructions</b>


Installation on linux:

``` 
sudo apt-add-repository ppa:fish-shell/release-3
sudo apt-get update
sudo apt-get install fish

sudo apt-get install fzf  # for old Ubuntu this doesn't work. 
                          # You need to clone github repo.
sudo apt-get install fonts-powerline
```

Installation on Mac:

```
brew install fish fzf     # or sudo port install fish fzf

git clone https://github.com/powerline/fonts.git --depth=1
cd fonts
./install.sh
cd ..
rm -rf fonts
```


Finally, on both systems install:
"fisher" (package manager) and fzf bindings:

```
# from the fish prompt
# use curl -sL to output some code 
# (-s = silent, -L = --location - to follow url redirects)

curl -sL git.io/fisher > temp_fisher.txt
source temp_fisher.txt 
rm temp_fisher.txt

fisher install jorgebucaran/fisher

fisher install jethrokuan/fzf
### fisher install fishpkg/fish-prompt-metro  ### this gives error on Mac - November 2020

set -U FZF_LEGACY_KEYBINDINGS 0
set -U FZF_DEFAULT_OPTS "--height 25"
```

Now if you are in fish on unix prompt and press Ctrl-R, you will see history - and can type words to do fuzzy search through history

On Mac OS type command:

```
fish_config
```

This will pop-up a browser window where you can see or change things.
For example, you can select a unix prompt. I like the prompt called "Sorin"


Afterwards, set up iterm_shell_integration. 
(You should do this on all machines you SSH into)
 - [https://iterm2.com/documentation-shell-integration.html]()


Question:

If you had custom bash shell scripts and functions, 
but now you want to use fish or bash as needed - what do you do?

Answer:

You maintain "bash" as your default login shell. 
This will set your bash variables, aliases and functions at login.
If you want to automatically load fish - you can add some code
to the end of your .bashrc to switch to "fish" - but only at first login

Here is the code:

```

# --------------------------------------------------------------
# Put this code at the end of your .bashrc 
# to start fish with your bash configs loaded
# It will activate fish if and only if 
# it exists and is executable and if this is a new session.
# i.e. if this is a login shell. 
# Note:
#     $- variable in bash contains a string representing the flags which are set
#     so echo $- normally outputs this short string:  himBH
#     where 'i' flag means "interactive"
#     [[ -x somefile ]] checks if the file exists and is executable

export SHELL=/bin/bash
FISH_LOCATION=$(which fish)

if [ -z "$FISH_FLAG" ]; then
    export FISH_FLAG="not_set"
else
    export FISH_FLAG="was_set"
fi

if echo $- | grep -q 'i' && [[ -x $FISH_LOCATION ]] && [[ "$FISH_FLAG" = "not_set" ]]; then
    exec env SHELL=$FISH_LOCATION $FISH_LOCATION -i
fi

# also create/edit file ~/.config/fish/config.fish

setenv SHELL /usr/local/bin/fish

function fish_greeting
end
funcsave fish_greeting

# --------------------------------------------------------------
```

Aliases and functions do not get ported from bash into fish automatically. You can copy their definitions into file ~/.config/fish/config.fish

Or you can source them in  file ~/.config/fish/config.fish from another file:

```
source ~/.bash_fish_aliases
```

Syntax for aliases definitions is the same as in bash
<br>Syntax for functions needs to be changed.

Examples:

```

# --------------------------------------------------------------
function path
    string split : $PATH
end
# --------------------------------------------------------------
function lll --wraps=ls --description 'List all using long format'
    ls -alh $argv
end
# --------------------------------------------------------------
alias gh="cd ~/Documents/GitHub"
alias uedit='open -a UltraEdit'
# --------------------------------------------------------------
```


FYI. The history file is located here: 

```
~/.local/share/fish/fish_history
```

Other fish plugins you can install with the package manager

 - [https://github.com/jorgebucaran/awesome.fish]() 
 - [https://github.com/jorgebucaran/bax.fish]() -> Run bash commands from fish. `fisher add jorgebucaran/bax.fish`
 - [https://github.com/joseluisq/gitnow]() -> Fish extensions for git.

Docs to visit

 - Homepage listing various features: [https://fishshell.com/]()
 - Tutorial: [https://fishshell.com/docs/current/tutorial.html]()
 - FAQ: [https://fishshell.com/docs/current/faq.html]()
 - Main Documentation: [https://fishshell.com/docs/current/index.html]()

Fish Scripting:

All fish functions must go into this directory if you want them to be auto-loaded on fish shell startup:

```
~/.config/fish/functions
```

You can find various other configuration in this directory:

```
~/.config/fish
```

In particular, this file is executed on fish startup. Analogous to .bashrc

```
~/.config/fish/config.fish
```

Be sure to familiarize yourself with the ‘set’ command. 
Fish lets you set variables in several different scopes and lifetimes.

 - [https://fishshell.com/docs/current/cmds/set.html]() 

Some of these lifetimes can exceed the life of the current process. 
I believe this is done by saving them into:

```
    ~/.config/fish/fish_variables
```

Scripting docs

 - Fish functions: [https://fishshell.com/docs/current/index.html#functions]()
 - Defining aliases: [https://fishshell.com/docs/current/index.html#defining-aliases]()
 - Autoloading functions (so they are available on startup): [https://fishshell.com/docs/current/index.html#autoloading-functions]()

Other utils that could be fun to install:

 - [https://github.com/BurntSushi/ripgrep]()
 - [https://github.com/BurntSushi/xsv]()
 - [https://github.com/sharkdp/bat]() 
 - [https://github.com/jorgebucaran/fishtape]() - unit test your fish scripts
 - [https://github.com/lotabout/skim]() - fzf competitor written in rust. 

Need to play with it. Not clear what major usage differences are at this point.

 - [https://github.com/jhawthorn/fzy]() - fzf competitor written in C. Meant to be faster (to be fair, I never had an issue with fzf, but faster is better?) and prefer whole words. (fzf might also do this… it has lots of features)
