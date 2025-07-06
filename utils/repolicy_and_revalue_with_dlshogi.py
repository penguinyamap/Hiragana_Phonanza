#psv形式の棋譜の指し手と評価値をDL系モデルで置換するコード
import numpy as np
from cshogi import *
from cshogi.dlshogi import make_input_features, make_move_label, FEATURES1_NUM, FEATURES2_NUM
import onnxruntime
import time

model_path = "C:/Users/RYZEN/Desktop/ShogiEngines/DL/Kanade_TSEC6/eval/model.onnx"
device_id = 0
enable_cuda = True
enable_tensorrt = True

batch_size = 1536
chunk_size = 10**7
max_chunks = 800

input_features = [
    np.empty((batch_size, FEATURES1_NUM, 9, 9), dtype=np.float32),
    np.empty((batch_size, FEATURES2_NUM, 9, 9), dtype=np.float32),
]

# 推論セッションの準備
available_providers = onnxruntime.get_available_providers()
enable_providers = []
if enable_tensorrt and 'TensorrtExecutionProvider' in available_providers:
    enable_providers.append(('TensorrtExecutionProvider', {
        'device_id': device_id,
        'trt_fp16_enable': True,
        'trt_engine_cache_enable': True,
    }))
    print("Enable TensorrtExecutionProvider")
if enable_cuda and 'CUDAExecutionProvider' in available_providers:
    enable_providers.append(('CUDAExecutionProvider', {
        'device_id': device_id,
    }))
    print("Enable CUDAExecutionProvider")
if 'CPUExecutionProvider' in available_providers:
    enable_providers.append('CPUExecutionProvider')
    print("Enable CPUExecutionProvider")

session = onnxruntime.InferenceSession(model_path, providers=enable_providers)

# 勝率を評価値に変換
def value_to_eval(value):
    if value == 1.0:
        return 32000
    elif value == 0.0:
        return -32000
    else:
        return int(-285 * np.log(1 / value - 1))

board = Board()

a = 0
while a < max_chunks:
    print(f"Chunk {a} 開始")
    offset_bytes = chunk_size * a * 40
    psvs = np.fromfile(
        "D:/desktop/Distilled_Datasets/Origine/shogi_suisho5_depth9/shuffled/shuffled.bin",
        count=chunk_size, offset=offset_bytes, dtype=PackedSfenValue)

    scores = []
    bestmoves = []

    j = 0
    start = time.time()
    for i in range(chunk_size):
        board.set_psfen(psvs[i]['sfen'])
        make_input_features(board, input_features[0][j], input_features[1][j])

        if j == batch_size - 1:
            io_binding = session.io_binding()
            io_binding.bind_cpu_input("input1", input_features[0][:j + 1])
            io_binding.bind_cpu_input("input2", input_features[1][:j + 1])
            io_binding.bind_output("output_policy")
            io_binding.bind_output("output_value")
            session.run_with_iobinding(io_binding)
            outputs = io_binding.copy_outputs_to_cpu()
            logits_all = outputs[0]  # shape: (batch_size, 2187)
            values = outputs[1].reshape(-1)

            for k in range(batch_size):
                board.set_psfen(psvs[i - j + k]['sfen'])
                legal_moves = list(board.legal_moves)
                if not legal_moves:
                    bestmoves.append("")  # 合法手なし
                    scores.append(values[k])
                    continue

                logit = logits_all[k]
                best_score = -float('inf')
                best_move = None
                for move in legal_moves:
                    label = make_move_label(move, board.turn)
                    if logit[label] > best_score:
                        best_score = logit[label]
                        best_move = move

                bestmoves.append(move_to_usi(best_move))
                scores.append(values[k])

            j = 0
        else:
            j += 1

        if (i + 1) % 1000000 == 0:
            print(f"{i + 1}局面処理済み")
            end = time.time()
            print(f"バッチサイズ{batch_size}で{chunk_size}局面を処理するのにかかった時間: {end - start:.2f}秒")
            start = time.time()

    print("評価値とポリシーをPSVに書き込み中...")
    for psv, score, bestmove in zip(psvs, scores, bestmoves):
        psv["score"] = value_to_eval(score)
        board.set_psfen(psv["sfen"])
        if bestmove == "":
            psv["move"] = 0
        else:
            try:
                move_index = board.move_from_usi(bestmove)
                psv["move"] = move16(move_index)
            except Exception as e:
                print(f"⚠️ move_from_usi 失敗: {e}, sfen={psv['sfen']}, bestmove={bestmove}")
                psv["move"] = 0  # fallback

    output_path = f"D:/desktop/Distilled_Datasets/Kanade_TSEC6/shogi_suisho5_depth9/shuffled{a}.bin"
    psvs.tofile(output_path)
    print(f"{output_path} 作成完了")
    a += 1
