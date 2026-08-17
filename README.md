### INTRODUCTION | [ABOUT](ABOUT.md) | [CFC](https://github.com/sz3/cfc) | [LIBCIMBAR](https://github.com/sz3/libcimbar)

## cimbar: Color Icon Matrix bar codes

cimbar is a proof-of-concept 2D data encoding format -- much like [QR Codes](https://en.wikipedia.org/wiki/QR_code), [JAB codes](https://jabcode.org/), and [Microsoft's HCCB](https://en.wikipedia.org/wiki/HCCB).

<p align="center">
<img src="https://github.com/sz3/cimbar-samples/blob/v0.6/b/4cecc30f.png" width="70%" title="A non-animated mode-B cimbar code" >
</p>

## How it works

Cimbar encodes data in a grid of symbols (or icons). There are 16 possible symbols per tile (position) on the grid, encoding 4 bits per tile. In addition, 2-3 color bits can be encoded per position.

![4 bit cimbar encoding](https://github.com/sz3/cimbar-samples/blob/v0.5/docs/encoding.png)

There are multiple color schemes:
* "dark" mode -- meant for backlit computer screens, with bright tiles on a black background
* "light" mode -- meant for paper, with dark tiles on a white background

Cimbar was inspired by [image hashing](https://github.com/JohannesBuchner/imagehash/). On a per-tile basis, the cimbar decoder compares the tile against a dictionary of 16 expected tiles -- each one representing a 4-bit symbol.

[Error correction](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction) is applied on the resulting bit stream, and the bit stream itself is interleaved across the image.

This python cimbar implementation is a research project. It works, but it is slow, and does not handle error cases with much grace. [libcimbar](https://github.com/sz3/libcimbar), the C++ implementation, is better suited for performance-critical use.

## Quick start (命令行)

- Encoding:

```
python -m cimbar.cimbar --encode myinputfile.txt encoded.png
```

- Decoding:

```
python -m cimbar.cimbar encoded.png myoutputfile.txt
python -m cimbar.cimbar /tmp/encoded.png -o /tmp/myoutputfile.txt
```

- 示例（测误差或 camera 解码）:

```
python -m cimbar.cimbar encoded.png -o clean.txt --deskew=0 --ecc=0
python -m cimbar.cimbar camera/001.jpg -o decode.txt --ecc=0
python -m cimbar.grader clean.txt decode.txt
```

## Programmatic usage（在 Python 中调用）

你可以直接从 Python 脚本或交互式环境调用 encode/decode：

```python
from cimbar.cimbar import encode, decode
from cimbar import conf

# 编码
encode('input.bin', 'out.png', dark=False, ecc=conf.ECC, fountain=False)

# 解码
decode(['out.png'], 'out.bin', dark=False, ecc=conf.ECC, fountain=False)
```

如果需要更高层次的 API（返回结构化状态、异常捕获等），请查看或使用 cimbar.api（如在本分支中添加）。

## GUI（桌面图形界面）

本仓库在 add-resource-path-pyinstaller 分支提供了一个简单的基于 PySimpleGUI 的桌面 GUI，文件路径：

  cimbar/gui.py

功能：
- 选择 Encode / Decode 模式
- Encode: 选择源文件，指定输出图片前缀
- Decode: 选择一个或多个图片文件，指定输出二进制文件
- 可设置 Dark palette、Fountain、ECC 等常用选项

运行方法（在仓库根目录下）：

```
python -m cimbar.gui
```

依赖：

```
pip install PySimpleGUI
```

建议先在本地使用虚拟环境并测试编码/解码工作正常，然后再考虑打包为可执行文件。

## 打包为 Windows 可执行文件（PyInstaller）

如果你希望发布单个独立的 Windows exe，推荐使用 PyInstaller。该分支已经对资源加载做了调整（使用 resource_path），以便支持 --onefile 模式。

示例打包命令（先做 onedir 调试，再做 onefile）：

1) onedir（调试用）

```
pyinstaller --name cimbar --console --onedir --add-data "bitmap;bitmap" cimbar\cimbar.py
```

2) onefile（生成单个 exe）

```
pyinstaller --name cimbar --console --onefile --add-data "bitmap;bitmap" cimbar\cimbar.py
```

说明：
- Windows 下 --add-data 的分隔符是分号 (;)，Linux/macOS 下用冒号 (:)
- resource_path 已在代码中处理 sys._MEIPASS（PyInstaller 单文件时的临时解包目录），确保打包后程序能找到 bitmap 资源
- 若运行 exe 报 ModuleNotFoundError，请在打包时使用 --hidden-import=module 或在 .spec 中添加 hiddenimports
- 若遇到 OpenCV/cv2 或其它二进制库的缺失，请确保安装相应的 Visual C++ 运行库或在 .spec 中包含所需二进制

## CI: Windows 构建示例（GitHub Actions）

本分支包含一个示例 workflow： .github/workflows/build-windows.yml
该 workflow 在 windows-latest 上安装依赖并运行 PyInstaller，若成功会把 dist\cimbar.exe 上传为 artifact（名称 cimbar-exe）。

触发：push 到 add-resource-path-pyinstaller 或手动触发 workflow。

## 其他说明与建议

- 本实现以研究为主，并非生产级别的鲁棒实现；若需在生产中使用，建议使用并优化 libcimbar 或在 C++ 版本中实现关键路径。
- 如果仓库中其它模块也直接使用相对路径访问 bitmap 资源（例如直接 Image.open('bitmap/...')），请在合并前一并替换为 resource_path(...)，以避免单文件 exe 找不到资源。我已在本分支修改了 cimbar/cimbar.py 并添加了 gui.py 和 CI workflow；如果你需要，我可以继续扫描并替换仓库的其它位置。

## Want to know more?

See [ABOUT](ABOUT.md) | [LIBCIMBAR](https://github.com/sz3/libcimbar)
