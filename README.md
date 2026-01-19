# PQC Benchmark

This repository provides a Docker-based setup for benchmarking Post-Quantum Cryptography (PQC) implementations. It supports multiple profiles for different hardware simulations: Mobile, Laptop, and Server.

---

## Test Environment

This benchmark was tested on a **Linux Ubuntu 24 VM** with:

- 2 CPUs  
- 2 GB RAM  

Your results may vary depending on available resources.

---

## Prerequisites

- Docker installed ([installation guide](https://docs.docker.com/get-docker/))
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

Version:           28.2.2
 API version:       1.50
 Go version:        go1.23.1
 Git commit:        28.2.2-0ubuntu1~24.04.1
 Built:             Wed Sep 10 14:16:39 2025
 OS/Arch:           linux/amd64
 Context:           default

- Linux or macOS recommended (Windows possible with WSL2)
- Git, to clone this repository
- Docker base image: `python:3.12-slim`
- Python 3.12.12 (inside the Docker container)
- Python 3.12.3 (outside the Docker container)



## Clone the Repository

```bash
git clone https://github.com/Aprilanna6/pqc-benchmark.git
cd pqc-benchmark
```
## Build the Docker Image

To build the Docker image, run:

```bash
# Optional: enable BuildKit (recommended)
export DOCKER_BUILDKIT=1

# Build the image
sudo docker build -t pqc-benchmark:latest .
```
Note: If you want to run Docker as a non-root user, add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
# log out and log back in
```

## Run Benchmarks

There are three pre-configured profiles:

| Profile | CPUs | RAM    | Description            |
| ------- | ---- | ------ | ---------------------- |
| Mobile  | 0.5  | 256 MB | Simulates a smartphone |
| Laptop  | 1    | 2 GB   | Simulates a laptop     |
| Server  | 4    | 8 GB   | Simulates a server     |

### Examples:

```bash
# Mobile
sudo docker run --rm -v $(pwd):/app -e PROFILE=Mobile --cpus=0.5 --memory=256m pqc-benchmark:latest

# Laptop
sudo docker run --rm -v $(pwd):/app -e PROFILE=Laptop --cpus=1 --memory=2048m pqc-benchmark:latest

# Server
sudo docker run --rm -v $(pwd):/app -e PROFILE=Server --cpus=4 --memory=8192m pqc-benchmark:latest

```
The -v $(pwd):/app option mounts the current project directory into the container so that results are saved directly on the host.

## Results

After each run, the script generates **folders with benchmark results** in the project directory.  
Typical folder structure:

results
|---Mobile
|---Laptop
\---Server


Each folder contains the benchmark data for the corresponding profile.

---

## Notes

- `.dockerignore` excludes unnecessary files from the Docker build (`.git`, `__pycache__/`, `*.pyc`)  
- BuildKit is recommended to use modern Docker features  
- Make sure your system has enough resources (CPU/RAM) for the container profiles

---

## License

Include your license here (e.g., MIT, Apache 2.0, etc.)


