import argparse
import os
from pathlib import Path
from typing import Set

def get_stem_set(directory: Path) -> Set[str]:
    """
    指定されたディレクトリ内のファイルの拡張子を除いた名前(stem)のセットを返す。
    隠しファイルは除外する。
    """
    if not directory.exists():
        print(f"エラー: ディレクトリが見つかりません: {directory}")
        return set()
    
    stems = set()
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and not entry.name.startswith('.'):
                    stem, _ = os.path.splitext(entry.name)
                    stems.add(stem)
    except OSError as e:
        print(f"警告: ディレクトリへのアクセス中にエラーが発生しました（一部のファイルが読み込めない可能性があります）: {directory}\n詳細: {e}")
    
    return stems

def main():
    parser = argparse.ArgumentParser(description="2つのディレクトリを比較し、変換されていないファイル（sourceにあってtargetにないファイル）を特定します。拡張子は無視されます。")
    parser.add_argument("source_dir", type=str, help="比較元ディレクトリ（例: PDFフォルダ）")
    parser.add_argument("target_dir", type=str, help="比較先ディレクトリ（例: MDフォルダ）")
    
    args = parser.parse_args()
    
    source_path = Path(args.source_dir)
    target_path = Path(args.target_dir)

    print(f"比較元: {source_path.resolve()}")
    print(f"比較先: {target_path.resolve()}")
    print("-" * 30)

    source_stems = get_stem_set(source_path)
    target_stems = get_stem_set(target_path)

    missing_stems = sorted(list(source_stems - target_stems))

    if missing_stems:
        print(f"以下の {len(missing_stems)} ファイルが {args.target_dir} に見つかりませんでした:")
        for stem in missing_stems:
            print(f"- {stem}")
    else:
        print("すべてのファイルが変換されています（欠落はありません）。")

if __name__ == "__main__":
    main()
