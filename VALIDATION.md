# Validation snapshot

Date: 2026-07-26

The repository preserves the selected local skill files byte-for-byte, excluding
only caches and repository metadata. Source and repository tree hashes match for
all ten skills.

## Current validator result

Eight skills pass the current `skill-creator` `quick_validate.py` check.

Two installed legacy skills are preserved unchanged and produce validator
compatibility warnings:

- `academic-pipeline`: its existing frontmatter description contains ASCII
  arrows (`->`), while the current validator rejects angle-bracket characters
  in descriptions.
- `grill-me`: its existing frontmatter uses
  `disable-model-invocation: true`, while the current validator no longer lists
  that legacy key among accepted properties.

Both skills were already present in the active local skill catalog. This
snapshot does not silently rewrite their behavior merely to satisfy a newer
validator. Any future migration should be performed explicitly and should
update both the installed skill and this snapshot together.

Six copied source files also retain a pre-existing blank line at end of file,
which `git diff --check` reports as whitespace. They remain unchanged so the
recorded source and repository tree hashes stay identical.

## Safety checks

- No common API-token, GitHub-token, AWS-key, or private-key patterns detected.
- No credential-like files, `.env` files, symlinks, nested Git repositories, or
  files larger than 10 MB detected.
- No absolute local paths or runtime references back to the source projects
  detected inside the copied skill content.
