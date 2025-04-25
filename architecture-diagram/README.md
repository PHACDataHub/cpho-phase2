# Architecture

These will converge over time and, once stable, we'll eventually just have one final state diagram. 

## Updating the diagram

The diagram is generated from [D2](https://d2lang.com/) code to allow versioning and rapid revisions. Install the [D2 CLI](https://d2lang.com/tour/install/) and the D2 VSCode extension before editing the `.d2` files.

To update the svg, cd in to `./architecture-diagram` and run `d2 --layout dagre <filename>.d2`. Add the `-w` flag for watch mode for a live-updating browser view while editing.

## Functional Architectures

### Application

![Functional component architecture](architecture-functional-components.svg)

### Network

![Functional network architecture](architecture-functional-network.svg)

## Architectures

### Kubernetes

![Current k8s architecture](architecture-k8s.png)

### Network

![Current network architecture](architecture-network.svg)

### Cloud Run (Deprecated)

![Old Cloud Run architecture](architecture-cloud-run.svg)
