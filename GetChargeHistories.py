import numpy as np

def GetChargeHistories(MFP, initialQ, length, N=10000, random_state=None, histories=None, ignored=False):
    """
    平均自由行程からモンテカルロ法による電荷変化履歴を得る
    lengthは、MFPと同じ単位を与える。MFPの単位がcmならlengthもcmで
    ignored が Trueのときは、電荷変化履歴は計算するが長さは変えない
    initialQ は 初期電荷か、電荷リストを与える
    random_state は以下のようにrsを生成して使い回す
    rs = np.random.RandomState(1)
    """
    assert random_state is not None  # 乱数発生器の指定を確認
    rs = random_state

    zp = int(list(MFP.keys())[0].split("-")[0])  # 初期電荷を取得

    if histories == None:
        histories = [[] for _ in range(N)]
        if type(initialQ) is list:
            initialQs = np.array(initialQ, dtype=np.int32)
        else:
            initialQs = np.full(N, initialQ, dtype=np.int32)
        offset_length = 0
    else:
        assert len(histories) == N
        initialQs = np.array([histories[n][-1][0] for n in range(N)], dtype=np.int32)
        offset_length = histories[0][-1][1]

    length = length + offset_length  # シミュレーションの終点を設定

    # MFP のキャッシュ (辞書参照回数を削減)
    mfp_cache = {key: MFP[key] for key in MFP}
    Qmax = max([int(key.split("->")[0]) for key in MFP])
    Qmin = min([int(key.split("->")[0]) for key in MFP])
    mfp_cache[f"{Qmax}->{Qmax+1}"] = float("inf")
    mfp_cache[f"{Qmin}->{Qmin-1}"] = float("inf")

    for n in range(N):
        Q = initialQs[n]
        current_length = offset_length

        history = [[Q, offset_length, "pre", zp]]  # 最初にだけzpを入れる
        while True:
            Qp, Qm = Q + 1, Q - 1

            lp = rs.exponential(mfp_cache[f"{Q}->{Qp}"])
            lm = rs.exponential(mfp_cache[f"{Q}->{Qm}"])

            if current_length + lp > length and current_length + lm > length:
                history.append([Q, length, "post"])
                break
            elif lp > lm:
                current_length += lm
                Q = Qm
                history.append([Q, current_length, "-"])
            else:
                current_length += lp
                Q = Qp
                history.append([Q, current_length, "+"])
        if ignored:
            # 計算した最後のQを距離0で追加する
            if len(histories[n]) > 0:
                history[-1][1] = histories[n][-1][1]
            else:
                history[-1][1] = 0
            history[-1][2] = "ignored"
            histories[n] += [history[0], history[-1]]
        else:
            histories[n] += history
    return histories


if __name__ == '__main__':
    MFP = {}
    MFP["1->2"] = 1.0
    MFP["2->1"] = 1.0
    MFP["2->3"] = 2.0
    MFP["3->2"] = 2.0

    GetChargeHistories(MFP, 1, 1000, 10000, np.random.RandomState(1))
