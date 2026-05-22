#!/usr/bin/env python3
"""
Host side script to check the LOAD fields of shared libraries using NDK llvm-objdump.
This script extracts and analyzes SO files from APK/AAR packages and summarizes by alignment.

Usage: check_so_load.py [input-path|input-APK|input-AAR]

Environment variables:
  ANDROID_NDK - Path to Android NDK (required)
"""

import os
import sys
import tempfile
import shutil
import subprocess
import zipfile
import re
import argparse
from pathlib import Path
from collections import defaultdict


def cleanup_temp_dir(temp_dir):
    """Clean up temporary directory"""
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def get_llvm_objdump_path():
    """Get the path to llvm-objdump from ANDROID_NDK"""
    android_ndk = os.environ.get('ANDROID_NDK')
    if not android_ndk:
        print("Error: ANDROID_NDK environment variable is not set.", file=sys.stderr)
        print("Please set it to your NDK installation path.", file=sys.stderr)
        sys.exit(1)

    llvm_objdump = os.path.join(
        android_ndk, "toolchains", "llvm", "prebuilt", "darwin-x86_64", "bin", "llvm-objdump")

    if not os.path.isfile(llvm_objdump):
        print(
            f"Error: llvm-objdump not found at {llvm_objdump}", file=sys.stderr)
        print("Please check your ANDROID_NDK path.", file=sys.stderr)
        sys.exit(1)

    return llvm_objdump


def extract_apk(apk_path, temp_dir):
    """Extract SO files from APK"""
    print("Extracting SO files from APK...")

    try:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            # Try to extract lib/* first
            lib_files = [f for f in zip_ref.namelist() if f.startswith(
                'lib/arm64-v8a') and f.endswith('.so')]
            if lib_files:
                for file in lib_files:
                    zip_ref.extract(file, temp_dir)
            else:
                # If no lib/* found, extract all files
                print("Warning: No lib/arm64-v8a/*.so files found, extracting all files...")
                zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        print(f"Error extracting APK: {e}", file=sys.stderr)
        sys.exit(1)


def extract_aar(aar_path, temp_dir):
    """Extract SO files from AAR"""
    print("Extracting SO files from AAR...")

    try:
        with zipfile.ZipFile(aar_path, 'r') as zip_ref:
            # Try to extract jni/* first (common location for SO files in AAR)
            jni_files = [f for f in zip_ref.namelist() if f.startswith(
                'jni/arm64-v8a') and f.endswith('.so')]
            if jni_files:
                for file in jni_files:
                    zip_ref.extract(file, temp_dir)
            else:
                # Also check for lib/* (alternative location)
                lib_files = [f for f in zip_ref.namelist() if f.startswith(
                    'lib/arm64-v8a') and f.endswith('.so')]
                if lib_files:
                    for file in lib_files:
                        zip_ref.extract(file, temp_dir)
                else:
                    # If no jni/* or lib/* found, extract all files
                    print(
                        "Warning: No jni/arm64-v8a/*.so or lib/arm64-v8a/*.so files found, extracting all files...")
                    zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        print(f"Error extracting AAR: {e}", file=sys.stderr)
        sys.exit(1)


def is_elf_file(file_path):
    """Check if file is an ELF file"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'\x7fELF'
    except:
        return False


def get_load_fields(llvm_objdump_path, so_file):
    """Get LOAD fields from SO file using llvm-objdump"""
    try:
        result = subprocess.run([llvm_objdump_path, '-p', so_file],
                                capture_output=True, text=True, check=True)
        load_lines = [line for line in result.stdout.split(
            '\n') if 'LOAD' in line]
        return load_lines
    except subprocess.CalledProcessError as e:
        print(f"Failed to run llvm-objdump on {so_file}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error processing {so_file}: {e}", file=sys.stderr)
        return []


def parse_alignment(align_str):
    """Parse alignment string like '2**16' and return power and human readable format"""
    match = re.match(r'2\*\*(\d+)', align_str)
    if match:
        power = int(match.group(1))
        actual_value = 2 ** power

        # Convert to human readable format
        if actual_value >= 1048576:  # 1MB
            mb_value = actual_value // 1048576
            size_display = f"{mb_value}M"
        elif actual_value >= 1024:  # 1KB
            kb_value = actual_value // 1024
            size_display = f"{kb_value}K"
        else:
            size_display = f"{actual_value}B"

        return power, actual_value, size_display
    return None, None, None


def get_alignment_sort_key(align_str):
    """Extract alignment power for sorting, handling None cases"""
    match = re.search(r'2\*\*(\d+)', align_str)
    return int(match.group(1)) if match else 0


def format_size(size_bytes):
    """Format size in bytes to human readable format"""
    if size_bytes >= 1048576:  # 1MB
        return f"{size_bytes // 1048576}M"
    elif size_bytes >= 1024:  # 1KB
        return f"{size_bytes // 1024}K"
    else:
        return f"{size_bytes}B"


def main():
    parser = argparse.ArgumentParser(
        description="Check LOAD fields of shared libraries using NDK llvm-objdump",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  ANDROID_NDK - Path to Android NDK (required)
        """
    )
    parser.add_argument(
        'input_path', help='Path to SO files, APK file, or AAR file')

    args = parser.parse_args()

    input_path = args.input_path

    if not os.path.exists(input_path):
        print(f"Invalid file: {input_path}", file=sys.stderr)
        sys.exit(1)

    llvm_objdump_path = get_llvm_objdump_path()
    temp_dir = None

    try:
        # Handle APK and AAR files
        if input_path.endswith('.apk'):
            print(f"\nAnalyzing APK: {input_path}\n")
            temp_dir = tempfile.mkdtemp(
                prefix=f"{Path(input_path).stem}_so_load_")
            work_dir = extract_apk(input_path, temp_dir)
        elif input_path.endswith('.aar'):
            print(f"\nAnalyzing AAR: {input_path}\n")
            temp_dir = tempfile.mkdtemp(
                prefix=f"{Path(input_path).stem}_so_load_")
            work_dir = extract_aar(input_path, temp_dir)
        else:
            work_dir = input_path

        print("\n=== SO LOAD Fields Analysis ===")
        print(f"Using: {llvm_objdump_path}\n")

        # Find all SO files
        so_files = []
        for root, dirs, files in os.walk(work_dir):
            for file in files:
                if file.endswith('.so'):
                    so_files.append(os.path.join(root, file))

        if not so_files:
            print("No SO files found in the specified path.")
            return

        # Arrays to store alignment data
        alignment_count = defaultdict(int)
        alignment_files = defaultdict(list)
        so_count = 0

        for so_file in so_files:
            # Check if it's an ELF file
            if not is_elf_file(so_file):
                continue

            so_count += 1
            print(f"--- {os.path.basename(so_file)} ---")
            print(f"Path: {so_file}")

            # Get LOAD fields
            load_output = get_load_fields(llvm_objdump_path, so_file)

            if load_output:
                for line in load_output:
                    print(line)

                # Extract alignment values
                alignments = set()
                for line in load_output:
                    parts = line.split()
                    if parts and parts[-1].startswith('2**'):
                        alignments.add(parts[-1])

                for align in alignments:
                    alignment_count[align] += 1
                    alignment_files[align].append(os.path.basename(so_file))
            else:
                print("Failed to get LOAD fields or no LOAD fields found")

            print()

        print("=== Summary ===")
        print(f"Analyzed {so_count} SO files\n")

        # Display alignment summary
        if alignment_count:
            print("=== Alignment Summary ===")
            # Fixed linter error by using separate function for sort key
            for align in sorted(alignment_count.keys(), key=get_alignment_sort_key):
                count = alignment_count[align]
                files = alignment_files[align]

                # Calculate the actual alignment value and convert to human readable format
                power, actual_value, size_display = parse_alignment(align)

                if size_display:
                    print(f"Alignment {align} ({size_display}): {count} files")
                else:
                    print(f"Alignment {align}: {count} files")

                print(f"  Files: {' '.join(files)}")
                print()
        else:
            print("No alignment data found")

        print("=====================")

    finally:
        # Clean up temporary directory
        if temp_dir:
            cleanup_temp_dir(temp_dir)


if __name__ == "__main__":
    main()
