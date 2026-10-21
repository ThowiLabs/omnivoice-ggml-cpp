#!/usr/bin/env bash
# CUDA 12 + compute capability 7.5 (NVIDIA Tesla T4), without mutating upstream GGML history.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
git submodule update --init --recursive
PATCH="$ROOT/patches/ggml-v0.9.11-omnivoice-cuda-fixes.patch"
if git -C vendor/ggml apply --reverse --check "$PATCH" >/dev/null 2>&1; then
    echo 'GGML CUDA fix already present'
else
    git -C vendor/ggml apply --check "$PATCH"
    git -C vendor/ggml apply "$PATCH"
fi
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON \
    -DGGML_CUDA_NO_VMM=ON -DCMAKE_CUDA_ARCHITECTURES=75 \
    -DGGML_CUDA_FA_ALL_QUANTS=OFF
cmake --build build --parallel "${JOBS:-4}"
python3 scripts/package_t4.py
