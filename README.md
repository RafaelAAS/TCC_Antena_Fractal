# Projeto Automatizado de Antenas Fractais em Python e Ansys HFSS

Este repositório contém o desenvolvimento do Trabalho de Conclusão de Curso (TCC) em Engenharia da Computação (IC-UFAL), dedicado à **modelagem e simulação automatizadas de antenas com geometria fractal** por meio de scripts em Python integrados ao simulador eletromagnético **Ansys HFSS**.

O objetivo é gerar a antena de forma paramétrica e reprodutível, sem desenhar nada manualmente na interface do simulador, e avaliá-la como tag RFID passiva na banda de 2,45 GHz. A validação é feita pela comparação com os resultados publicados por Yu e Cai (2015). O trabalho se limita à simulação: não foram fabricados protótipos nem realizadas medições.

---

## Estrutura do Repositório

O projeto é organizado por geometria fractal, o que facilita a inclusão de outras geometrias no futuro (por exemplo, Koch, Minkowski e Hilbert).

```text
TCC_Antena_Fractal/
├── sierpinski/                          # Triângulo de Sierpinski (SFMA)
│   ├── main.py                          # Script definitivo: antena principal (ordem 2)
│   ├── main_ordens.py                   # Variante: compara as ordens fractais 0, 1 e 2
│   ├── main_barra.py                    # Variante: sensibilidade à altura da barra do laço
│   ├── script_interno_hfss*.py          # Scripts gerados pelos main*.py e executados pelo HFSS
│   ├── Antena_Fractal_SFMA_v2.aedt      # Projeto HFSS gerado por main.py
│   ├── Antena_Fractal_SFMA_ordens.aedt  # Projeto HFSS gerado por main_ordens.py
│   ├── Antena_Fractal_SFMA_barra.aedt   # Projeto HFSS gerado por main_barra.py
│   └── historico/                       # Versões anteriores do código (main1.py a main15.py)
│
├── resultados/                          # Dados exportados do HFSS e scripts de análise
│   ├── S11_chip_*.csv, Z_entrada_*.csv  # Curvas exportadas (ordens fractais e posições da barra)
│   ├── profile_ordem2.prof              # Perfil de tempo e memória da solução (ordem 2)
│   ├── convergencia_ordem2.conv         # Histórico de convergência da malha (ordem 2)
│   ├── plotar_comparacao_ordens.py      # Gera images/S11_chip_ordens.png e a tabela de métricas
│   ├── plotar_comparacao_barra.py       # Gera images/S11_chip_barra.png e a tabela de métricas
│   └── gerar_figuras_fractais.py        # Gera as figuras do Capítulo 2: fractal_koch, fractal_hilbert e fractal_sierpinski
│
├── images/                              # Figuras usadas na monografia
├── docs/                                # Material de apoio local (artigos de referência e rascunhos), fora do controle de versão
│
├── requirements.txt                     # Dependências Python do ambiente de desenvolvimento
└── README.md                            # Documentação principal
```

Os scripts `main*.py` usam apenas a biblioteca padrão do Python. Os scripts de `resultados/` precisam do `matplotlib`.

---

## Modelo Implementado: SFMA (Sierpinski Fractal Monopole Antenna)

O modelo baseia-se no artigo:

> **"A RFID Tag Antenna Design Based on Sierpinski Fractal Structure"**
> Yanzhong Yu e Zhishan Cai, *International Journal of Advanced Engineering Research and Science* (IJAERS), 2015.

### Características do projeto

- **Aplicação**: tag RFID passiva na banda de 2,45 GHz.
- **Substrato**: epóxi/Kevlar ($\varepsilon_r = 3{,}6$, $\tan\delta = 0$), com $23{,}2\text{ mm} \times 24{,}9\text{ mm} \times 1{,}0\text{ mm}$ (largura $\times$ comprimento $\times$ espessura).
- **Impedância do chip**: $Z_{\text{chip}} = 30 - j200\,\Omega$.
- **Casamento**: laço indutivo integrado à antena, que fornece reatância indutiva próxima de $+j200\,\Omega$ para o casamento conjugado com o chip capacitivo.
- **Plano de terra**: faixa truncada de $3\text{ mm}$ no verso da placa, ligada ao laço por duas vias.
- **Excitação e análise**: porta concentrada (*lumped port*) com referência de $50\,\Omega$ renormalizada. O coeficiente de reflexão em relação ao chip, $S_{11}^{\text{chip}}$, é calculado no pós-processamento com a expressão de Kurokawa, a partir de $Z(1,1)$.

### Parâmetros geométricos (Tabela 1 do artigo)

| Parâmetro | Descrição | Valor |
| :--- | :--- | :--- |
| $L$ | Altura do menor triângulo | $4{,}8\text{ mm}$ |
| $R$ | Razão $W/L$ | $0{,}577$ |
| $W$ | Meia-largura ($R \times L$) | $2{,}77\text{ mm}$ |
| $WL$ | Altura da perna esquerda do laço | $5{,}0\text{ mm}$ |
| $LW$ | Largura da perna esquerda do laço | $1{,}0\text{ mm}$ |
| $L_1$ | Vão horizontal do laço | $5{,}2\text{ mm}$ |
| $W_1$ | Espessura da barra superior do laço | $1{,}0\text{ mm}$ |
| $L_2$ | Altura da perna direita | $5{,}3\text{ mm}$ |
| $W_2$ | Largura da perna direita | $1{,}0\text{ mm}$ |
| $H_{\text{gnd}}$ | Altura do plano de terra no verso | $3{,}0\text{ mm}$ |

O artigo não informa a altura da barra superior do laço. Neste trabalho ela ocupa $Y = 4{,}0$ a $5{,}0\text{ mm}$, isto é, $0{,}3\text{ mm}$ abaixo do topo da perna direita. A sensibilidade da sintonia a essa escolha é avaliada com o `main_barra.py`.

---

## Como Executar

1. Instale o **Ansys Electronics Desktop (HFSS)**. O trabalho foi desenvolvido com a versão 2025 R2.4 (Ansys Student).
2. Execute o script desejado a partir da raiz do repositório:

   ```bash
   python sierpinski/main.py            # antena principal (ordem 2)
   python sierpinski/main_ordens.py     # ordens fractais 0, 1 e 2 em um único projeto
   python sierpinski/main_barra.py      # duas alturas da barra do laço em um único projeto
   ```

   Nos três casos, o script pede o caminho do `ansysedt.exe`. Pressione ENTER para usar o caminho padrão (`C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe`). Com a opção `--gerar-apenas`, `main_ordens.py` e `main_barra.py` apenas geram o script interno, sem abrir o HFSS.
3. O script gera a geometria de forma paramétrica, cria o substrato, o plano de terra, o laço, as vias, a porta, a caixa de radiação (margem de $35\text{ mm}$, maior que $\lambda/4$) e as esferas de campo distante. Em seguida, configura o solver (convergência $\Delta S \le 0{,}01$, de 3 a 15 passes) e a varredura de $1{,}5$ a $4{,}0\text{ GHz}$, e salva o projeto `.aedt`.
4. No HFSS, execute *Analyze All*. Os relatórios já estão configurados:
   - `Z_entrada`: $\text{Re}(Z)$ e $\text{Im}(Z)$;
   - `S11_chip`: perda de retorno referenciada ao chip ($30 - j200\,\Omega$);
   - `S11_50ohm`: $S_{11}$ com referência de $50\,\Omega$;
   - `Ganho_3D`: ganho total em 3D em $2{,}45\text{ GHz}$;
   - `Diagrama_2D_Planos` e `Diagrama_2D_XY`: cortes polares do ganho.
5. Para refazer as figuras de comparação a partir dos CSVs exportados (salvos em `resultados/`):

   ```bash
   python resultados/plotar_comparacao_ordens.py
   python resultados/plotar_comparacao_barra.py
   ```

6. Para refazer as figuras do Capítulo 2 (curva de Koch, curva de Hilbert e triângulo de Sierpinski), que são desenhadas por código:

   ```bash
   python resultados/gerar_figuras_fractais.py
   ```

---

## Resultados Obtidos

Todos os valores são de simulação e foram obtidos nas mesmas condições (mesma malha adaptativa, mesma caixa de radiação e mesma varredura).

### Antena principal (ordem 2, barra em $Y = 4{,}0$ a $5{,}0\text{ mm}$)

| Grandeza | Este trabalho | Yu e Cai (2015) |
| :--- | :--- | :--- |
| Mínimo de $S_{11}^{\text{chip}}$ | $-29{,}96\text{ dB}$ em $2{,}48\text{ GHz}$ | $-29{,}60\text{ dB}$ em $2{,}45\text{ GHz}$ |
| $S_{11}^{\text{chip}}$ em $2{,}45\text{ GHz}$ | $-14{,}52\text{ dB}$ | $-29{,}60\text{ dB}$ |
| Banda de $-10\text{ dB}$ | $2{,}432$ a $2{,}529\text{ GHz}$ ($97\text{ MHz}$) | $2{,}41$ a $2{,}50\text{ GHz}$ ($90\text{ MHz}$) |
| $Z_{\text{ant}}$ em $2{,}45\text{ GHz}$ | $24{,}56 + j191{,}14\,\Omega$ | $28{,}35 + j201{,}00\,\Omega$ |
| Ganho máximo | $2{,}38\text{ dBi}$ | $2{,}04\text{ dBi}$ |
| Alcance estimado (Friis) | $5{,}01\text{ m}$ | $4{,}91\text{ m}$ |

A ressonância ficou deslocada em $30\text{ MHz}$ ($1{,}2\,\%$) em relação à referência. O alcance é um limite superior, pois a simulação usa condutores perfeitos e substrato sem perdas, em espaço livre, com $P_t = 1\text{ W}$, $G_t = 8\text{ dBi}$ e $P_{\text{th}} = -14\text{ dBm}$.

### Efeito da ordem do fractal (`main_ordens.py`)

O triângulo externo é o mesmo nas três ordens, de modo que a comparação é "mesmo envelope, menos metal".

| Ordem | Recortes | Área metálica ($\text{mm}^2$) | Mínimo de $S_{11}^{\text{chip}}$ | $S_{11}^{\text{chip}}$ em $2{,}45\text{ GHz}$ | Banda de $-10\text{ dB}$ | Ganho máximo |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| 0 | 0 | $212{,}7$ | $-18{,}29\text{ dB}$ em $2{,}47\text{ GHz}$ | $-14{,}49\text{ dB}$ | $92\text{ MHz}$ | $2{,}33\text{ dBi}$ |
| 1 | 1 | $159{,}5$ | $-22{,}10\text{ dB}$ em $2{,}46\text{ GHz}$ | $-20{,}42\text{ dB}$ | $95\text{ MHz}$ | $2{,}24\text{ dBi}$ |
| 2 | 4 | $119{,}6$ | $-29{,}96\text{ dB}$ em $2{,}48\text{ GHz}$ | $-14{,}52\text{ dB}$ | $97\text{ MHz}$ | $2{,}38\text{ dBi}$ |

A ordem 2 usa $43{,}8\,\%$ menos metal que o triângulo cheio, com ressonância, largura de banda, ganho e alcance comparáveis. Como o triângulo externo foi mantido, os recortes não deslocam a ressonância nem miniaturizam a antena nesta configuração: o benefício observado é a economia de material. O laço é o da antena de referência (ordem 2) e não foi reotimizado para as demais, por isso as diferenças de profundidade em $2{,}45\text{ GHz}$ não devem ser atribuídas à ordem fractal.

### Sensibilidade à altura da barra do laço (`main_barra.py`)

| Grandeza | Barra em $Y = 4{,}0$ a $5{,}0\text{ mm}$ | Barra em $Y = 4{,}3$ a $5{,}3\text{ mm}$ |
| :--- | :--- | :--- |
| Mínimo de $S_{11}^{\text{chip}}$ | $-29{,}96\text{ dB}$ em $2{,}48\text{ GHz}$ | $-14{,}46\text{ dB}$ em $2{,}40\text{ GHz}$ |
| $S_{11}^{\text{chip}}$ em $2{,}45\text{ GHz}$ | $-14{,}52\text{ dB}$ | $-8{,}99\text{ dB}$ |
| Banda de $-10\text{ dB}$ | $2{,}432$ a $2{,}529\text{ GHz}$ ($97\text{ MHz}$) | $2{,}363$ a $2{,}441\text{ GHz}$ ($78\text{ MHz}$) |
| $Z_{\text{ant}}$ em $2{,}45\text{ GHz}$ | $24{,}56 + j191{,}14\,\Omega$ | $33{,}98 + j223{,}93\,\Omega$ |
| Ganho máximo | $2{,}38\text{ dBi}$ | $2{,}40\text{ dBi}$ |

Alinhar a barra ao topo da perna direita ($0{,}3\text{ mm}$ acima) move a ressonância em cerca de $80\text{ MHz}$ e tira os $2{,}45\text{ GHz}$ da banda de $-10\text{ dB}$. A ressonância de Yu e Cai fica entre os resultados das duas posições, o que indica que esse detalhe, não especificado no artigo, pode explicar boa parte do desvio de $30\text{ MHz}$.

---

## Histórico de Desenvolvimento

A pasta `sierpinski/historico/` guarda as 15 versões intermediárias do código (`main1.py` a `main15.py`) e os projetos HFSS associados. Elas são mantidas apenas como registro. O `main.py` equivale ao `main15.py` acrescido dos relatórios de ganho e diagramas de radiação.

---

## Referência Principal

Y. Yu e Z. Cai, "A RFID Tag Antenna Design Based on Sierpinski Fractal Structure", *International Journal of Advanced Engineering Research and Science*, vol. 2, n. 4, abr. 2015. Os PDFs de referência não são versionados neste repositório (direitos autorais); as referências completas estão na monografia.
