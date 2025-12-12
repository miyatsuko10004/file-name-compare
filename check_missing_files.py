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
    processed_count = 0
    max_name_len = 0
    last_file = None

    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and not entry.name.startswith('.'):
                    stem, _ = os.path.splitext(entry.name)
                    stems.add(stem)
                    processed_count += 1
                    max_name_len = max(max_name_len, len(entry.name))
                    last_file = entry.name
    except OSError as e:
        dir_path_len = len(str(directory.resolve()))
        print(f"\n[ERROR] ディレクトリスキャン中にエラーが発生しました: {directory}")
        print(f"詳細: {e}")
        print(f"- 処理できたファイル数: {processed_count}")
        print(f"- ディレクトリパス長: {dir_path_len} 文字")
        print(f"- 検出した最大ファイル名長: {max_name_len} 文字")
        if last_file:
            print(f"- 最後に処理したファイル: {last_file}")
            print(f"- 直近の推定合計パス長: {dir_path_len + len(last_file) + 1} 文字")
        
        if dir_path_len + max_name_len > 250:
            print("\n【ヒント】パスの長さが Windows の制限 (MAX_PATH: 260文字) に近づいているか、超えている可能性があります。")
            print("パスを短くするか、ディレクトリ階層を浅くすることを検討してください。")
        print("-" * 30)
    
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
