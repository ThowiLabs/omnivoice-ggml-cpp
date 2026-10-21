#!/usr/bin/env python3
"""Package tested, native Linux CUDA T4 binaries + complete vendored source.
No weights, user dataset contents, tokens or git data are ever included.
"""
from pathlib import Path
import hashlib, json, os, shutil, tarfile, tempfile
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True)
BIN=ROOT/'build'
LIB_FILES={
    'libomnivoice_ggml_cpp.so':BIN/'libomnivoice_ggml_cpp.so',
    'libggml-base.so.0.9.11':BIN/'ggml/src/libggml-base.so.0.9.11',
    'libggml-cpu.so.0.9.11':BIN/'ggml/src/libggml-cpu.so.0.9.11',
    'libggml.so.0.9.11':BIN/'ggml/src/libggml.so.0.9.11',
    'libggml-cuda.so.0.9.11':BIN/'ggml/src/ggml-cuda/libggml-cuda.so.0.9.11',
}
SOURCES=('CMakeLists.txt','README.md','README-THOWI.md','LICENSE','NOTICE',
         'THIRD_PARTY_NOTICES.md','src','include','vendor','patches','docs','scripts', '.gitmodules')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as src:
        for b in iter(lambda:src.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def safe_tar_filter(info):
    parts=Path(info.name).parts
    if any(p=='.git' or p=='__pycache__' or p=='.venv' for p in parts):return None
    if any(part in ('build','build-cpu','dist','alt-data') for part in parts):return None
    if info.issym() or info.islnk():
        # Source should be copyable and audited; no symlink escapes.
        return None
    return info
with tempfile.TemporaryDirectory(prefix='omnivoice-t4-pkg-') as temp:
    stage=Path(temp)/'bluryar-cuda-sm75'
    (stage/'bin').mkdir(parents=True)
    (stage/'lib').mkdir(parents=True)
    for name in ('omnivoice-cli','omnivoice-server'):
        p=BIN/name
        if not p.is_file():raise FileNotFoundError(str(p))
        shutil.copy2(p,stage/'bin'/name)
    for name,p in LIB_FILES.items():
        if not p.is_file():raise FileNotFoundError(str(p))
        shutil.copy2(p,stage/'lib'/name)
    for package in ('base','cpu','','cuda'):
        full='libggml'+('-'+package if package else '')
        for alias in (full+'.so',full+'.so.0'):
            (stage/'lib'/alias).symlink_to(full+'.so.0.9.11')
    (stage/'bin'/'run-omnivoice.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LD_LIBRARY_PATH="$HERE/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:${LD_LIBRARY_PATH:-}"
exec "$HERE/bin/omnivoice-cli" "$@"
''')
    os.chmod(stage/'bin'/'run-omnivoice.sh',0o755)
    shutil.copy2(ROOT/'LICENSE',stage/'LICENSE')
    shutil.copy2(ROOT/'NOTICE',stage/'NOTICE')
    (stage/'README.txt').write_text(
        'bluryar/omnivoice.cpp CUDA sm_75, Linux x86_64 (Tesla T4).\n'
        'Requirements: NVIDIA driver, CUDA runtime 12, libcublas.so.12, libcublasLt.so.12.\n'
        'Usage: bin/run-omnivoice.sh --model MODEL.gguf --text "Hola" '
        '--output voz.wav --device cuda:0 --language Spanish --num-step 32\n'
        'Voice cloning: add --ref-audio sample.wav --ref-text "transcript".\n'
        'Built with -DGGML_CUDA_NO_VMM=ON -DCMAKE_CUDA_ARCHITECTURES=75.\n'
        'Weights licensed separately. Reference: https://github.com/bluryar/omnivoice.cpp\n')
    out=DIST/'bluryar-omnivoice-cuda-sm75-linux-x86_64.tar.gz'
    with tarfile.open(out,'w:gz',compresslevel=6) as tar:
        tar.add(stage,arcname=stage.name,filter=safe_tar_filter)
    print('BIN_ARCHIVE',out.name,out.stat().st_size,sha(out),flush=True)
    src_out=DIST/'bluryar-omnivoice-full-source.tar.gz'
    with tarfile.open(src_out,'w:gz',compresslevel=6) as tar:
        for entry in SOURCES:
            p=ROOT/entry
            if p.exists():tar.add(p,arcname='bluryar-omnivoice-source/'+entry,filter=safe_tar_filter)
    print('SRC_ARCHIVE',src_out.name,src_out.stat().st_size,sha(src_out),flush=True)
    manifest={x.name:{'bytes':x.stat().st_size,'sha256':sha(x)} for x in (out,src_out)}
    (DIST/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
