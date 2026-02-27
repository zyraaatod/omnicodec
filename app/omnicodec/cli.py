from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from .engine import OmniCodecEngine
from .models import MethodSpec
from .tui import (
    banner,
    home_panel,
    methods_panel,
    print_error,
    print_info,
    print_success,
    print_warning,
    prompt,
    clear_screen,
    separator,
    C,
)


def _parse_options(raw: str | None) -> dict:
    if not raw:
        return {}
    return json.loads(raw)


def _read_input(text: str | None, file: str | None) -> bytes:
    if text is not None:
        return text.encode("utf-8")
    if file is not None:
        return Path(file).read_bytes()
    raise ValueError("Provide --text or --file")


def _format_method_line(spec: MethodSpec) -> str:
    modes = []
    if spec.encode:
        modes.append("enc")
    if spec.decode:
        modes.append("dec")
    if spec.verify:
        modes.append("ver")
    return f"{spec.key:20} [{'/'.join(modes):7}] {spec.description}"


def _methods_by_mode(engine: OmniCodecEngine, mode: str) -> list[MethodSpec]:
    methods = []
    for spec in engine.list_methods():
        if mode == "encode" and spec.encode is not None:
            methods.append(spec)
        if mode == "decode" and spec.decode is not None:
            methods.append(spec)
    return methods


def cmd_list(engine: OmniCodecEngine, category: str | None = None) -> int:
    """List all available methods, optionally filtered by category."""
    clear_screen()
    print("")
    print(banner())
    print("")
    
    by_cat = engine.categories()
    
    if category:
        rows = [_format_method_line(s) for s in by_cat.get(category, [])]
        if not rows:
            print_error(f"Category not found: {category}")
            return 1
        print(methods_panel(category, rows))
        return 0

    for cat, specs in by_cat.items():
        rows = [_format_method_line(s) for s in specs]
        print(methods_panel(cat, rows))
        print("")  # Empty line between categories
    return 0


def cmd_run(args: argparse.Namespace, engine: OmniCodecEngine) -> int:
    """Run a single transform operation from CLI."""
    options = _parse_options(args.options)
    data = _read_input(args.text, args.file)
    expected = args.expected.encode("utf-8") if args.expected else None
    
    result = engine.run(
        method_key=args.method,
        mode=args.mode,
        input_data=data,
        options=options,
        expected=expected,
        autosave=not args.no_autosave,
    )
    
    print("")
    print(result.output.decode("utf-8", errors="replace"))
    
    if result.output_path:
        print_info(f"Saved: {result.output_path}")
    print("")
    return 0


def cmd_detect(args: argparse.Namespace, engine: OmniCodecEngine) -> int:
    """Detect likely encoding method from input data."""
    data = _read_input(args.text, args.file)
    cands = engine.detect(data)
    
    print("")
    if not cands:
        print_info("No candidates detected - input doesn't match known patterns")
    else:
        print_success(f"Detected {len(cands)} candidate(s):")
        print(f"  {', '.join(cands)}")
    print("")
    return 0


def _uptime(seconds: float) -> str:
    sec = int(seconds)
    hh = sec // 3600
    mm = (sec % 3600) // 60
    ss = sec % 60
    return f"{hh:02}:{mm:02}:{ss:02}"


def _redraw(engine: OmniCodecEngine, started_at: float, last_action: str) -> None:
    """Clear screen and redraw the main interface."""
    clear_screen()
    print("")
    print(banner())
    print("")
    total_methods = len(engine.list_methods())
    total_categories = len(engine.categories())
    print(home_panel(total_methods, total_categories, _uptime(time.time() - started_at), last_action))
    print("")


def _choose_feature() -> str | None:
    """Choose input feature: text or file."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info("Pilih fitur input:")
    print(f"  {C.cyan}[1]{C.reset} text  - Ketik/paste text langsung")
    print(f"  {C.cyan}[2]{C.reset} file  - Browse dan pilih file")
    print(f"  {C.cyan}[q]{C.reset} back  - Kembali ke menu")
    print("")
    
    while True:
        pick = input(prompt()).strip().lower()
        if pick in {"1", "text", "t"}:
            return "text"
        if pick in {"2", "file", "f"}:
            return "file"
        if pick in {"q", "batal", "cancel", "back"}:
            return None
        print_error("Pilihan tidak valid. Gunakan 1/2/q.")
        print("")


def _collect_by_feature(feature: str) -> bytes:
    """Collect input data based on selected feature."""
    if feature == "text":
        print_info("Masukkan text input (tekan Enter untuk selesai):")
        print("")
        return input(prompt()).encode("utf-8")

    clear_screen()
    print("")
    print(banner())
    print("")
    print_info("Masukkan path file:")
    print("")
    path = Path(input(prompt()).strip().strip('"'))
    if not path.exists() or not path.is_file():
        raise ValueError(f"File tidak ditemukan: {path}")
    return path.read_bytes()


def _choose_method(engine: OmniCodecEngine, mode: str) -> str | None:
    """Choose encoding/decoding method from available options."""
    methods = _methods_by_mode(engine, mode)
    
    # Group by category for better organization
    by_category: dict[str, list] = {}
    for spec in methods:
        cat = spec.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(spec)
    
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"Tersedia {len(methods)} method untuk {mode}:")
    print("")
    
    idx = 1
    for cat, specs in sorted(by_category.items()):
        print(f"{C.yellow}{C.bold}{cat}:{C.reset}")
        for spec in specs:
            print(f"  {C.cyan}[{idx:02}]{C.reset} {spec.key:22} - {spec.description}")
            idx += 1
        print("")
    
    print_info("Pilih nomor method, nama method, atau ketik 'q' untuk batal:")
    print("")
    
    while True:
        pick = input(prompt()).strip().lower()
        if pick in {"q", "batal", "cancel", "back"}:
            return None
        if pick.isdigit():
            i = int(pick)
            if 1 <= i <= len(methods):
                return methods[i - 1].key
            print_error("Nomor di luar daftar.")
            print("")
            continue
        try:
            spec = engine.registry.get(pick)
        except KeyError:
            print_error("Method tidak dikenal.")
            print("")
            continue
        if mode == "encode" and spec.encode is None:
            print_error("Method ini tidak support encode.")
            print("")
            continue
        if mode == "decode" and spec.decode is None:
            print_error("Method ini tidak support decode.")
            print("")
            continue
        return spec.key


def _show_result_preview(data: bytes) -> None:
    """Show preview of output data."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.green}{C.bold}HASIL ENCODE/DECODE:{C.reset}")
    print("")
    print(separator())
    print("")
    
    preview = data[:512].decode("utf-8", errors="replace")
    print(preview)
    
    if len(data) > 512:
        print("")
        print_warning(f"... ({len(data)} bytes total, menampilkan 512 bytes pertama)")
    print("")


def _show_help() -> None:
    """Show help information."""
    clear_screen()
    print("")
    print(banner())
    print("")
    
    lines = [
        f"{C.yellow}{C.bold}Quick Commands:{C.reset}",
        f"  {C.cyan}1, enc, e{C.reset}       - Encode mode (1 method)",
        f"  {C.cyan}2, dec, d{C.reset}       - Decode mode",
        f"  {C.cyan}3, list, ls, l{C.reset}   - List all methods",
        f"  {C.cyan}a, encall, all{C.reset}   - ⭐ ENCODE ALL! (1 file → semua method enc)",
        f"  {C.cyan}x, allinone{C.reset}      - 🔥 ALL IN ONE! (1 file → ENC+DEC semua method)",
        f"  {C.cyan}clear, cls, c{C.reset}    - Clear screen",
        f"  {C.cyan}help, h, ?{C.reset}      - Show this help",
        f"  {C.cyan}q, quit, exit{C.reset}    - Exit application",
        "",
        f"{C.yellow}{C.bold}Standard Flow:{C.reset}",
        f"  Menu → [1] ENC → Pilih input → Pilih method → Auto-save",
        f"  Menu → [2] DEC → Pilih input → Auto-detect → Auto-save",
        "",
        f"{C.yellow}{C.bold}Batch Encode:{C.reset}",
        f"  Menu → [a] ENC ALL → Pilih input → Encode semua method → Save semua output",
        "",
        f"{C.yellow}{C.bold}ALL IN ONE (ULTIMATE):{C.reset}",
        f"  Menu → [x] ALL IN ONE → Pilih file → ENC semua method → DEC semua method → Save semua",
        "",
        f"{C.yellow}{C.bold}Tips:{C.reset}",
        f"  • ALL IN ONE menghasilkan 2 folder: encoded/ dan decoded/",
        f"  • Auto-detect decode akan mencoba semua method jika tidak yakin",
        f"  • Gunakan {C.cyan}clear{C.reset} atau {C.cyan}cls{C.reset} untuk membersihkan layar kapan saja",
        "",
    ]
    
    for line in lines:
        print(line)


def _encode_all_methods(engine: OmniCodecEngine) -> str:
    """Encode one input with ALL encode methods at once."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.yellow}{C.bold}ENCODE ALL METHODS - Batch Encode{C.reset}")
    print(separator())
    print("")
    print_info("Fitur ini akan meng-encode 1 input dengan SEMUA method encode!")
    print("")
    
    # Choose input type
    print_info("Pilih jenis input:")
    print(f"  {C.cyan}[1]{C.reset} Text - Ketik text langsung")
    print(f"  {C.cyan}[2]{C.reset} File - Pilih file")
    print(f"  {C.cyan}[q]{C.reset} back - Kembali ke menu")
    print("")
    
    pick = input(prompt()).strip().lower()
    if pick in {"q", "batal", "cancel", "back"}:
        return "Encode all dibatalkan"
    
    # Collect input
    if pick in {"1", "text", "t"}:
        print_info("Masukkan text:")
        input_data = input(prompt()).encode("utf-8")
        input_name = "text_input"
    elif pick in {"2", "file", "f"}:
        clear_screen()
        print("")
        print(banner())
        print("")
        print_info("Masukkan path file:")
        print("")
        path = Path(input(prompt()).strip().strip('"'))
        if not path.exists() or not path.is_file():
            raise ValueError(f"File tidak ditemukan: {path}")
        input_data = path.read_bytes()
        input_name = path.name
    else:
        print_error("Pilihan tidak valid")
        return "Encode all dibatalkan"
    
    # Get all encode methods
    all_methods = [spec for spec in engine.list_methods() if spec.encode is not None]
    
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"Encoding dengan {len(all_methods)} method...")
    print("")
    print(f"Input: {C.cyan}{input_name}{C.reset}")
    print(f"Size: {C.cyan}{len(input_data)} bytes{C.reset}")
    print("")
    print(separator())
    print("")
    
    # Encode with all methods
    success_count = 0
    error_count = 0
    results = []
    
    for i, spec in enumerate(all_methods, start=1):
        try:
            output = spec.encode(input_data, {})
            results.append((spec.key, "OK", len(output)))
            success_count += 1
            print(f"[{i:03}/{len(all_methods)}] {C.green}✓{C.reset} {spec.key:25} → {len(output)} bytes")
        except Exception as e:
            results.append((spec.key, "ERROR", str(e)))
            error_count += 1
            print(f"[{i:03}/{len(all_methods)}] {C.red}✗{C.reset} {spec.key:25} → {str(e)[:50]}")
    
    print("")
    print(separator())
    print("")
    print_success(f"Encode all selesai!")
    print(f"  Sukses: {C.green}{success_count}{C.reset}")
    print(f"  Error:  {C.red}{error_count}{C.reset}")
    print("")
    
    # Save all outputs
    print_info("Menyimpan semua output...")
    print("")
    
    output_dir = engine.io.output_dir
    batch_dir = output_dir / f"batch_{input_name}_{int(time.time())}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for spec_key, status, output_or_error in results:
        if status == "OK":
            try:
                spec = engine.registry.get(spec_key)
                ext = spec.extensions[0] if spec.extensions else ".txt"
                output_path = batch_dir / f"{spec_key}{ext}"
                # Re-encode to get output
                output = spec.encode(input_data, {})
                output_path.write_bytes(output)
                saved_count += 1
            except Exception as e:
                print_error(f"  {spec_key}: {str(e)}")
    
    print("")
    print_success(f"Disimpan {saved_count} file ke: {batch_dir}")
    print("")
    
    input(f"{C.gray}Tekan Enter untuk kembali...{C.reset}")
    return f"ENC ALL: {success_count} methods, {saved_count} saved"


def _get_file_header(data: bytes) -> tuple[bytes, bytes]:
    """Extract header from file based on extension."""
    text = data.decode("utf-8", errors="ignore")
    lines = text.split("\n")
    
    header_lines = []
    body_start = 0
    
    # Check for shebang (bash, python, perl, ruby, etc.)
    if lines[0].startswith("#!"):
        header_lines.append(lines[0])
        body_start = 1
        # Check for second header line (encoding, etc.)
        if len(lines) > 1 and lines[1].startswith("#") and not lines[1].startswith("#!"):
            header_lines.append(lines[1])
            body_start = 2
    
    # Check for HTML doctype
    elif lines[0].strip().upper().startswith("<!DOCTYPE"):
        header_lines.append(lines[0])
        body_start = 1
    
    # Check for XML declaration
    elif lines[0].strip().startswith("<?xml"):
        header_lines.append(lines[0])
        body_start = 1
    
    # Check for PHP tag
    elif lines[0].strip().startswith("<?php"):
        header_lines.append(lines[0])
        body_start = 1
    
    # Check for batch file header
    elif lines[0].strip().lower().startswith("@echo"):
        header_lines.append(lines[0])
        body_start = 1
    
    # Check for PowerShell comment header
    elif lines[0].strip().startswith("#") and "powershell" in lines[0].lower():
        header_lines.append(lines[0])
        body_start = 1
    
    header = "\n".join(header_lines)
    body = "\n".join(lines[body_start:])
    
    return header.encode("utf-8"), body.encode("utf-8")


def _spesial_enc(engine: OmniCodecEngine) -> str:
    """SPESIAL ENC - 1 file target, 1 file result, semua encoding tanpa label."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.yellow}{C.bold}SPESIAL ENCODE - All Encodings in One File{C.reset}")
    print(separator())
    print("")
    print_info("1 file → 1 file (semua encoding, tanpa label, preserve header)")
    print("")
    
    # Input file
    print_info("Masukkan path file target:")
    print("")
    path = Path(input(prompt()).strip().strip('"'))
    if not path.exists() or not path.is_file():
        raise ValueError(f"File tidak ditemukan: {path}")
    
    input_data = path.read_bytes()
    input_name = path.stem
    input_ext = path.suffix
    
    # Extract header
    header, body = _get_file_header(input_data)
    
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"Processing: {path.name}")
    print(f"Header: {C.green}Preserved{C.reset}")
    print(f"Body size: {C.cyan}{len(body)} bytes{C.reset}")
    print("")
    print(separator())
    print("")
    
    # Get all encode methods
    all_methods = [spec for spec in engine.list_methods() if spec.encode is not None]
    
    print_info(f"Encoding dengan {len(all_methods)} method...")
    print("")
    
    # Encode with all methods
    encoded_lines = []
    success_count = 0
    error_count = 0
    
    for i, spec in enumerate(all_methods, start=1):
        try:
            output = spec.encode(body, {})
            # Convert to text and add to lines
            encoded_text = output.decode("utf-8", errors="replace").strip()
            # Remove any newlines from encoded text
            encoded_text = encoded_text.replace("\n", "\\n")
            encoded_lines.append(encoded_text)
            success_count += 1
            print(f"[{i:03}/{len(all_methods)}] {C.green}✓{C.reset} {spec.key:25}")
        except Exception as e:
            error_count += 1
            print(f"[{i:03}/{len(all_methods)}] {C.red}✗{C.reset} {spec.key:25} → {str(e)[:40]}")
    
    print("")
    print(separator())
    print("")
    
    # Generate output file
    output_name = f"{input_name}-enc{input_ext}"
    output_path = path.parent / output_name
    
    # Build output content
    output_lines = []
    
    # Add header
    if header:
        output_lines.append(header.decode("utf-8", errors="ignore"))
    
    # Add comment
    output_lines.append(f"# OMNICODEC ENCODED - {success_count} encodings")
    output_lines.append(f"# Original: {path.name}")
    output_lines.append(f"# Decode: python start.py spesial-dec <file>")
    output_lines.append("")
    
    # Add all encoded lines
    output_lines.extend(encoded_lines)
    
    # Write output
    output_content = "\n".join(output_lines)
    output_path.write_text(output_content, encoding="utf-8")
    
    print_success(f"Saved: {output_path}")
    print(f"  Original: {len(input_data)} bytes")
    print(f"  Encoded: {len(output_content)} bytes")
    print(f"  Encodings: {success_count}")
    print("")
    
    input(f"{C.gray}Tekan Enter untuk kembali...{C.reset}")
    return f"SPESIAL ENC: {output_name}"


def _spesial_dec(engine: OmniCodecEngine) -> str:
    """SPESIAL DEC - Decode file from spesial enc."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.green}{C.bold}SPESIAL DECODE - Restore Original File{C.reset}")
    print(separator())
    print("")
    print_info("Decode file dari spesial enc → restore original")
    print("")
    
    # Input file
    print_info("Masukkan path file encoded:")
    print("")
    path = Path(input(prompt()).strip().strip('"'))
    if not path.exists() or not path.is_file():
        raise ValueError(f"File tidak ditemukan: {path}")
    
    input_content = path.read_text(encoding="utf-8")
    input_name = path.stem.replace("-enc", "")
    input_ext = path.suffix
    
    # Parse file
    lines = input_content.split("\n")
    header_lines = []
    encoded_lines = []
    in_body = False
    
    for line in lines:
        if not in_body:
            if line.startswith("# OMNICODEC"):
                in_body = True
                continue
            elif line.startswith("#") or line.strip() == "":
                header_lines.append(line)
                continue
            else:
                in_body = True
        
        if line.strip():
            encoded_lines.append(line)
    
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"Processing: {path.name}")
    print(f"Encoded lines: {C.cyan}{len(encoded_lines)}{C.reset}")
    print("")
    print(separator())
    print("")
    
    # Try to decode with all methods
    all_methods = [spec for spec in engine.list_methods() if spec.decode is not None]
    
    print_info("Trying to decode...")
    print("")
    
    decoded_results = {}
    
    for i, spec in enumerate(all_methods, start=1):
        try:
            # Try first few encoded lines
            for enc_line in encoded_lines[:5]:
                # Unescape newlines
                enc_line = enc_line.replace("\\n", "\n")
                output = spec.decode(enc_line.encode("utf-8"), {})
                # Check if result looks like valid data
                if output and len(output) > 0:
                    decoded_results[spec.key] = output
                    print(f"[{i:03}/{len(all_methods)}] {C.green}✓{C.reset} {spec.key:25} → {len(output)} bytes")
                    break
        except Exception:
            pass
    
    print("")
    print(separator())
    print("")
    
    if not decoded_results:
        print_error("Tidak ada yang bisa di-decode!")
        input(f"{C.gray}Tekan Enter untuk kembali...{C.reset}")
        return "SPESIAL DEC: Failed"
    
    # Use first successful decode as result
    first_key = list(decoded_results.keys())[0]
    decoded_data = decoded_results[first_key]
    
    # Generate output file
    output_name = f"{input_name}{input_ext}"
    output_path = path.parent / output_name
    
    # Add header back
    header_text = "\n".join(header_lines)
    if header_text.strip():
        output_content = header_text + "\n" + decoded_data.decode("utf-8", errors="replace")
    else:
        output_content = decoded_data.decode("utf-8", errors="replace")
    
    output_path.write_text(output_content, encoding="utf-8")
    
    print_success(f"Restored: {output_path}")
    print(f"  Method: {first_key}")
    print(f"  Size: {len(output_content)} bytes")
    print(f"  Decoded: {len(decoded_results)} methods succeeded")
    print("")
    
    input(f"{C.gray}Tekan Enter untuk kembali...{C.reset}")
    return f"SPESIAL DEC: {output_name}"
    """ALL IN ONE - Process 1 file with ALL encode AND decode methods."""
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.red}{C.bold}🔥 ALL IN ONE - ULTIMATE PROCESSOR 🔥{C.reset}")
    print(separator())
    print("")
    print_info("Process 1 file dengan SEMUA method ENC + DEC sekaligus!")
    print("")
    
    # Choose input
    print_info("Pilih input file:")
    print("")
    path = Path(input(prompt()).strip().strip('"'))
    if not path.exists() or not path.is_file():
        raise ValueError(f"File tidak ditemukan: {path}")
    
    input_data = path.read_bytes()
    input_name = path.name
    
    clear_screen()
    print("")
    print(banner())
    print("")
    print_info(f"{C.red}{C.bold}PROCESSING: {input_name}{C.reset}")
    print(f"Size: {C.cyan}{len(input_data)} bytes{C.reset}")
    print("")
    print(separator())
    print("")
    
    # Get all methods
    all_methods = engine.list_methods()
    encode_methods = [spec for spec in all_methods if spec.encode is not None]
    decode_methods = [spec for spec in all_methods if spec.decode is not None]
    
    print_info(f"Total: {len(all_methods)} methods")
    print(f"  Encode: {C.green}{len(encode_methods)}{C.reset}")
    print(f"  Decode: {C.blue}{len(decode_methods)}{C.reset}")
    print("")
    print(separator())
    print("")
    
    # ENCODE ALL
    print_info(f"{C.green}{C.bold}PHASE 1: ENCODE ALL{C.reset}")
    print("")
    
    enc_success = 0
    enc_error = 0
    enc_results = []
    
    for i, spec in enumerate(encode_methods, start=1):
        try:
            output = spec.encode(input_data, {})
            enc_results.append((spec.key, "OK", len(output)))
            enc_success += 1
            print(f"[ENC {i:03}/{len(encode_methods)}] {C.green}✓{C.reset} {spec.key:25} → {len(output)} bytes")
        except Exception as e:
            enc_results.append((spec.key, "ERROR", str(e)))
            enc_error += 1
            print(f"[ENC {i:03}/{len(encode_methods)}] {C.red}✗{C.reset} {spec.key:25} → {str(e)[:40]}")
    
    print("")
    print(separator())
    print("")
    
    # DECODE ALL
    print_info(f"{C.blue}{C.bold}PHASE 2: DECODE ALL{C.reset}")
    print("")
    
    dec_success = 0
    dec_error = 0
    dec_results = []
    
    for i, spec in enumerate(decode_methods, start=1):
        try:
            output = spec.decode(input_data, {})
            dec_results.append((spec.key, "OK", len(output)))
            dec_success += 1
            print(f"[DEC {i:03}/{len(decode_methods)}] {C.green}✓{C.reset} {spec.key:25} → {len(output)} bytes")
        except Exception as e:
            dec_results.append((spec.key, "ERROR", str(e)))
            dec_error += 1
            print(f"[DEC {i:03}/{len(decode_methods)}] {C.red}✗{C.reset} {spec.key:25} → {str(e)[:40]}")
    
    print("")
    print(separator())
    print("")
    
    # SUMMARY
    print_info(f"{C.red}{C.bold}🔥 ALL IN ONE COMPLETE! 🔥{C.reset}")
    print("")
    print(f"  ENCODE: {C.green}{enc_success} sukses{C.reset}, {C.red}{enc_error} error{C.reset}")
    print(f"  DECODE: {C.blue}{dec_success} sukses{C.reset}, {C.red}{dec_error} error{C.reset}")
    print("")
    
    # SAVE ALL
    print_info("Menyimpan semua output...")
    print("")
    
    output_dir = engine.io.output_dir
    batch_dir = output_dir / f"allinone_{input_name}_{int(time.time())}"
    enc_dir = batch_dir / "encoded"
    dec_dir = batch_dir / "decoded"
    enc_dir.mkdir(parents=True, exist_ok=True)
    dec_dir.mkdir(parents=True, exist_ok=True)
    
    # Save encoded
    enc_saved = 0
    for spec_key, status, _ in enc_results:
        if status == "OK":
            try:
                spec = engine.registry.get(spec_key)
                ext = spec.extensions[0] if spec.extensions else ".txt"
                output = spec.encode(input_data, {})
                (enc_dir / f"{spec_key}{ext}").write_bytes(output)
                enc_saved += 1
            except Exception:
                pass
    
    # Save decoded
    dec_saved = 0
    for spec_key, status, _ in dec_results:
        if status == "OK":
            try:
                spec = engine.registry.get(spec_key)
                ext = spec.extensions[0] if spec.extensions else ".dec"
                output = spec.decode(input_data, {})
                (dec_dir / f"{spec_key}{ext}").write_bytes(output)
                dec_saved += 1
            except Exception:
                pass
    
    print("")
    print_success(f"Disimpan ke: {batch_dir}")
    print(f"  Encoded: {C.green}{enc_saved} files{C.reset}")
    print(f"  Decoded: {C.blue}{dec_saved} files{C.reset}")
    print("")
    
    input(f"{C.gray}Tekan Enter untuk kembali...{C.reset}")
    return f"ALL IN ONE: ENC={enc_success}, DEC={dec_success}"


def _encode_flow(engine: OmniCodecEngine) -> str:
    """Run the encode workflow."""
    feature = _choose_feature()
    if feature is None:
        return "Encode dibatalkan"

    method = _choose_method(engine, "encode")
    if method is None:
        return "Encode dibatalkan"

    input_data = _collect_by_feature(feature)
    result = engine.run(method_key=method, mode="encode", input_data=input_data, autosave=True)
    
    _show_result_preview(result.output)
    if result.output_path:
        print_success(f"Auto-saved: {result.output_path}")
    
    input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
    return f"ENC {method} via {feature}"


def _decode_flow(engine: OmniCodecEngine) -> str:
    """Run the decode workflow."""
    feature = _choose_feature()
    if feature is None:
        return "Decode dibatalkan"

    input_data = _collect_by_feature(feature)

    clear_screen()
    print("")
    print(banner())
    print("")
    print_info("Opsi decode:")
    print(f"  {C.cyan}[1]{C.reset} auto detect encoding (recommended)")
    print(f"  {C.cyan}[2]{C.reset} manual pilih method")
    print("")
    
    dec_opt = input(prompt()).strip().lower()

    method: str | None = None
    if dec_opt in {"1", "auto", "detect"}:
        # Use detect_with_decode for better accuracy
        from .detect import detect_with_decode
        candidates = detect_with_decode(engine, input_data)
        
        # Filter to only methods that have decode function
        valid: list[str] = []
        for key in candidates:
            try:
                spec = engine.registry.get(key)
                if spec.decode is not None:
                    valid.append(spec.key)
            except KeyError:
                continue

        if not valid:
            # Fallback: try all methods that have decode
            clear_screen()
            print("")
            print(banner())
            print("")
            print_warning("Auto-detect tidak yakin, mencoba semua method...")
            print("")
            for spec in engine.list_methods():
                if spec.decode is not None:
                    try:
                        spec.decode(input_data, {})
                        valid.append(spec.key)
                    except Exception:
                        pass
        
        if len(valid) == 1:
            method = valid[0]
            print_success(f"Auto-detect: {method}")
        elif len(valid) > 1:
            clear_screen()
            print("")
            print(banner())
            print("")
            print_info(f"Ditemukan {len(valid)} kandidat:")
            print("")
            for i, key in enumerate(valid[:10], start=1):  # Show max 10
                print(f"  {C.cyan}[{i}]{C.reset} {key}")
            if len(valid) > 10:
                print(f"  ... dan {len(valid) - 10} lainnya")
            print("")
            pick = input(prompt()).strip()
            if pick.isdigit() and 1 <= int(pick) <= len(valid):
                method = valid[int(pick) - 1]
            else:
                method = valid[0]  # Default to first
                print_info(f"Menggunakan: {method}")
        else:
            # No candidates, let user choose manually
            clear_screen()
            print("")
            print(banner())
            print("")
            print_warning("Tidak ada encoding terdeteksi, pilih manual:")
            print("")
            method = _choose_method(engine, "decode")
    else:
        method = _choose_method(engine, "decode")

    if method is None:
        return "Decode dibatalkan"

    result = engine.run(method_key=method, mode="decode", input_data=input_data, autosave=True)
    
    _show_result_preview(result.output)
    if result.output_path:
        print_success(f"Auto-saved: {result.output_path}")
    
    input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
    return f"DEC {method} via {feature}"


def cmd_interactive(engine: OmniCodecEngine) -> int:
    """Main interactive loop."""
    started_at = time.time()
    last_action = "Session started"
    _redraw(engine, started_at, last_action)

    while True:
        raw = input(prompt()).strip().lower()

        # Clear screen commands
        if raw in {"clear", "cls", "c", "refresh", "4"}:
            _redraw(engine, started_at, last_action)
            continue

        if raw in {"q", "quit", "exit"}:
            clear_screen()
            print_info("Goodbye! Thank you for using OMNICODEC")
            print("")
            return 0
        if raw in {"3", "list", "ls", "l"}:
            clear_screen()
            cmd_list(engine)
            last_action = "List methods"
            input(f"\n{C.gray}Tekan Enter untuk kembali...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"1", "enc", "encode", "e"}:
            try:
                last_action = _encode_flow(engine)
            except Exception as exc:  # noqa: BLE001
                print_error(str(exc))
                input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"2", "dec", "decode", "d"}:
            try:
                last_action = _decode_flow(engine)
            except Exception as exc:  # noqa: BLE001
                print_error(str(exc))
                input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"s", "spesial", "special", "sp"}:
            try:
                clear_screen()
                print("")
                print(banner())
                print("")
                print_info(f"{C.yellow}{C.bold}SPESIAL MENU:{C.reset}")
                print(f"  {C.cyan}[1]{C.reset} SPESIAL ENC - 1 file → 1 file (all encodings)")
                print(f"  {C.cyan}[2]{C.reset} SPESIAL DEC - Restore file from spesial enc")
                print(f"  {C.cyan}[q]{C.reset} Back to menu")
                print("")
                pick = input(prompt()).strip().lower()
                if pick in {"1", "enc", "e"}:
                    last_action = _spesial_enc(engine)
                elif pick in {"2", "dec", "d"}:
                    last_action = _spesial_dec(engine)
                elif pick in {"q", "back", "b"}:
                    pass
                else:
                    print_error("Pilihan tidak valid")
            except Exception as exc:  # noqa: BLE001
                print_error(str(exc))
                input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"a", "encall", "encodeall", "all", "batch"}:
            try:
                last_action = _encode_all_methods(engine)
            except Exception as exc:  # noqa: BLE001
                print_error(str(exc))
                input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"x", "allinone", "all-in-one", "one", "ultimate"}:
            try:
                last_action = _all_in_one(engine)
            except Exception as exc:  # noqa: BLE001
                print_error(str(exc))
                input(f"{C.gray}Tekan Enter untuk lanjut...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue
        if raw in {"help", "h", "?", ""}:
            _show_help()
            input(f"\n{C.gray}Tekan Enter untuk kembali...{C.reset}")
            _redraw(engine, started_at, last_action)
            continue

        print_error(f"Perintah tidak dikenali: {raw}")
        print_info("Gunakan: 1/enc, 2/dec, 3/list, s/spesial, a/enc-all, x/all-in-one, clear/cls, q/quit, help/?")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="omnicodec", description="Universal encode/decode toolkit")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all methods")
    sub.add_parser("interactive", help="Start interactive shell")

    run = sub.add_parser("run", help="Run transform")
    run.add_argument("--mode", choices=["encode", "decode", "verify"], required=True)
    run.add_argument("--method", required=True)
    run.add_argument("--text")
    run.add_argument("--file")
    run.add_argument("--expected", help="Required for verify mode")
    run.add_argument("--options", help="JSON options object")
    run.add_argument("--no-autosave", action="store_true")

    detect = sub.add_parser("detect", help="Detect likely method")
    detect.add_argument("--text")
    detect.add_argument("--file")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    engine = OmniCodecEngine()

    if args.command == "list":
        return cmd_list(engine)
    if args.command == "run":
        return cmd_run(args, engine)
    if args.command == "detect":
        return cmd_detect(args, engine)
    if args.command == "interactive":
        return cmd_interactive(engine)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
