---
description: Filesystem Boundaries
applyTo: "**"
metadata:
  version: 1.2
---
# Filesystem Boundaries
When searching or reading local files outside the project directory, only access well-defined, discoverable
locations relevant to the task — such as the current environment dependencies' folders and packages.
Never speculatively browse the user's home directory, arbitrary system paths, or paths that may or may not exist.
If you need to find the location of an installed package, use the appropriate tooling for the language
rather than guessing at paths.
