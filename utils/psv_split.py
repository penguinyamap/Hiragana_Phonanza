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
    psvs = np.fromfile(psv, dtype=PackedSfenValue,count = count,offset = psvs.nbytes*i)
    #print(psvs)
    #print(psvs.nbytes/(1024**3),"GB")
    #print(len(psvs))
    bins = np.zeros(len(psvs), dtype=PackedSfenValue)
    i += 1
    bin = '{0}_{1:03d}.bin'.format(file_name,i) #ファイル名に連番を付与
    #print(i)
    if len(psvs) == 0:
        break
    else:
        #print(bin)
        bins.tofile(bin)