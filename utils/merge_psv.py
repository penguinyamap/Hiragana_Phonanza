import glob
import re
import subprocess
import os

# 元フォルダ
base_dir = "D:/desktop/Distilled_Datasets/新しいフォルダー"

# 元ファイル一覧を取得
files = glob.glob(os.path.join(base_dir, "distilled20250805_*.bin"))

# ファイル名の番号を抽出して辞書化
file_dict = {}
for f in files:
    m = re.search(r"distilled20250805_(\d+)\.bin$", f)
    if m:
        num = int(m.group(1))
        file_dict[num] = f

# ソート済み番号リスト
numbers = sorted(file_dict.keys())

# 範囲ごとにまとめる
step = 49  # 1グループの幅（000～049, 050～099 ...）
chunk_size = 10**9

for start in range(0, max(numbers) + 1, step + 1):
    end = start + step
    group_nums = [n for n in numbers if start <= n <= end]
    if not group_nums:
        continue

    # 対象ファイル
    group_files = [file_dict[n] for n in group_nums]

    # 出力ファイル名（同じフォルダに保存）
    output_file = os.path.join(
        base_dir,
        f"distilled20250805_{start:03d}to{end:03d}.bin"
    )

    # コマンド作成
    cmd = f'python "C:/Users/RYZEN/psv-utils/concat.py" --chunk-size {chunk_size} ' + \
          ' '.join(f'"{f}"' for f in group_files) + \
          f' "{output_file}"'

    print("実行:", cmd)
    subprocess.run(cmd, shell=True, check=True)
