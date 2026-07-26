# Venue Profiles

## Resolution Order

1. Read the live paper entry point and its document class/style.
2. Inspect how neighboring figures use `figure`/`figure*`, `\columnwidth`,
   `\textwidth`, captions, and labels.
3. Use official venue instructions already present in the project.
4. If the venue is unknown, use a conservative template-derived profile and
   disclose that the final dimensions still need venue verification.

## AAAI / Two-Column Profile

- Treat the checked-in AAAI style as authoritative for layout.
- Use `\columnwidth` for one-column figures and `\textwidth` for `figure*`.
- Prefer compact legends, direct labels, vector output, and minimal decoration.
- Put interpretation in the caption, not a large title inside the plot.
- Verify the figure inside the real manuscript; an isolated preview is not a
  camera-ready layout pass.

## Other CS Venues

Do not guess ACL, NeurIPS, IEEE, ACM, or journal dimensions from memory. Derive
them from the checked-in template and record `venue: template-derived` when no
verified profile exists.

