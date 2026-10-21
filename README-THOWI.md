# ThowiLabs · OmniVoice GGML C++ / CUDA T4

Fork upstream: [bluryar/omnivoice.cpp](https://github.com/bluryar/omnivoice.cpp).

This fork retains the original GGML source, commit-pinned vendor/ggml submodule,
upstream Apache-2.0 license, notices and CUDA patch. It adds an **idempotent
Tesla T4 CUDA build script** and a portable binary/source packager.

## Build from scratch

```bash
git clone --recurse-submodules https://github.com/ThowiLabs/omnivoice-ggml-cpp.git
cd omnivoice-ggml-cpp
JOBS=4 bash scripts/build_t4_cuda.sh
```

Outputs appear in `dist/`. CUDA build uses NVIDIA sm_75, `GGML_CUDA_NO_VMM=ON`,
and patched GGML conv-transpose and im2col CUDA kernels. The binary distribution
bundles its own GGML shared libraries and startup launcher, but **not** CUDA's
NVIDIA drivers or proprietary runtime; CUDA 12 GPU drivers are still required.

## Prebuilt and user interface

Prebuilt CUDA binaries, vendored source archive, separate Q8 GGUF and a complete
Gradio companion interface are available in the original project repository:

[ThowiLabs/OVLC on Hugging Face](https://huggingface.co/ThowiLabs/OVLC/tree/main/bluryar).

These are stored under `bluryar/` to preserve the original OVLC C++ engine.
The companion Gradio has isolated datasets and on-demand compressed MP3 previews.
**Voice cloning and model-weight licenses may restrict commercial usage.** Use
only voices with consent. GGUF weights have their own original model licenses.
