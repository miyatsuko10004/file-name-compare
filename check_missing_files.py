import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set

def get_stem_map(directory: Path) -> Dict[str, List[str]]:
    """
    指定されたディレクトリ内のファイルをスキャンし、
    {stem: [filename1, filename2, ...]} の辞書を返す。
    隠しファイルは除外する。
    """
    if not directory.exists():
        print(f"エラー: ディレクトリが見つかりません: {directory}")
        return {}
    
    stem_map = {}
    processed_count = 0
    max_name_len = 0
    last_file = None

    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and not entry.name.startswith('.'):
                    stem, _ = os.path.splitext(entry.name)
                    if stem not in stem_map:
                        stem_map[stem] = []
                    stem_map[stem].append(entry.name)
                    
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
    
    return stem_map

def process_differences(base_dir: Path, diff_stems: List[str], stem_map: Dict[str, List[str]], target_desc: str, move: bool):
    """
    差分があるファイルを表示し、オプションで移動する。
    """
    if not diff_stems:
        return

    print(f"以下の {len(diff_stems)} 種類のファイル（stem）が {target_desc} に見つかりませんでした (場所: {base_dir.name}):")
    
    notfound_dir = base_dir / "notfound"
    if move:
        if not notfound_dir.exists():
            try:
                notfound_dir.mkdir(parents=True, exist_ok=True)
                print(f"ディレクトリを作成しました: {notfound_dir}")
            except OSError as e:
                print(f"ディレクトリ作成エラー: {e}")
                return

    for stem in diff_stems:
        print(f"- {stem}")
        if move:
            for filename in stem_map[stem]:
                src_file = base_dir / filename
                dst_file = notfound_dir / filename
                try:
                    shutil.move(str(src_file), str(dst_file))
                    print(f"  -> 移動しました: {filename}")
                except OSError as e:
                    print(f"  -> 移動失敗: {filename} ({e})")
    
    if move:
        print(f"\n合計 {len(diff_stems)} 件の未処理アイテムに関連するファイルを {notfound_dir} に移動しました。")
    print("-" * 30)

def main():
    parser = argparse.ArgumentParser(description="2つのディレクトリを双方向に比較し、片方にしかないファイルを特定します。拡張子は無視されます。")
    parser.add_argument("source_dir", type=str, help="ディレクトリ1（例: PDFフォルダ）")
    parser.add_argument("target_dir", type=str, help="ディレクトリ2（例: MDフォルダ）")
    parser.add_argument("--move", action="store_true", help="片方にしかないファイルをそれぞれの notfound ディレクトリに移動します")
    
    args = parser.parse_args()
    
    source_path = Path(args.source_dir)
    target_path = Path(args.target_dir)

    print(f"ディレクトリ1: {source_path.resolve()}")
    print(f"ディレクトリ2: {target_path.resolve()}")
    if args.move:
        print("モード: 差分ファイルの移動 (各ディレクトリ内の notfound フォルダへ)")
    print("-" * 30)

    source_map = get_stem_map(source_path)
    target_map = get_stem_map(target_path)

    source_stems = set(source_map.keys())
    target_stems = set(target_map.keys())

    # Sourceにのみあるファイル
    missing_in_target = sorted(list(source_stems - target_stems))
    # Targetにのみあるファイル
    missing_in_source = sorted(list(target_stems - source_stems))

    if not missing_in_target and not missing_in_source:
        print("ディレクトリの中身は一致しています（ファイル名の対応において）。")
    else:
        # Source側の処理
        process_differences(source_path, missing_in_target, source_map, f"{target_path.name}", args.move)
        
        # Target側の処理
        process_differences(target_path, missing_in_source, target_map, f"{source_path.name}", args.move)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
