# Custom settings for fish
# Env (PATH, PYTHONPATH, keys) comes from ~/.bashrc,
# which execs fish at its end (see _bashrc_fish.txt).

setenv SHELL /opt/homebrew/bin/fish
set -gx CLAUDE_CODE_SHELL /bin/bash   # Claude Code tools run in bash
set -l venv_activate $HOME/.venvs/standard/bin/activate.fish
test -f $venv_activate; and source $venv_activate

# --------------------------------------------------------------
set fish_greeting
# --------------------------------------------------------------
function fish_prompt
    if test -n "$SSH_TTY"
        echo -n (set_color brred)"$USER"(set_color white)'@'(set_color yellow)(prompt_hostname)' '
    end

    echo -n (set_color blue)(prompt_pwd)
    echo -n (set_color magenta)(fish_git_prompt)  # ' (branch)' in a repo
    echo -n ' '

    set_color -o
    if test "$USER" = 'root'
        echo -n (set_color red)'# '
    end
    echo -n (set_color red)'❯'(set_color yellow)'❯'(set_color green)'❯ '
    set_color normal
end
# --------------------------------------------------------------
function path
    string split : $PATH
end
# --------------------------------------------------------------
function pypath
    string split : $PYTHONPATH
end
# --------------------------------------------------------------
test -f ~/.myaliases; and source ~/.myaliases
alias hist 'history merge; history'
# --------------------------------------------------------------
test -e {$HOME}/.iterm2_shell_integration.fish ; and source {$HOME}/.iterm2_shell_integration.fish

test -f $HOME/.docker/init-fish.sh; and source $HOME/.docker/init-fish.sh   # Docker Desktop

# sets correct VSCODE SHELL INTEGRATION - and caches it
if string match -q "$TERM_PROGRAM" "vscode"
    # Check if we have a cached path in a universal variable
    if not set -q VSCODE_SHELL_INTEGRATION_PATH
        # Path not cached, find it now using the code command
        set -Ux VSCODE_SHELL_INTEGRATION_PATH (code --locate-shell-integration-path fish)
    end

    # Use the cached path
    if test -f "$VSCODE_SHELL_INTEGRATION_PATH"
        source "$VSCODE_SHELL_INTEGRATION_PATH"
    end
end
