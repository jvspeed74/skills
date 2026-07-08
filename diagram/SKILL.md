---
name: diagram
description: Create mermaid diagrams for one or more systems. Use when the user asks to diagram, visualize, map, or document system architecture, behavior, state machines, data flow, or component boundaries.
tools: Read, Write, Glob, Grep
disable-model-invocation: true
---

Create mermaid diagrams for the following: $ARGUMENTS

Parse the arguments: the final token is the output file path; everything before it names the system(s) to diagram.

Create as many diagrams as necessary to fully visualize the system(s). Cover every applicable dimension:

- **Behavior** — how the system acts under different inputs and conditions
- **State machine** — discrete states and their transitions
- **Flow** — data and control flow through the system
- **Views** — structural decomposition into components or layers
- **Boundaries** — system edges, external dependencies, and integration points

Output all diagrams as a single markdown document written to the specified file path. Each diagram must have a heading and a brief description of what it shows.
