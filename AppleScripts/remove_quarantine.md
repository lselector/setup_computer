# Allow the my_* apps to open without the "Open Anyway" prompt

The prompt is **Gatekeeper quarantine**. When apps are transferred (download,
AirDrop, email, etc.) macOS tags them with a `com.apple.quarantine` attribute
that triggers the "unidentified developer / Open Anyway" gate.

The apps live in `/Applications`.

## Clear it from one app

`-d` deletes the attribute, `-r` recurses into the `.app` bundle:

```bash
xattr -dr com.apple.quarantine /Applications/my_zed.app
```

## Do all the my_* apps at once

```bash
xattr -dr com.apple.quarantine /Applications/my_New_iTerm.app /Applications/my_zed.app /Applications/my_NewTextFile2.app
```

## Useful checks

```bash
xattr /Applications/my_zed.app          # see if the quarantine flag is present
xattr -cr /Applications/my_zed.app      # nuke ALL extended attributes (broader hammer, also works)
```

## Notes

- Run this on the machine where the apps live (quarantine is applied on the
  receiving end).
- After clearing, the apps open with no "Open Anyway" detour.
