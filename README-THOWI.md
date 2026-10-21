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

## Experimental: Hangry Labs speech-edge protection

**On branch `feat/hangry-edge-protection`.** The behavior was adapted from
[hangry-labs/OmniVoiceTTS](https://github.com/hangry-labs/OmniVoiceTTS):

- `--fade-duration F`: seconds of audio fade per edge (default 0.1; try 0.02 or 0).
- `--pad-duration F`: silence seconds added per edge (default 0.1; independent of fade).
- `--output-preserve-active-edges true`: avoid discarding weak nonzero samples
  at both ends during silence cleanup (default false for compatibility).
- `--normalize-terminal-punctuation true|false`: normalize *attached ASCII*
  terminal `?`/`!` into separate tokens, excluding CJK. Default true.

These flags are supported in the C++ CLI and corresponding snake_case JSON
options by the C++ HTTP server. Use the following for experimental output:

```bash
./build-experimental/omnivoice-cli --model omnivoice-q8_0.gguf \
  --text '¿Estamos listos?' --ref-audio sample.wav \
  --ref-text 'Exact transcription of sample.' --language Spanish \
  --device cuda:0 --num-step 32 --output test.wav \
  --fade-duration 0.02 --pad-duration 0.1 \
  --output-preserve-active-edges true \
  --normalize-terminal-punctuation true
```

Use `--fade-duration 0.1 --pad-duration 0.1
--output-preserve-active-edges false --normalize-terminal-punctuation false` for
byte-for-byte compatibility with the previous motor (tested with a real
voice clone). Note the original model *still* predicts a fixed number of audio
frames; no fade adjustment guarantees complete final phonemes. Source files
remain Apache 2.0, and this adaptation retains attribution to Hangry Labs.

To validate the algorithm without a GPU:

```bash
cmake -S . -B build-tests -DGGML_CUDA=OFF -DOMNIVOICE_BUILD_TESTS=ON
cmake --build build-tests --target test-edge-controls --parallel 4
ctest --test-dir build-tests --output-on-failure
```

**Production safety:** dataset-generating Gradio continues to use the previous
binary until this experimental variant is intentionally deployed. Generated
WAVs and job manifests are never modified by these build/test scripts.
