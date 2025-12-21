## fish & VSCode

There is a problem with Cline VSCode extension getting
stuck when running the shell commands

It works well when your shell is bash.
But it may have problems with zsh and fish.

To avoid problems with fish, add the following code
at the end of file ~/.config/fish/config.fish

``` sh 
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
```

For zsh we do similar changes in ~/.zshrc file:

``` sh
# sets correct VSCODE SHELL INTEGRATION - and caches it
if [ "$TERM_PROGRAM" = "vscode" ]; then
    # Check if we have a cached path
    if [ -z "$VSCODE_SHELL_INTEGRATION_PATH" ]; then
        # Path not cached, find it now using the code command
        export VSCODE_SHELL_INTEGRATION_PATH=$(code --locate-shell-integration-path zsh)
        
        # Optionally persist it (add to .zshenv for persistence across sessions)
        # echo "export VSCODE_SHELL_INTEGRATION_PATH='$VSCODE_SHELL_INTEGRATION_PATH'" >> ~/.zshenv
    fi

    # Use the cached/found path
    if [ -f "$VSCODE_SHELL_INTEGRATION_PATH" ]; then
        source "$VSCODE_SHELL_INTEGRATION_PATH"
    fi
fi
```
