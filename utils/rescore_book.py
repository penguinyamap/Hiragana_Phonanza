#やねうら王形式の定跡を再評価するプログラム。評価値と指し手をDL系モデルで置換するときにどうぞ。
import sys
import time
import subprocess
import threading
import os
from collections import deque

# パス設定（適宜調整）
os.chdir(r"C:\Users\RYZEN\ShogiBookTools")
sys.path.append(r"C:\Users\RYZEN\ShogiBookTools\YaneBookLib")
from YaneBookLib.BookIO import *

# グローバル変数（スレッドと共有する用）
latest_score = None
latest_bestmove = None
result_ready = threading.Event()
q = deque(maxlen=2)

# USIエンジン出力を処理するスレッド関数
def output():
    global latest_score, latest_bestmove
    while True:
        line = shogi.stdout.readline()
        if line == "":
            break
        print(line, end="", flush=True)
        q.append(line)

        # 評価値を保存
        if line.startswith("info") and "score" in line:
            if "cp" in line:
                try:
                    latest_score = int(line.split("score cp")[1].split()[0])
                except:
                    pass
            elif "mate" in line:
                try:
                    latest_score = "mate " + line.split("score mate")[1].split()[0]
                except:
                    pass

        # bestmove 行が来たら通知
        elif line.startswith("bestmove"):
            try:
                latest_bestmove = line.split()[1]
            except:
                latest_bestmove = None
            result_ready.set()

# USIコマンドを送る関数
def usi(command):
    shogi.stdin.write(command + "\n")
    shogi.stdin.flush()

# USIエンジンを起動
shogi = subprocess.Popen(
    r"C:\Users\RYZEN\ShogiBookTools\YaneuraOu_NNUE_halfkp_512x2_8_64-V860DEV_ZEN2.exe",
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    encoding="UTF-8"
)

# エンジン出力スレッド起動
t = threading.Thread(target=output, daemon=True)
t.start()

# 初期化コマンド送信
usi("usi")
time.sleep(1)
usi("isready")
time.sleep(1)
usi("usinewgame")
time.sleep(1)

# 定跡ファイル読み込み
with StandardBookReader(r"C:\Users\RYZEN\Desktop\ShogiEngines\NNUE\Suisho10\book\petabook.db") as reader:
    for i, book_node in enumerate(reader):
        sfen = str(book_node[0])

        # 準備
        usi("position sfen " + sfen)
        result_ready.clear()

        # 探索
        usi("go nodes 10000000")
        result_ready.wait(timeout=10)  # bestmove が出るまで待つ（最大10秒）

        # 出力結果表示
        print(f"評価値: {latest_score}, bestmove: {latest_bestmove}")

        if i >= 4:
            break  # 最初の5局面で終了（必要に応じて変更）

# 終了処理
usi("quit")
shogi.wait()
