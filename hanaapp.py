import streamlit as st
import numpy as np
import pandas as pd

st.title("🎰 スロット差枚＆設定推測ツール")

# =========================
# 🎯 台選択
# =========================
machine = st.selectbox(
    "機種を選択",
    ["キングハナハナ", "ハナハナ鳳凰", "ニューキングハナハナ"]
)

# =========================
# 設定＆係数
# =========================
if machine == "キングハナハナ":
    settings = {
        1: {"big": 292, "reg": 489, "machine": -0.0289},
        2: {"big": 280, "reg": 452, "machine": -0.0092},
        3: {"big": 268, "reg": 420, "machine": 0.0114},
        4: {"big": 257, "reg": 390, "machine": 0.0444},
        5: {"big": 244, "reg": 360, "machine": 0.0754},
        6: {"big": 232, "reg": 332, "machine": 0.1053},
    }
    BIG_COEF = 260
    REG_COEF = 120

elif machine == "ハナハナ鳳凰":
    settings = {
        1: {"big": 297, "reg": 496, "machine": -0.037},
        2: {"big": 284, "reg": 458, "machine": -0.018},
        3: {"big": 273, "reg": 425, "machine": 0.003},
        4: {"big": 264, "reg": 390, "machine": 0.023},
        5: {"big": 256, "reg": 364, "machine": 0.051},
        6: {"big": 242, "reg": 334, "machine": 0.077},
    }
    BIG_COEF = 240
    REG_COEF = 120

elif machine == "ニューキングハナハナ":
    settings = {
        1: {"big": 299, "reg": 496, "machine": -0.03},
        2: {"big": 291, "reg": 471, "machine": -0.01},
        3: {"big": 281, "reg": 442, "machine": 0.01},
        4: {"big": 268, "reg": 406, "machine": 0.04},
        5: {"big": 253, "reg": 372, "machine": 0.08},
        
    }
    BIG_COEF = 312
    REG_COEF = 130

# =========================
# 入力
# =========================
n = st.number_input("台数", min_value=1, max_value=10, value=1)

big_list, reg_list, games_list, diff_list = [], [], [], []

for i in range(n):
    st.markdown(f"### 台{i+1}")
    col1, col2 = st.columns(2)

    with col1:
        big = st.number_input(f"BIG_{i}", min_value=0, key=f"big{i}")
        reg = st.number_input(f"REG_{i}", min_value=0, key=f"reg{i}")

    with col2:
        games = st.number_input(f"回転数_{i}", min_value=0, key=f"games{i}")
        diff = st.number_input(f"差枚_{i}", value=0, key=f"diff{i}")

    big_list.append(big)
    reg_list.append(reg)
    games_list.append(games)
    diff_list.append(diff)

# =========================
# 計算
# =========================
if st.button("計算する"):

    results = []

    for i in range(n):

        big = big_list[i]
        reg = reg_list[i]
        games = games_list[i]
        diff = diff_list[i]

        # 確率
        big_prob = games / big if big > 0 else 0
        reg_prob = games / reg if reg > 0 else 0
        bonus_prob = games / (big + reg) if (big + reg) > 0 else 0

        scores = []

        for s in settings.keys():

            p = settings[s]

            # 理論ボーナス回数
            a = games / p["big"]
            b = games / p["reg"]

            # 機械割差枚
            c = games * 3 * p["machine"]

            # ボーナス差分
            d = (big - a) * BIG_COEF
            e = (reg - b) * REG_COEF

            # ★ 正しい定義
            actual_diff = e + d
            
            estimated_diff = diff - e - d
            theoretical_diff = estimated_diff - c
            

            scores.append(abs(theoretical_diff))

            row = {
                "台": f"台{i+1}",
                "設定": s,
                "BIG確率": f"1/{big_prob:.1f}" if big > 0 else "-",
                "REG確率": f"1/{reg_prob:.1f}" if reg > 0 else "-",
                "合算": f"1/{bonus_prob:.1f}" if (big + reg) > 0 else "-",
                "実稼働差異": int(actual_diff),
                "理論値差異": int(theoretical_diff),
                "推定値差枚": int(estimated_diff)
            }

            results.append(row)

        # =========================
        # 🧠 信頼度
        # =========================
        inv_scores = [1/(s+1) for s in scores]
        total = sum(inv_scores)
        probs = [v/total*100 for v in inv_scores]

        st.subheader(f"🎰 台{i+1} 設定信頼度")

        prob_df = pd.DataFrame({
            "設定": list(settings.keys()),
            "信頼度(%)": [round(p,1) for p in probs]
        })

        st.dataframe(prob_df)

        best = prob_df.iloc[prob_df["信頼度(%)"].idxmax()]
        st.success(f"👉 設定{int(best['設定'])} が最も有力 ({best['信頼度(%)']}%)")

    df = pd.DataFrame(results)

    # 色付け
    def color(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return "color: green"
            elif val < 0:
                return "color: red"
        return ""

    st.subheader("📊 詳細データ")
    st.dataframe(df.style.applymap(color, subset=["実稼働差異", "理論値差異", "推定値差枚"]))