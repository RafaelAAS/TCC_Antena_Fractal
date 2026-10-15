# TCC - Projeto Automatizado de Antenas Fractais em Python e Ansys HFSS

Este repositório contém o desenvolvimento do Trabalho de Conclusão de Curso (TCC) focado no **desenho e simulação automatizada de antenas com geometrias fractais** utilizando scripts em Python integrados ao simulador eletromagnético **Ansys HFSS**.

O objetivo principal é explorar propriedades como o preenchimento de espaço (*space-filling*) e auto-similaridade (*self-similarity*) dos fractais para obter miniaturização e maximizar a eficiência de transferência de potência sem aumentar as dimensões físicas da antena.

---

## 📁 Estrutura do Repositório

O projeto é modularizado por **geometria fractal**, facilitando a expansão futura para outros tipos de geometrias (ex.: Koch, Minkowski, Hilbert):

```text
TCC_Antena_Fractal/
├── sierpinski/                          # Geometria do Triângulo de Sierpinski (SFMA)
│   ├── main.py                          # Script Python automatizado definitivo
│   ├── Antena_Fractal_SFMA_v2.aedt      # Projeto Ansys HFSS gerado
│   └── historico/                       # Histórico do processo iterativo de desenvolvimento
│       ├── main1.py ... main15.py       # Refinamentos da geometria, porta e casamento
│       ├── desenha_antena.py            # Testes preliminares
│       └── Antena_Fractal_SFMA.aedt     # Versões anteriores do modelo HFSS
│
├── docs/                                # Documentação e referências acadêmicas
│   └── artigos/                         # Artigos científicos base (ex.: Yu & Cai, 2015)
│
├── resultados/                          # Gráficos e dados exportados (S11, impedância Z, ganho)
│
├── requirements.txt                     # Dependências Python
└── README.md                            # Documentação principal
```

---

## 📡 Modelo Atual: SFMA (Sierpinski Fractal Monopole Antenna)

O modelo implementado em [`sierpinski/main.py`](sierpinski/main.py) baseia-se no artigo:
> **"A RFID Tag Antenna Design Based on Sierpinski Fractal Structure"**  
> *Yanzhong Yu & Zhishan Cai (IJAERS, 2015)*

### Características do Projeto:
- **Aplicação**: Tag RFID passiva operando na banda de $2.45\text{ GHz}$.
- **Substrato**: Epoxy-Kevlar ($\varepsilon_r = 3.6$, $\tan\delta = 0$, espessura $H = 1.0\text{ mm}$).
- **Dimensões do Substrato**: $24.9\text{ mm} \times 23.2\text{ mm} \times 1.0\text{ mm}$.
- **Impedância do Chip Alvo**: $Z_{chip} = (30 - j200)\,\Omega$.
- **Mecanismo de Casamento**: Laço indutivo integrado (*inductive match loop*) que fornece forte reatância indutiva ($+j200\,\Omega$) para cancelamento da capacitância parasita interna do chip RFID (casamento conjugado de potência).

### Parâmetros Geométricos (Tabela 1 do Artigo):
| Parâmetro | Descrição | Valor |
| :--- | :--- | :--- |
| $L$ | Altura do menor triângulo | $4.8\text{ mm}$ |
| $R$ | Razão $W/L$ | $0.577$ |
| $W$ | Meia-largura ($R \times L$) | $2.77\text{ mm}$ |
| $WL$ | Altura da perna esquerda do laço | $5.0\text{ mm}$ |
| $LW$ | Largura da perna esquerda do laço | $1.0\text{ mm}$ |
| $L1$ | Vão horizontal do laço | $5.2\text{ mm}$ |
| $W1$ | Espessura da barra superior do laço | $1.0\text{ mm}$ |
| $L2$ | Altura da perna direita | $5.3\text{ mm}$ |
| $W2$ | Largura da perna direita | $1.0\text{ mm}$ |
| $H_{GND}$ | Altura do plano de terra no verso | $3.0\text{ mm}$ |

---

## 🚀 Como Executar

1. Certifique-se de que o **Ansys Electronics Desktop (HFSS)** está instalado (testado com versão 2025 R2.4 / Ansys Student).
2. Execute o script principal da geometria desejada via terminal:
   ```bash
   python sierpinski/main.py
   ```
3. O script irá:
   - Gerar a geometria fractal de forma paramétrica e recursiva;
   - Desenhar o substrato, plano de terra, laço de casamento e porta lumped;
   - Configurar o solver FEM, caixa de radiação ($\ge \lambda/4$) e varredura de frequência ($1.5$ a $4.0\text{ GHz}$);
   - Criar relatórios de pós-processamento automáticos:
     - `Z_entrada`: $\text{Re}(Z)$ e $\text{Im}(Z)$;
     - `S11_chip`: Perda de retorno referenciada ao chip RFID conjugado ($30 - j200\,\Omega$);
     - `S11_50ohm`: $S_{11}$ com referência padrão de $50\,\Omega$.
   - Salvar o arquivo do projeto e disparar a execução no HFSS.

---

## 📊 Resultados Obtidos

- **$S_{11\_chip}$ Mínimo**: **$-29.96\text{ dB}$** (Artigo: $-29.60\text{ dB}$).
- **Frequência de Ressonância**: **$2.48\text{ GHz}$** (Artigo: $2.45\text{ GHz}$, desvio de apenas $1.2\%$).
- **Impedância na Ressonância**: $Z_{in} \approx (30 + j200)\,\Omega$, obtendo excelente casamento conjugado de máxima transferência de potência.