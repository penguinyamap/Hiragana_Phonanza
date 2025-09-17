import numpy as np
import cshogi

count = 10**2 #読み込む局面数。5億局面丸々読もうとして5億とかに設定すると、RAMを20GBほど消費するので注意。
file_name = "D:/desktop/Distilled_Datasets/Knowledge_distilled_dataset_by_Kanade_20250805upload/distilled20250805_01.bin"

confirmation = np.fromfile(file_name, dtype=PackedSfenValue,count = count)
board = cshogi.Board()
for i in range(count):
    print(confirmation[i])
    board.set_psfen(confirmation[i]['sfen'])
    print(board)