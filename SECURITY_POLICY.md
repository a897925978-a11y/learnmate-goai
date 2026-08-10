# GitHub Repository Security & Branch Protection Policy

1. Main Branch Protection (`main`):
   - Direct push forbidden for non-owner collaborators.
   - All code changes must arrive via Pull Request (PR).
   - Mandatory 1 approval required before merge.

2. Code Access Boundary:
   - Collaborators assigned `Developer` role (no Admin/Owner access).
   - .aiexclude & .cursorignore enforced to block automated AI RAG indexing of private modules.
