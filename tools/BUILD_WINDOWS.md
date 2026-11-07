# Building the Windows package

The release zip is the `app/RongpatStudio` folder plus a self-contained Windows Python in `RongpatStudio/python`. It can be built on Linux with micromamba (no Windows machine needed).

```bash
# 1. micromamba (from conda-forge)
curl -LO https://conda.anaconda.org/conda-forge/linux-64/micromamba-2.10.0-0.tar.bz2
tar xjf micromamba-*.tar.bz2 bin/micromamba
export MAMBA_ROOT_PREFIX=$PWD/mamba

# 2. a Windows Python environment with OpenBLAS (much smaller than MKL)
./bin/micromamba create -y --platform win-64 -p winenv -c conda-forge \
    python=3.12 numpy scipy pillow openpyxl "libblas=*=*openblas"

# 3. Windows wheels that conda-forge doesn't provide
pip download --platform win_amd64 --python-version 3.12 --only-binary=:all: --no-deps \
    resvg_py imageio-ffmpeg -d wheels

# 4. assemble
cp -r app/RongpatStudio dist/RongpatStudio
cp -r winenv dist/RongpatStudio/python
cd dist/RongpatStudio/python
find . -name "*.pdb" -delete
# on Linux the env has both Lib/ and lib/ - merge them for Windows
cp -rn lib/site-packages/* Lib/site-packages/ 2>/dev/null; cp -rn lib/python3.12/site-packages/* Lib/site-packages/ 2>/dev/null; rm -rf lib bin
for w in ../../../wheels/*.whl; do python3 -m zipfile -e "$w" Lib/site-packages/; done
```

The `.bat` launchers set `PATH` (including `python\Library\bin` for the DLLs) and `PYTHONPATH=engine`, then run `python -m rongpat …`.

**Testing on Linux with Wine:** Wine's built-in `ucrtbase` lacks some functions, so prefer the bundled ones:
```bash
WINEDLLOVERRIDES="ucrtbase,vcruntime140,vcruntime140_1,msvcp140=n,b" \
WINEPATH="Z:\\path\\to\\RongpatStudio\\python;Z:\\path\\to\\RongpatStudio\\python\\Library\\bin" \
PYTHONPATH='Z:\path\to\RongpatStudio\engine' \
wine64 RongpatStudio/python/python.exe -m rongpat still "projects\\Demo - The Last Ball" 2
```

## Regenerating the rigs

`tools/autorig_bible.py` re-runs the bible's body code (`tools/bible_source/`) with the limb drawing functions captured, and writes `app/RongpatStudio/engine/assets/rigs/*.json`:

```bash
python tools/autorig_bible.py
```
