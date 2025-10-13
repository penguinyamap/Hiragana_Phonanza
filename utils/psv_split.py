#psv形式のファイルを分割するスクリプト
#print関数は挙動を確認するために残していますがコメントアウトしています。適宜コメントアウトを外して挙動を確認するとよいかも。
#format関数はpythonのバージョンによって書き方がことなるので、適宜修正してください。

from cshogi import *
import numpy as np

i = 0 #途中から再開するときに使う。初期値は0
count = 10**8 #何局面ごとに分割するか。1億局面で4GBのファイルに分割できる。

file_name = "D:/downlod/split/val" #出力するファイルのパス
psv = "D:/downlod/val-001.bin" #分割したいファイル

while True:
    if i ==0:
        psvs = np.fromfile(psv, dtype=PackedSfenValue,count = count, offset = 0)
    else:
        psvs = np.fromfile(psv, dtype=PackedSfenValue,count = count,offset = psvs.nbytes*i)
    splited_filemname = '{0}_{1:03d}.bin'.format(file_name,i)
    print(splited_filemname)
    psvs.tofile(splited_filemname)
    print(psvs)
    print(psvs.nbytes/(1024**3),"GB")
    i += 1
    if len(psvs) == 0:
        break