"""Compara o S11_chip das duas posicoes da barra superior do laco da SFMA.

Le os CSVs exportados do HFSS (S11_chip_barra_Y4_0.csv e S11_chip_barra_Y4_3.csv, nesta
pasta), gera a figura images/S11_chip_barra.png e imprime as metricas usadas na Tabela 4.x
do TCC (minimo, valor em 2,40 e 2,45 GHz, banda de -10 dB e segundo vale). Se existirem
Z_entrada_ordem2.csv e Z_entrada_barra_Y4_3.csv, imprime tambem a impedancia de entrada.

Os dois designs vem do main_barra.py:
  Barra_Y4_0 : barra em Y = 4,0 a 5,0 mm (igual ao main.py, referencia do TCC)
  Barra_Y4_3 : barra em Y = 4,3 a 5,3 mm (alinhada ao topo da perna direita)

Uso:  python resultados/plotar_comparacao_barra.py
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).resolve().parent
SAIDA = PASTA.parent / "images" / "S11_chip_barra.png"

F_ALVO = 2.45  # GHz
LIMITE_DB = -10.0
BANDA_YU_CAI = (2.41, 2.50)  # GHz, S11 <= -10 dB (Yu e Cai, 2015)

# Mesma cor da ordem 2 em S11_chip_ordens.png (Barra_Y4_0 e a antena do main.py = ordem 2).
# A segunda curva usa a cor violeta da paleta validada (slot 7).
DESIGNS = [
    ("Y4_0", "Barra em 4,0 a 5,0 mm (antena principal)", "#1baf7a"),
    ("Y4_3", "Barra em 4,3 a 5,3 mm (alinhada ao topo da perna direita)", "#6250d6"),
]

TINTA = "#0b0b0b"
TINTA_SEC = "#52514e"
TINTA_MUDA = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def ler(nome):
    with open(PASTA / f"S11_chip_barra_{nome}.csv", encoding="utf-8") as f:
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

    def em(freq):
        return s[min(range(len(f)), key=lambda k: abs(f[k] - freq))]

    return {
        "f_min": f[i], "s_min": s[i], "s_240": em(2.40), "s_245": em(F_ALVO),
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

dados = {n: ler(n) for n, _, _ in DESIGNS}

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

for n, rotulo, cor in DESIGNS:
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

# Painel (b): regiao de ressonancia, com a banda de -10 dB reportada por Yu e Cai
ax2.set_xlim(2.35, 2.60)
ax2.axvspan(*BANDA_YU_CAI, color=TINTA_MUDA, alpha=0.15, linewidth=0)
ax2.axhline(LIMITE_DB, color=TINTA_MUDA, linewidth=0.9, linestyle="--")
ax2.axvline(F_ALVO, color=TINTA_MUDA, linewidth=0.8, linestyle=":")
ax2.text(2.598, LIMITE_DB - 0.6, "−10 dB", color=TINTA_SEC, fontsize=8, ha="right", va="top")
ax2.text(F_ALVO + 0.003, -1.2, "2,45 GHz", color=TINTA_SEC, fontsize=8, va="top")
ax2.text(BANDA_YU_CAI[0] + 0.003, -31.5, "faixa de\nYu e Cai", color=TINTA_SEC, fontsize=7.5,
         ha="left", va="bottom", linespacing=1.1)
ax2.set_xlabel("Frequência (GHz)")
ax2.set_title("(b) Região de ressonância", loc="left", fontsize=9, color=TINTA)
ax2.set_xticks([2.40, 2.45, 2.50, 2.55, 2.60])  # sem 2,35, que encostaria no "4,0" do painel (a)
ax2.xaxis.set_major_formatter(FuncFormatter(lambda v, p: virgula(v, p, 2)))
ax2.tick_params(labelleft=False)

fig.legend(*ax1.get_legend_handles_labels(), loc="outside upper center", ncol=1,
           frameon=False, fontsize=8.5, handlelength=1.8, labelcolor=TINTA)

SAIDA.parent.mkdir(exist_ok=True)
fig.savefig(SAIDA, dpi=300, facecolor="#ffffff")
print(f"Figura salva em: {SAIDA}\n")

print(f"{'barra':>5} {'f_min':>6} {'S11_min':>8} {'S11@2,40':>9} {'S11@2,45':>9} "
      f"{'banda -10 dB (GHz)':>22} {'BW (MHz)':>9} {'BW (%)':>7} {'2o vale':>16}")
for n, _, _ in DESIGNS:
    m = metricas(*dados[n])
    fc = (m["inf"] + m["sup"]) / 2
    print(f"{n:>5} {m['f_min']:>6.2f} {m['s_min']:>8.2f} {m['s_240']:>9.2f} {m['s_245']:>9.2f} "
          f"{m['inf']:>10.4f} a {m['sup']:<8.4f} {m['bw_mhz']:>9.1f} {m['bw_mhz'] / 1000 / fc * 100:>7.2f} "
          f"{m['s_2v']:>7.2f} @ {m['f_2v']:.2f}")


# ---- Impedancia de entrada (opcional): ordem 2 = Barra_Y4_0 e Barra_Y4_3 ----------------
def ler_z(arquivo):
    with open(PASTA / arquivo, encoding="utf-8") as f:
        linhas = list(csv.reader(f))[1:]
    return [(float(a), float(b), float(c)) for a, b, c in linhas]


def cruzamento(z, coluna, alvo):
    """primeira frequencia (interpolada) em que a coluna (1 = R, 2 = X) passa por 'alvo'"""
    for k in range(1, len(z)):
        a, b = z[k - 1][coluna], z[k][coluna]
        if a < alvo <= b:
            return z[k - 1][0] + (z[k][0] - z[k - 1][0]) * (alvo - a) / (b - a)
    return None


arquivos_z = {"Y4_0": "Z_entrada_ordem2.csv", "Y4_3": "Z_entrada_barra_Y4_3.csv"}
if all((PASTA / a).exists() for a in arquivos_z.values()):
    print("\nImpedância de entrada (Y4_0 = Z_entrada_ordem2.csv):")
    for n, arq in arquivos_z.items():
        z = ler_z(arq)
        linha = []
        for freq in (2.40, 2.45, 2.48):
            p = min(z, key=lambda t: abs(t[0] - freq))
            linha.append(f"{freq:.2f} GHz: {p[1]:.2f}{p[2]:+.2f}j")
        print(f"  {n}: " + " | ".join(linha)
              + f" | R=30 em {cruzamento(z, 1, 30.0):.4f} GHz | X=200 em {cruzamento(z, 2, 200.0):.4f} GHz")
