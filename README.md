# python_setup

unix and git dot files
python and ipython config files
some common modules I use

## dot/

Templates for home-directory dot files. A leading `_`
stands for `.`, and `.txt` is dropped on install:
`dot/_zshrc.txt` -> `~/.zshrc`,
`dot/_config/fish/` -> `~/.config/fish/`,
`dot/_claude/` -> `~/.claude/` (rules and skills).

- `_bashrc.txt`: plain bash.
- `_bashrc_fish.txt`: the same, then execs fish at the end.
- `_zshenv.txt` + `_zshrc.txt`: zsh env and interactive parts.

API keys are commented placeholders. Fill them in locally
and never commit real values.
