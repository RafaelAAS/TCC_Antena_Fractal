"""Gera as figuras do Capitulo 2 do TCC: Curva de Koch, Curva de Hilbert e Triangulo de Sierpinski.

As figuras sao desenhadas por codigo, no tamanho em que entram no texto (fontes de 9 pt),
de modo que a legenda possa dizer "Fonte: Elaborada pelo autor." sem depender de imagens de
origem desconhecida.

Saidas (pasta images/, 300 dpi, fundo branco):
  fractal_koch.png        Curva de Koch, n = 0 a 4, com o comprimento da curva em cada passo
  fractal_hilbert.png     Curva de Hilbert, n = 1 a 6
  fractal_sierpinski.png  Triangulo de Sierpinski, n = 0 a 4

Uso:  python resultados/gerar_figuras_fractais.py
"""
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

SAIDA = Path(__file__).resolve().parent.parent / "images"
DPI = 300

TINTA = "#0b0b0b"
TINTA_SEC = "#52514e"
AZUL_PETROLEO = "#0e4d64"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "font.size": 9,
})


def salvar(fig, nome):
    caminho = SAIDA / nome
    SAIDA.mkdir(exist_ok=True)
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    print(f"Figura salva em: {caminho}")


# ---- Curva de Koch ---------------------------------------------------------------------
def curva_koch(n):
    """Pontos (numeros complexos) da curva de Koch de ordem n sobre o segmento [0, 1]."""
    pontos = [0j, 1 + 0j]
    giro = complex(math.cos(math.pi / 3), math.sin(math.pi / 3))  # rotacao de +60 graus
    for _ in range(n):
        novos = []
        for a, b in zip(pontos, pontos[1:]):
            d = (b - a) / 3
            p1, p3 = a + d, a + 2 * d
            p2 = p1 + d * giro
            novos += [a, p1, p2, p3]
        novos.append(pontos[-1])
        pontos = novos
    return pontos


def figura_koch():
    fig, ax = plt.subplots(figsize=(3.3, 4.0))
    passo = 0.40  # distancia vertical entre uma curva e a seguinte
    comprimentos = ["L", "4L/3", "16L/9", "64L/27", "256L/81"]  # (4/3)^n * L
    for n in range(5):
        pts = curva_koch(n)
        y0 = -n * passo
        ax.plot([p.real for p in pts], [p.imag + y0 for p in pts],
                color=TINTA, linewidth=1.0 - 0.12 * n, solid_joinstyle="round")
        ax.text(-0.05, y0 + 0.03, f"n = {n}", ha="right", va="center", color=TINTA)
        ax.text(1.05, y0 + 0.03, comprimentos[n], ha="left", va="center",
                color=TINTA_SEC, fontsize=8.5)
    ax.text(1.05, 0.20, "comprimento", ha="left", va="bottom", color=TINTA_SEC, fontsize=8)
    ax.set_xlim(-0.27, 1.35)
    ax.set_ylim(-4 * passo - 0.05, 0.32)
    ax.set_aspect("equal")
    ax.axis("off")
    salvar(fig, "fractal_koch.png")


# ---- Curva de Hilbert ------------------------------------------------------------------
def pontos_hilbert(ordem):
    """Centros das celulas percorridas pela curva de Hilbert de ordem 'ordem', em [0, 1]^2."""
    n = 2 ** ordem
    pts = []
    for d in range(n * n):
        x = y = 0
        t = d
        s = 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1:
                    x, y = s - 1 - x, s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        pts.append(((x + 0.5) / n, (y + 0.5) / n))
    return pts


def figura_hilbert():
    fig, eixos = plt.subplots(2, 3, figsize=(4.1, 3.05))
    larguras = [1.5, 1.2, 0.9, 0.65, 0.45, 0.3]
    for ordem, ax in enumerate(eixos.flat, start=1):
        xs, ys = zip(*pontos_hilbert(ordem))
        ax.plot(xs, ys, color=TINTA, linewidth=larguras[ordem - 1], solid_joinstyle="miter")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for lado in ax.spines.values():
            lado.set_linewidth(0.7)
            lado.set_color(TINTA)
        ax.set_xlabel(f"n = {ordem}", color=TINTA, labelpad=3)
    fig.subplots_adjust(wspace=0.10, hspace=0.35)
    salvar(fig, "fractal_hilbert.png")


# ---- Triangulo de Sierpinski -----------------------------------------------------------
def triangulos_sierpinski(v1, v2, v3, n):
    """Triangulos solidos que restam apos n subtracoes do triangulo central."""
    if n == 0:
        return [(v1, v2, v3)]
    m12 = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2)
    m23 = ((v2[0] + v3[0]) / 2, (v2[1] + v3[1]) / 2)
    m31 = ((v3[0] + v1[0]) / 2, (v3[1] + v1[1]) / 2)
    return (triangulos_sierpinski(v1, m12, m31, n - 1)
            + triangulos_sierpinski(m12, v2, m23, n - 1)
            + triangulos_sierpinski(m31, m23, v3, n - 1))


def figura_sierpinski():
    h = math.sqrt(3) / 2
    espaco = 1.35
    fig, ax = plt.subplots(figsize=(6.0, 1.55))
    for n in range(5):
        x0 = n * espaco
        tris = triangulos_sierpinski((x0, 0), (x0 + 1, 0), (x0 + 0.5, h), n)
        ax.add_collection(PolyCollection(tris, facecolors=AZUL_PETROLEO, edgecolors="none"))
        ax.text(x0 + 0.5, -0.10, f"n = {n}", ha="center", va="top", color=TINTA)
    ax.set_xlim(-0.05, 4 * espaco + 1.05)
    ax.set_ylim(-0.34, h + 0.04)
    ax.set_aspect("equal")
    ax.axis("off")
    salvar(fig, "fractal_sierpinski.png")


if __name__ == "__main__":
    figura_koch()
    figura_hilbert()
    figura_sierpinski()
