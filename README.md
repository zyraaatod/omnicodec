<div align="center">

# 🔓 OMNICODEC

### **Universal Encode/Decode Toolkit**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Methods](https://img.shields.io/badge/Methods-169+-orange.svg)]()
[![Categories](https://img.shields.io/badge/Categories-25+-purple.svg)]()

**Encode • Decode • Detect • Batch Process • All-in-One**

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Methods](#-methods)
- [Examples](#-examples)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 About

**OMNICODEC** adalah toolkit encoding/decoding **TERLENGKAP** yang pernah ada! Dengan **169+ methods** di **25+ categories**, OMNICODEC bisa meng-encode dan decode file dengan SEMUA encoding yang ada di dunia.

> 💡 **Satu tool untuk semua encoding!**

<div align="center">

```bash
python start.py
```

</div>

---

## ✨ Features

### 🔥 Core Features

| Feature | Description |
|---------|-------------|
| **🎨 169+ Methods** | Base64, Base32, Hex, Binary, Morse, Braille, dan 160+ lainnya |
| **📦 25+ Categories** | Crypto, Compression, Serialization, Languages, Esoteric, dll |
| **🚀 Auto-Detect** | Deteksi encoding otomatis dengan akurasi tinggi |
| **💾 Auto-Save** | Semua output otomatis tersimpan dengan naming yang rapi |
| **🎭 TUI Cantik** | Terminal User Interface yang bersih dan modern |
| **🔧 Batch Process** | Encode/decode banyak file sekaligus |

### ⭐ Special Features

| Feature | Description |
|---------|-------------|
| **🔥 SPESIAL ENC** | 1 file → 1 file dengan SEMUA encoding (preserve header!) |
| **🔓 SPESIAL DEC** | Restore file dari spesial enc dengan 1 klik |
| **📦 ENC ALL** | Encode 1 file dengan semua method → ~170 files |
| **🎯 ALL IN ONE** | ENC + DEC semua method → ~320 files terorganisir |

---

## 🚀 Quick Start

### Instant Run

```bash
# Clone repository
git clone https://github.com/zyraaatod/omnicodec.git
cd omnicodec

# Run interactive mode
python start.py
```

### Basic Commands

```bash
# Interactive mode (RECOMMENDED)
python start.py

# List all methods
python start.py list

# Encode
python start.py run --mode encode --method base64 --text "Hello World"

# Decode
python start.py run --mode decode --method base64 --text "SGVsbG8gV29ybGQ="

# Auto-detect encoding
python start.py detect --text "48656c6c6f"
```

---

## 📦 Installation

### Requirements

- Python 3.10 atau lebih tinggi
- pip (Python package manager)

### Step by Step

```bash
# 1. Clone repository
git clone https://github.com/zyraaatod/omnicodec.git
cd omnicodec

# 2. (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies (if any)
pip install -e .

# 4. Run
python start.py
```

---

## 💻 Usage

### Interactive Mode

Jalankan OMNICODEC dalam mode interaktif dengan TUI yang cantik:

```bash
python start.py
```

**Menu Utama:**
```
╔══════════════════════════════════════════════════════════════════╗
║  OMNICODEC - Universal Encode/Decode Toolkit                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Statistics:                                                      ║
║    Methods:    169                                                ║
║    Categories: 25                                                 ║
║                                                                   ║
║  Main Menu:                                                       ║
║    [1, e] ENC       - Encode data dengan 1 method                 ║
║    [2, d] DEC       - Decode data back to original                ║
║    [3, l] LIST      - List all available methods                  ║
║    [s] SPESIAL    - 🔥 1 file → 1 file (all encodings) ⭐          ║
║    [a] ENC ALL    - Encode 1 file dengan SEMUA method!            ║
║    [x] ALL IN ONE  - 🔥 ENC+DEC semua method!                     ║
║    [c] CLEAR      - Refresh screen                                ║
║    [q] EXIT       - Exit application                              ║
╚══════════════════════════════════════════════════════════════════╝
```

### Command Line Mode

#### Encode

```bash
# Encode text
python start.py run --mode encode --method base64 --text "Hello World"

# Encode file
python start.py run --mode encode --method gzip --file document.txt

# Encode with options
python start.py run --mode encode --method base64 --text "Hello" --options '{"wrap": 80}'
```

#### Decode

```bash
# Decode text
python start.py run --mode decode --method base64 --text "SGVsbG8gV29ybGQ="

# Decode file
python start.py run --mode decode --method gzip --file document.txt.gz
```

#### Detect

```bash
# Detect encoding
python start.py detect --text "SGVsbG8gV29ybGQ="
python start.py detect --file encoded.txt
```

#### List Methods

```bash
# List all methods
python start.py list

# List by category
python start.py list --category crypto_hash
```

---

## 📚 Methods

### Categories Overview

| Category | Methods | Description |
|----------|---------|-------------|
| **Base-N** | 15+ | Base64, Base32, Base58, Base62, Base91, dll |
| **Binary/Text** | 10+ | Hex, Binary, Octal, Decimal, Nibble |
| **Crypto Hash** | 17+ | MD5, SHA family, BLAKE, RIPEMD, Whirlpool |
| **Checksum** | 11+ | CRC8/16/32, Fletcher, Luhn, Verhoeff, Damm |
| **Compression** | 13+ | Gzip, Zlib, Bzip2, XZ, LZ4, Zstd, Brotli |
| **Serialization** | 13+ | JSON, XML, YAML, CBOR, MessagePack, BSON |
| **Web Escape** | 16+ | URL, HTML, CSS, JavaScript, SQL escape |
| **Unicode** | 19+ | Hiragana, Katakana, Hangul, Arabic, Hebrew |
| **Esoteric** | 11+ | Brainfuck, Whitespace, Zalgo, Emoji, Kaomoji |
| **Visual** | 13+ | Braille, Morse, NATO, Color codes |
| **Scientific** | 12+ | UUID, ULID, NanoID, Geohash, Plus Code |
| **Legacy** | 9+ | BinHex, XXEncode, yEnc, TAR, MIME |
| **... dan 13 categories lainnya!** | | |

### Popular Methods

```
base64, base32, base58, base62, hex, binary, morse, braille
gzip, zlib, bzip2, xz, lz4, zstd, brotli
md5, sha1, sha256, sha512, blake2b, blake3
json, xml, yaml, cbor, msgpack, bson
url, html_entity, javascript_escape, css_escape
hiragana, katakana, hangul, arabic, hebrew, thai
brainfuck, whitespace, zalgo, emoji, kaomoji
uuid, ulid, nanoid, geohash, plus_code
```

---

## 🎓 Examples

### Example 1: Basic Encode/Decode

```bash
# Encode
$ python start.py run --mode encode --method base64 --text "Hello World"
SGVsbG8gV29ybGQ=

# Decode
$ python start.py run --mode decode --method base64 --text "SGVsbG8gV29ybGQ="
Hello World
```

### Example 2: File Encoding

```bash
# Encode file
$ python start.py run --mode encode --method gzip --file document.txt
[+] Saved: document.txt.gz

# Decode file
$ python start.py run --mode decode --method gzip --file document.txt.gz
[+] Restored: document.txt
```

### Example 3: Auto-Detect

```bash
$ python start.py detect --text "48656c6c6f"
[+] Detected 2 candidate(s):
  hex, url
```

### Example 4: Spesial Encode (NEW!)

```bash
# In interactive mode
python start.py
# Choose [s] SPESIAL → [1] SPESIAL ENC
# Input: install.sh
# Output: install-enc.sh (with ALL encodings in 1 file!)
```

### Example 5: Batch Encode

```bash
# In interactive mode
python start.py
# Choose [a] ENC ALL
# Input: document.txt
# Output: batch_document_<timestamp>/ (170+ encoded files!)
```

### Example 6: All-in-One (ULTIMATE!)

```bash
# In interactive mode
python start.py
# Choose [x] ALL IN ONE
# Input: test.txt
# Output: allinone_test_<timestamp>/
#   ├── encoded/ (150 files)
#   └── decoded/ (130 files)
```

---

## 📁 Project Structure

```
omnicodec/
├── start.py                    # Main launcher
├── README.md                   # This file
├── pyproject.toml              # Python project config
├── app/
│   ├── omnicodec/
│   │   ├── __init__.py
│   │   ├── cli.py              # CLI & Interactive TUI
│   │   ├── engine.py           # Core encoding engine
│   │   ├── registry.py         # Method registry
│   │   ├── models.py           # Data models
│   │   ├── config.py           # Configuration
│   │   ├── detect.py           # Auto-detection
│   │   ├── io_manager.py       # File I/O
│   │   ├── tui.py              # TUI helpers
│   │   └── methods/            # All encoding methods
│   │       ├── __init__.py
│   │       ├── base_n.py       # Base64, Base32, etc.
│   │       ├── text_escape.py  # URL, HTML, etc.
│   │       ├── compression.py  # Gzip, Bzip2, etc.
│   │       ├── crypto.py       # Hash, checksum
│   │       ├── serialization.py# JSON, XML, etc.
│   │       ├── esoteric_transport.py
│   │       ├── unicode_languages.py  # NEW!
│   │       ├── esoteric_abnormal.py  # NEW!
│   │       ├── advanced_base_n.py    # NEW!
│   │       ├── web_advanced.py       # NEW!
│   │       ├── serialization_advanced.py  # NEW!
│   │       ├── compression_advanced.py  # NEW!
│   │       ├── crypto_symmetric.py      # NEW!
│   │       ├── visual_advanced.py       # NEW!
│   │       ├── scientific_specialized.py# NEW!
│   │       ├── legacy_archive.py        # NEW!
│   │       └── crypto_extended.py       # NEW!
│   ├── tests/
│   │   └── test_smoke.py
│   └── config.default.json
└── output/                     # Auto-saved outputs
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a new branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Adding New Methods

To add a new encoding method:

1. Create new file in `app/omnicodec/methods/`
2. Implement `encode()` and `decode()` functions
3. Add `get_specs()` function
4. Register in `methods/__init__.py`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the concept of universal encoding
- Built with ❤️ using Python
- Thanks to all contributors!

---

<div align="center">

### **Made with ❤️ by [@zyraaatod](https://github.com/zyraaatod)**

[![GitHub stars](https://img.shields.io/github/stars/zyraaatod/omnicodec?style=social)](https://github.com/zyraaatod/omnicodec/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/zyraaatod/omnicodec?style=social)](https://github.com/zyraaatod/omnicodec/network)
[![GitHub issues](https://img.shields.io/github/issues/zyraaatod/omnicodec)](https://github.com/zyraaatod/omnicodec/issues)

**🌟 Star this repo if you find it useful! 🌟**

</div>
