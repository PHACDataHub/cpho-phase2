# Architecture

We have to architecture diagrams right now. A diagram of the current WIP state of the architecture, and a diagram of the current draft of the target architecture state.These should converge over time and, once stable, we'll eventually just have one final state diagram. 

## Updating the diagram
The diagram is generated from [D2](https://d2lang.com/) code to allow versioning and rapid revisions. Install the [D2 CLI](dev-env-secret-pattern) and the D2 VSCode extension before editing the `.d2` files.

To update the svg, cd in to `./architecture-diagram` and run `d2 --layout elk <filename>.d2`. Add the `-w` flag for watch mode for a live-updating browser view while editing. 

## Current WIP Architecture

![draft architecture](architecture-current.svg)

## Draft Target Architecture

![draft architecture](architecture-target.svg)