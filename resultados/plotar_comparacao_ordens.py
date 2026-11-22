"""Compara o S11_chip das ordens fractais 0, 1 e 2 da SFMA.

Le os CSVs exportados do HFSS (S11_chip_ordem{0,1,2}.csv, nesta pasta), gera a
figura images/S11_chip_ordens.png e imprime as metricas usadas na Tabela 4.x
do TCC (minimo, valor em 2,45 GHz, banda de -10 dB e segundo vale).

Uso:  python resultados/plotar_comparacao_ordens.py
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA.parent / "images" / "S11_chip_ordens.png"

F_ALVO = 2.45  # GHz
LIMITE_DB = -10.0

# Cores categoricas fixas por ordem (paleta validada, slots 1 a 3)
ORDENS = [
    (0, "Ordem 0 (triângulo cheio)", "#2a78d6"),
    (1, "Ordem 1", "#eb6834"),
    (2, "Ordem 2", "#1baf7a"),
]

TINTA = "#0b0b0b"
TINTA_SEC = "#52514e"
TINTA_MUDA = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def ler(ordem):
    with open(PASTA / f"S11_chip_ordem{ordem}.csv", encoding="utf-8") as f:
        linhas = list(csv.reader(f))[1:]
    return [float(a) for a, _ in linhas], [float(b) for _, b in linhas]


def metricas(f, s):
    i = min(range(len(s)), key=lambda k: s[k])
    inf = sup = None
    for k in range(i, 0, -1):
        if s[k - 1] > LIMITE_DB >= s[k]:
            inf = f[k - 1] + (f[k] - f[k - 1]) * (LIMITE_DB - s[k - 1]) / (s[k] - s[k - 1])
            break
    for k in range(i, len(s) - 1):
        if s[k] <= LIMITE_DB < s[k + 1]:
            sup = f[k] + (f[k + 1] - f[k]) * (LIMITE_DB - s[k]) / (s[k + 1] - s[k])
            break
    j = min((k for k in range(len(f)) if f[k] > 3.0), key=lambda k: s[k])
    return {
        "f_min": f[i], "s_min": s[i],
        "s_245": s[min(range(len(f)), key=lambda k: abs(f[k] - F_ALVO))],
        "inf": inf, "sup": sup, "bw_mhz": (sup - inf) * 1000,
        "f_2v": f[j], "s_2v": s[j],
    }


def virgula(v, _pos=None, casas=1):
    return f"{v:.{casas}f}".replace("-", "−").replace(".", ",")


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "font.size": 9,
    "axes.edgecolor": EIXO,
    "axes.labelcolor": TINTA,
    "xtick.color": TINTA_SEC,
    "ytick.color": TINTA_SEC,
})

dados = {n: ler(n) for n, _, _ in ORDENS}

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(7.4, 3.4), sharey=True,
    gridspec_kw={"width_ratios": [1.25, 1]}, layout="constrained",
)

for ax in (ax1, ax2):
    ax.set_facecolor("#ffffff")
    ax.grid(True, color=GRADE, linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=3, width=0.6)

for n, rotulo, cor in ORDENS:
    f, s = dados[n]
    ax1.plot(f, s, color=cor, linewidth=1.8, label=rotulo, solid_capstyle="round")
    ax2.plot(f, s, color=cor, linewidth=1.8, solid_capstyle="round")
    m = metricas(f, s)
    ax2.plot(m["f_min"], m["s_min"], "o", color=cor, markersize=6,
             markeredgecolor="#ffffff", markeredgewidth=1.5, zorder=5)

# Painel (a): faixa completa; destaca a janela ampliada em (b)
ax1.set_xlim(1.5, 4.0)
ax1.set_ylim(-32, 0)
ax1.axvspan(2.35, 2.60, color=TINTA_MUDA, alpha=0.12, linewidth=0)
ax1.axvline(F_ALVO, color=TINTA_MUDA, linewidth=0.8, linestyle=":")
ax1.set_xlabel("Frequência (GHz)")
ax1.set_ylabel(r"$S_{11}^{\mathrm{chip}}$ (dB)")
ax1.set_title("(a) Faixa simulada", loc="left", fontsize=9, color=TINTA)
ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, p: virgula(v, p, 1)))
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, p: virgula(v, p, 0)))

# Painel (b): regiao de ressonancia
ax2.set_xlim(2.35, 2.60)
ax2.axhline(LIMITE_DB, color=TINTA_MUDA, linewidth=0.9, linestyle="--")
ax2.axvline(F_ALVO, color=TINTA_MUDA, linewidth=0.8, linestyle=":")
ax2.text(2.352, LIMITE_DB + 0.6, "−10 dB", color=TINTA_SEC, fontsize=8, va="bottom")
ax2.text(F_ALVO + 0.003, -1.2, "2,45 GHz", color=TINTA_SEC, fontsize=8, va="top")
ax2.set_xlabel("Frequência (GHz)")
ax2.set_title("(b) Região de ressonância", loc="left", fontsize=9, color=TINTA)
ax2.set_xticks([2.40, 2.45, 2.50, 2.55, 2.60])  # sem 2,35, que encostaria no "4,0" do painel (a)
ax2.xaxis.set_major_formatter(FuncFormatter(lambda v, p: virgula(v, p, 2)))
ax2.tick_params(labelleft=False)

fig.legend(*ax1.get_legend_handles_labels(), loc="outside upper center", ncol=3,
           frameon=False, fontsize=9, handlelength=1.8, labelcolor=TINTA)

SAIDA.parent.mkdir(exist_ok=True)
fig.savefig(SAIDA, dpi=300, facecolor="#ffffff")
print(f"Figura salva em: {SAIDA}\n")

print(f"{'ordem':>5} {'f_min':>6} {'S11_min':>8} {'S11@2,45':>9} {'banda -10 dB (GHz)':>22} {'BW (MHz)':>9} {'BW (%)':>7} {'2o vale':>16}")
for n, _, _ in ORDENS:
    m = metricas(*dados[n])
    fc = (m["inf"] + m["sup"]) / 2
    print(f"{n:>5} {m['f_min']:>6.2f} {m['s_min']:>8.2f} {m['s_245']:>9.2f} "
          f"{m['inf']:>10.4f} a {m['sup']:<8.4f} {m['bw_mhz']:>9.1f} {m['bw_mhz'] / 1000 / fc * 100:>7.2f} "
          f"{m['s_2v']:>7.2f} @ {m['f_2v']:.2f}")
