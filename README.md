# 🔐 SecureSteg — Image Steganography Lab

> A desktop steganography toolkit built with **Python** and **PyQt5** that allows you to hide secret messages inside images, recover hidden messages, analyze image quality, and perform basic steganalysis — all from a modern desktop interface.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

# 🧠 What Is SecureSteg?

SecureSteg is a local desktop application designed for learning and experimenting with image steganography.

Using chaotic-map-driven LSB substitution, it allows users to:

- 🔒 Hide secret text inside images
- 🔓 Recover hidden messages
- 📊 Measure image quality after embedding
- 🕵️ Detect potential hidden data
- 🧩 Visualize image bit planes
- 📈 Compare image histograms
- 📚 Learn steganography concepts interactively

Everything runs locally on your machine.

✅ No browser required  
✅ No server required  
✅ No cloud storage  
✅ No internet connection required

---

# ✨ Features

| # | Tool | Description |
|---|------|-------------|
| 01 | Encode | Hide secret messages inside images |
| 02 | Decode | Recover hidden messages from encoded images |
| 03 | Scan | Check image dimensions and storage capacity |
| 04 | PSNR Analysis | Measure image quality degradation |
| 05 | Binary Visualizer | Convert text into binary representation |
| 06 | Histogram Viewer | Compare RGB distributions |
| 07 | Steganalysis | Detect possible hidden information |
| 08 | Bit Plane Viewer | Explore image bit planes |
| 09 | History | Local record of operations |
| 10 | Learn | Educational steganography reference |

---

# 📁 Project Structure

```text
steg/
├── main.py              # Application entry point
├── views.py             # Application views
├── widgets.py           # Reusable UI widgets
├── core.py              # Steganography logic and analysis
├── history.py           # Local history management
├── theme.py             # Styling and themes
├── requirements.txt     # Dependencies
├── README.md            # Documentation

├── build/               # PyInstaller build files
├── dist/                # Generated executable
├── venv/                # Virtual environment
├── __pycache__/         # Python cache
└── steg.spec            # PyInstaller specification
```

---

# ⚙️ Requirements

- Python 3.8+
- PyQt5
- NumPy
- Pillow

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🚀 Running From Source

```bash
https://github.com/0xfa-ni/Image-Steganogrphy-tool.git

cd Image-Steganogrphy-tool

pip install -r requirements.txt

python main.py
```

---

# 🖥️ Running The EXE
```text
dist/
├── steg.exe
└── chat.db
```

1. Double-click the `steg.exe`
2. Start using the application

No Python installation required.

---

# 📖 User Guide

## 🔒 Encode

Hide a secret message inside an image.

### Steps

1. Open **Encode**
2. Select an image
3. Enter a numeric seed
4. Select a technique:
   - Logistic Map
   - Tent Map
   - SIGN Method
5. Enter your secret message
6. Click **Encode & Save PNG**

The generated image now contains the hidden message.

---

## 🔓 Decode

Recover a hidden message.

### Steps

1. Open **Decode**
2. Select the encoded image
3. Enter the original seed
4. Select the original technique
5. Click **Decode Message**

The hidden text will be displayed.

---

## 📏 Scan

Analyze image capacity.

### Displays

- Resolution
- Pixel count
- Estimated message capacity

---

## 📊 PSNR Analysis

Compare image quality before and after encoding.

### Steps

1. Select original image
2. Select encoded image
3. Click **Calculate PSNR**

### Interpretation

| PSNR | Quality |
|--------|----------|
| >50 dB | Excellent |
| 40–50 dB | Very Good |
| 30–40 dB | Acceptable |
| <30 dB | Noticeable Changes |

---

## 🔢 Binary Visualizer

Convert text into binary representation.

Example:

```text
A = 01000001
```

Useful for understanding how text is stored before embedding.

---

## 📈 Histogram Viewer

Compare color distributions between images.

Useful for visualizing the effect of steganography on:

- Red Channel
- Green Channel
- Blue Channel

---

## 🕵️ Steganalysis

Estimate whether an image contains hidden data.

Possible outcomes:

```text
Clean
Suspicious
Likely Contains Hidden Data
```

Includes a suspicion score.

---

## 🧩 Bit Plane Viewer

Inspect image data one bit plane at a time.

Features:

- Red channel inspection
- Green channel inspection
- Blue channel inspection
- View all 8 bit layers

Useful for educational and forensic purposes.

---

## 📝 History

SecureSteg automatically stores:

- Encode operations
- Decode operations
- Timestamps

Stored locally only.

Users can:

- Delete individual entries
- Clear all history

---

## 📚 Learn

Built-in learning resources covering:

- Steganography
- Chaotic Maps
- LSB Encoding
- XOR Encryption
- PSNR
- Steganalysis

---

# 🧠 How It Works

SecureSteg combines several techniques:

### Chaotic Maps

Pseudo-random sequences are generated from a numeric seed using:

- Logistic Map
- Tent Map
- SIGN Method

### Pixel Shuffling

A Fisher–Yates shuffle distributes message bits across image pixels.

### XOR Encryption

Messages are XOR-encrypted using a key derived from the chaotic sequence before embedding.

### LSB Embedding

Data is stored inside the least significant bits of image color channels.

These modifications are typically invisible to the human eye.

### Verification

Built-in tools allow users to evaluate:

- Visual quality
- Detectability
- Distribution changes

---

# 💾 Data Storage

History is stored locally using a JSON file.

No information is uploaded or transmitted.

Everything remains on your device.

---

# 📦 Building The EXE

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
python -m PyInstaller --onefile --windowed --name SecureSteg main.py
```

Output:

```text
dist/
└── SecureSteg.exe
```

---

# 🔮 Future Improvements

- 📄 Export reports as PDF
- 🌗 Light theme support
- 🔐 Password-based encryption
- 📊 Advanced steganalysis metrics
- 🎚️ Additional embedding techniques

---

# 🔒 Privacy

SecureSteg runs entirely on your local machine.

- No cloud services
- No telemetry
- No external servers
- No internet required

Your images and messages never leave your device.

---

# 📄 License

This project was created for educational and research purposes.

Feel free to study and learn from the code. Please do not redistribute it as your own work.

---

## 🙏 Credits

- Python
- PyQt5
- NumPy
- Pillow
- PyInstaller
