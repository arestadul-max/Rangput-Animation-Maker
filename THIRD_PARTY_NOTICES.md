# Third-party notices

The Windows release (`Rangput-Animation-Maker-Windows.zip`) bundles these open-source components inside `RongpatStudio/python`. Each keeps its own licence.

| Component | Use | Licence | Source |
|---|---|---|---|
| Python 3.12 (conda-forge build) | runs the program | PSF License | https://www.python.org |
| NumPy, SciPy | audio synthesis and filters | BSD-3-Clause | https://numpy.org, https://scipy.org |
| OpenBLAS | maths library used by NumPy/SciPy | BSD-3-Clause | https://www.openblas.net |
| Pillow | images | MIT-CMU (HPND) | https://python-pillow.org |
| openpyxl, et_xmlfile | reading and writing scenes.xlsx | MIT | https://openpyxl.readthedocs.io |
| resvg / resvg_py | drawing every frame | MPL-2.0 / Apache-2.0 | https://github.com/linebender/resvg |
| imageio-ffmpeg (ffmpeg binary) | making the MP4 video | BSD-2 (wrapper), **GPL** (ffmpeg build) | https://github.com/imageio/imageio-ffmpeg, https://ffmpeg.org |
| Microsoft Visual C++ runtime, UCRT | needed by Python on Windows | Microsoft redistributable licence | https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist |

Fonts in `RongpatStudio/engine/assets/fonts`, all under the **SIL Open Font License 1.1**:

| Font | Designer | Source |
|---|---|---|
| Hind Siliguri | Indian Type Foundry | https://fonts.google.com/specimen/Hind+Siliguri |
| Rozha One | Indian Type Foundry | https://fonts.google.com/specimen/Rozha+One |
| Inter | Rasmus Andersson | https://rsms.me/inter |

**ffmpeg (GPL):** the bundled ffmpeg executable is an unmodified build distributed by the imageio-ffmpeg project. Its complete source code is available from https://ffmpeg.org/download.html, and the build scripts from https://github.com/imageio/imageio-binaries.
