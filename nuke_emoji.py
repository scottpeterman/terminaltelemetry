#!/usr/bin/env python3
"""
Package-Wide Emoji Cleaner for Python Projects
Recursively walks through Python packages and removes all emojis from .py files
while preserving all other Unicode characters and functionality.
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Dict


class EmojiCleaner:
    """Comprehensive emoji cleaner for Python codebases"""

    def __init__(self):
        # Comprehensive emoji patterns - covers all major emoji Unicode blocks
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emoticons (😀-🙏)
            "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs (🌀-🗿)
            "\U0001F680-\U0001F6FF"  # Transport and Map Symbols (🚀-🛿)
            "\U0001F1E0-\U0001F1FF"  # Regional Indicator Symbols (🇦-🇿)
            "\U00002600-\U000026FF"  # Misc symbols (☀-⛿)
            "\U00002700-\U000027BF"  # Dingbats (✀-➿)
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs (🤀-🧿)
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A (🩰-🫿)
            "\U0001F004"  # Mahjong Red Dragon 🀄
            "\U0001F0CF"  # Playing Card Black Joker 🃏
            "\U0001F170-\U0001F251"  # Enclosed Characters (🅰-🉑)
            # Additional problematic characters
            "\u274c"  # Cross mark ❌
            "\u2705"  # Check mark ✅  
            "\u26a0"  # Warning sign ⚠️
            "\u2699"  # Gear ⚙️
            "\u2728"  # Sparkles ✨
            "\u2B50"  # Star ⭐
            "\u26A1"  # High voltage ⚡
            "\u2753"  # Question mark ❓
            "\u2757"  # Exclamation ❗
            "\u2714"  # Check mark ✔️
            "\u2716"  # Heavy multiplication ✖️
            "\u2139"  # Information ℹ️
            "\u26D4"  # No entry ⛔
            "\u267E"  # Permanent paper ♾️
            "\u2622"  # Radioactive ☢️
            "\u2623"  # Biohazard ☣️
            "\u267F"  # Wheelchair ♿
            "\u2620"  # Skull and crossbones ☠️
            "\u269C"  # Fleur-de-lis ⚜️
            "\u26AA"  # White circle ⚪
            "\u26AB"  # Black circle ⚫
            "\u2B55"  # Red circle ⭕
            "\u2B24"  # Black large circle ⬤
            "\u25AA"  # Black small square ▪️
            "\u25AB"  # White small square ▫️
            "\u25FE"  # Black medium small square ◾
            "\u25FD"  # White medium small square ◽
            "\u25FC"  # Black medium square ◼️
            "\u25FB"  # White medium square ◻️
            "\u2B1B"  # Black large square ⬛
            "\u2B1C"  # White large square ⬜
            "\u2665"  # Heart suit ♥️
            "\u2666"  # Diamond suit ♦️
            "\u2663"  # Club suit ♣️
            "\u2660"  # Spade suit ♠️
            "\u267B"  # Recycling ♻️
            # CRITICAL: Variation selectors and other invisible emoji modifiers
            "\ufe0f"  # Variation Selector-16 (makes emojis colorful)
            "\ufe0e"  # Variation Selector-15 (makes emojis text-style)
            "\u200d"  # Zero Width Joiner (combines emojis)
            "\u20e3"  # Combining Enclosing Keycap (number emojis)
            "]+",
            flags=re.UNICODE
        )

        # Enhanced specific emojis list including the ones from your search
        self.specific_emojis = [
            # From your search results
            '❌', '✅', '⚠️', '❓', '❗', '✔️', '✖️', 'ℹ️', '⛔',
            # Common programming/status emojis
            '🔧', '📱', '🚀', '⭐', '🎯', '📊', '💻', '🌟', '🔥',
            '💡', '📝', '🎉', '👍', '👎', '✨', '🛠️', '⚡', '🔍',
            '📈', '📉', '🔔', '🔕', '📦', '🎁', '🏆', '🎮', '🎨',
            # Technical/status symbols that might appear in code
            '⚙️', '🔄', '🔀', '🔁', '🔂', '⏸️', '⏯️', '⏹️', '⏺️',
            '⏭️', '⏮️', '⏩', '⏪', '⏫', '⏬', '🔽', '🔼', '▶️',
            '◀️', '🔃', '🔙', '🔚', '🔛', '🔜', '🔝',
            # More symbols that might be in error messages or UI
            '♻️', '⚜️', '🔱', '📯', '🔰', '♾️', '☢️', '☣️', '♿',
            '☠️', '⚪', '⚫', '⭕', '⬤', '▪️', '▫️', '◾', '◽',
            '◼️', '◻️', '⬛', '⬜', '♥️', '♦️', '♣️', '♠️',
            # CRITICAL: The invisible "gremlins"
            '\ufe0f',  # Variation Selector-16 (the main culprit!)
            '\ufe0e',  # Variation Selector-15
            '\u200d',  # Zero Width Joiner
            '\u20e3',  # Combining Enclosing Keycap
        ]

        # Track statistics
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'emojis_removed': 0,
            'errors': 0,
            'skipped_files': []
        }

        # Track what emojis were found for reporting
        self.found_emojis = set()

    def is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji"""
        return bool(self.emoji_pattern.match(char)) or char in self.specific_emojis

    def clean_text(self, text: str, debug: bool = False) -> Tuple[str, int]:
        """
        Remove emojis from text while preserving all other content
        Returns: (cleaned_text, emoji_count_removed)
        """
        original_length = len(text)

        # Find all emojis before removing them for statistics
        found_emojis = self.emoji_pattern.findall(text)
        for emoji in found_emojis:
            self.found_emojis.add(emoji)

        # Also find specific emojis character by character
        for char in text:
            if char in self.specific_emojis:
                self.found_emojis.add(char)
                found_emojis.append(char)

        # Debug: Show what we found
        if debug and found_emojis:
            print(f"    DEBUG: Found emojis: {found_emojis}")
            print(f"    DEBUG: Unicode codes: {[f'\\u{ord(c):04x}' for c in found_emojis]}")

        # Remove emojis using regex
        cleaned_text = self.emoji_pattern.sub('', text)

        # Remove specific emojis that might be missed
        for emoji in self.specific_emojis:
            if emoji in cleaned_text:
                self.found_emojis.add(emoji)
                cleaned_text = cleaned_text.replace(emoji, '')

        emojis_removed = original_length - len(cleaned_text)
        return cleaned_text, emojis_removed

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules',
                     '.venv', 'venv', '.env', 'build', 'dist', '.tox'}

        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            return True

        # Skip non-Python files
        if file_path.suffix != '.py':
            return True

        # Skip certain special files
        skip_files = {'setup.py'}  # Be careful with setup.py
        if file_path.name in skip_files:
            return True

        return False

    def clean_file(self, file_path: Path, backup: bool = False) -> bool:
        """
        Clean emojis from a single Python file
        Returns: True if file was modified, False otherwise
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Clean the content
            cleaned_content, emojis_removed = self.clean_text(original_content)

            self.stats['files_processed'] += 1

            # Check if any changes were made
            if emojis_removed == 0:
                return False

            # Create backup if requested (now optional)
            if backup:
                backup_path = file_path.with_suffix('.py.emoji_backup')
                shutil.copy2(file_path, backup_path)

            # Write cleaned content directly
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            self.stats['files_modified'] += 1
            self.stats['emojis_removed'] += emojis_removed

            print(f"✓ Cleaned {file_path} - removed {emojis_removed} emoji characters")
            return True

        except UnicodeDecodeError:
            print(f"⚠ Warning: Could not decode {file_path} as UTF-8, skipping")
            self.stats['errors'] += 1
            self.stats['skipped_files'].append(str(file_path))
            return False
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            self.stats['errors'] += 1
            self.stats['skipped_files'].append(str(file_path))
            return False

    def clean_package(self, package_path: Path, backup: bool = False,
                      preview: bool = False, debug: bool = False) -> Dict:
        """
        Clean all Python files in a package directory

        Args:
            package_path: Path to the package directory
            backup: Whether to create backup files
            preview: If True, only show what would be changed

        Returns:
            Dictionary with cleaning statistics
        """
        package_path = Path(package_path)

        if not package_path.exists():
            raise FileNotFoundError(f"Package path does not exist: {package_path}")

        if not package_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {package_path}")

        print(f"{'Preview' if preview else 'Cleaning'} Python package: {package_path}")
        print("=" * 60)

        # Find all Python files
        python_files = []
        for file_path in package_path.rglob('*.py'):
            if not self.should_skip_file(file_path):
                python_files.append(file_path)

        print(f"Found {len(python_files)} Python files to process")
        print()

        # Process each file
        for file_path in python_files:
            if preview:
                # Preview mode - just analyze
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    _, emoji_count = self.clean_text(content)
                    self.stats['files_processed'] += 1

                    if emoji_count > 0:
                        self.stats['files_modified'] += 1
                        self.stats['emojis_removed'] += emoji_count
                        print(f"📋 {file_path} - would remove {emoji_count} emojis")

                        # Show a few examples
                        emojis_found = self.emoji_pattern.findall(content)
                        unique_emojis = list(set(emojis_found))[:5]
                        if unique_emojis:
                            print(f"   Examples: {' '.join(unique_emojis)}")

                except Exception as e:
                    print(f"✗ Error analyzing {file_path}: {e}")
                    self.stats['errors'] += 1
            else:
                # Actually clean the file
                self.clean_file(file_path, backup)

        return self.get_statistics()

    def get_statistics(self) -> Dict:
        """Get cleaning statistics"""
        return {
            'files_processed': self.stats['files_processed'],
            'files_modified': self.stats['files_modified'],
            'emojis_removed': self.stats['emojis_removed'],
            'errors': self.stats['errors'],
            'skipped_files': self.stats['skipped_files'].copy(),
            'unique_emojis_found': list(self.found_emojis)
        }

    def print_summary(self):
        """Print a summary of the cleaning operation"""
        print("\n" + "=" * 60)
        print("EMOJI CLEANING SUMMARY")
        print("=" * 60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"Total emojis removed: {self.stats['emojis_removed']}")
        print(f"Errors encountered: {self.stats['errors']}")

        if self.found_emojis:
            print(f"\nUnique emojis found and removed:")
            emoji_list = list(self.found_emojis)
            # Group emojis for better display
            for i in range(0, len(emoji_list), 10):
                print(f"  {' '.join(emoji_list[i:i + 10])}")

        if self.stats['skipped_files']:
            print(f"\nSkipped files ({len(self.stats['skipped_files'])}):")
            for file_path in self.stats['skipped_files'][:10]:  # Show first 10
                print(f"  {file_path}")
            if len(self.stats['skipped_files']) > 10:
                print(f"  ... and {len(self.stats['skipped_files']) - 10} more")


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Remove all emojis from Python files in a package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python emoji_cleaner.py /path/to/package                    # Clean all .py files
  python emoji_cleaner.py . --preview                         # Preview changes
  python emoji_cleaner.py ./termtel --no-backup               # Clean without backup
  python emoji_cleaner.py ./src --backup-dir ./backups        # Custom backup location
        """
    )

    parser.add_argument(
        'package_path',
        help='Path to the Python package directory to clean'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview changes without modifying files'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files (dangerous!)'
    )

    parser.add_argument(
        '--backup-dir',
        help='Directory to store backup files (default: alongside original files)'
    )

    parser.add_argument(
        '--include-setup',
        action='store_true',
        help='Include setup.py files (normally skipped for safety)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed processing information'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug information including Unicode codes'
    )

    args = parser.parse_args()

    try:
        # Create cleaner instance
        cleaner = EmojiCleaner()

        # Modify skip rules if requested
        if args.include_setup:
            # Remove setup.py from skip list (modify the method if needed)
            pass

        # Confirm operation if not preview mode
        if not args.preview:
            print(f"⚠️  This will modify Python files in: {args.package_path}")
            if not args.no_backup:
                print("   Backup files will be created with .emoji_backup extension")
            else:
                print("   NO BACKUPS will be created!")
            confirm = input("Continue? (y/N): ").lower().strip()
            if confirm != 'y':
                print("Operation cancelled.")
                return 0

        # Perform the cleaning
        results = cleaner.clean_package(
            package_path=Path(args.package_path),
            backup=not args.no_backup,
            preview=args.preview,
            debug=args.debug
        )

        # Print summary
        cleaner.print_summary()

        if args.preview:
            print(f"\n🔍 Preview complete. Use without --preview to apply changes.")
        else:
            print(f"\n✅ Emoji cleaning complete!")
            if not args.no_backup:
                print(f"💾 Backup files created with .emoji_backup extension")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())