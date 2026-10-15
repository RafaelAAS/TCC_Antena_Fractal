# ==============================================================================
# ALTERACOES EM RELACAO A VERSAO ANTERIOR
#  1. Porta: referencia padrao de 50 ohm (CharImp=Zpi, renormalizada). A string
#     "30-200i ohm" em CharImp nao e a forma de definir referencia complexa no HFSS.
#  2. Pos-processamento: Z(1,1) e S11_chip = (Zin - conj(Zchip))/(Zin + Zchip), que e
#     como o artigo obtem -29,6 dB (Zchip = 30 - j200 ohm). Relatorios criados em Results.
#  3. Laco com os valores da Tabela 1 (L1 = 5,2 e L2 = 5,3; antes: 5,3 na barra e 5,0 na
#     perna direita). Parametros agora no topo do script.
#  4. Caixa de radiacao com 35 mm de margem (lambda/4 em 2,45 GHz = 30,6 mm).
#  5. Setup: MaxDeltaS 0,01 e minimo de 3 passes (antes 0,02 e 1).
#  6. Folhas extras geradas pelo Subtract tambem recebem PEC (seguranca).
#  7. Projeto salvo como Antena_Fractal_SFMA_v2.aedt; mensagens com {chaves} corrigidas.
# ==============================================================================
import subprocess
import time
import os

# ==============================================================================
# PARAMETROS DO PROJETO  (Tabela 1 do artigo de Yu & Cai, IJAERS 2015) - tudo em mm
# Edite aqui e rode de novo para testar variacoes (o artigo mostra a sensibilidade
# da impedancia a LW, L1, L2, W1, W2 nas Figs. 14-19).
# ==============================================================================
L_TRI     = 4.8      # L  : altura do menor triangulo
RATIO_R   = 0.577    # R  : W/L  (W = R*L)
WL        = 5.0      # altura da perna esquerda do laco
LW        = 1.0      # largura da perna esquerda
L1        = 5.2      # vao horizontal do laco (entre as pernas)         [artigo: 5,2]
W1        = 1.0      # espessura da barra superior do laco
L2        = 5.3      # altura total da perna direita                    [artigo: 5,3]
W2        = 1.0      # largura da perna direita
Y_PORTA   = 2.1      # trecho inferior da perna direita ate a porta (Fig. 3: 2,1 mm)
GAP_PORTA = 1.5      # gap onde fica o chip / porta (Fig. 3: 1,5 mm)
Y_APICE   = WL - 1.0 # vertice inferior do triangulo (4,0 mm)

W_SUB, L_SUB, H_SUB = 23.2, 24.9, 1.0   # substrato epoxy_Kevlar (er = 3,6; tan d = 0)
H_GND = 3.0                             # plano de terra (verso), faixa de 3 mm

ORDEM_FRACTAL = 2

# 1.0 = geometria exata do artigo (os 9 triangulos se tocam so em vertices).
# Teste de diagnostico: 0.97 encolhe os furos em 3%, de modo que os triangulos passam a se
# ligar por faixas finas de metal (e aparece um rebordo fino nas bordas). Se o resultado mudar
# muito em relacao a 1.0, a conexao entre os triangulos esta pesando na simulacao.
FATOR_RECORTE = 1.0

# Impedancia do chip do artigo (Zchip = 30 - j200 ohm). Usada so no pos-processamento.
Z_CHIP_R, Z_CHIP_X = 30.0, -200.0

# Distancia entre a antena e a caixa de radiacao. lambda/4 em 2,45 GHz = 30,6 mm.
MARGEM_AR = 35.0


def mm(v):
    """formata um numero como string de comprimento do HFSS (ex.: 5.7 -> '5.7mm')"""
    v = round(v, 6)
    return f"{v:g}mm"


# ==============================================================================
# ALGORITMO GERADOR DO FRACTAL DE SIERPINSKI
# ==============================================================================
def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)

cutouts_sym = []
def build_sierpinski_sym(v1, v2, v3, order, current_order=1):
    if current_order > order:
        return
    m1 = midpoint(v1, v2)
    m2 = midpoint(v2, v3)
    m3 = midpoint(v3, v1)
    cutouts_sym.append((m1, m2, m3))
    build_sierpinski_sym(v1, m1, m3, order, current_order+1)
    build_sierpinski_sym(m1, v2, m2, order, current_order+1)
    build_sierpinski_sym(m3, m2, v3, order, current_order+1)

build_sierpinski_sym((0.0, 0.0), (4.0, 4.0), (-4.0, 4.0), order=ORDEM_FRACTAL)

def encolher(tri, k):
    """encolhe o triangulo de recorte em torno do seu centroide (k=1.0 -> sem alteracao)"""
    cx = sum(p[0] for p in tri) / 3.0
    cy = sum(p[1] for p in tri) / 3.0
    return tuple((cx + k * (p[0] - cx), cy + k * (p[1] - cy)) for p in tri)

# ==============================================================================
# GERACAO DINAMICA DOS COMANDOS HFSS (IRONPYTHON)
# ==============================================================================
hfss_cutouts_code = ""
cutout_names = []

def fmt(v):
    v = round(v, 6)
    return 0.0 if v == 0 else v   # elimina -0.0

def format_coord(c):
    cw, cl = fmt(c[0]), fmt(c[1])
    x_str = f"{cw}*W" if cw != 0 else "0mm"
    y_str = f"{mm(Y_APICE)} + {cl}*L" if cl != 0 else mm(Y_APICE)
    return x_str, y_str

for i, tri in enumerate(cutouts_sym):
    name = f"Cutout_{i+1}"
    cutout_names.append(name)
    m1, m2, m3 = encolher(tri, FATOR_RECORTE)
    x1, y1 = format_coord(m1)
    x2, y2 = format_coord(m2)
    x3, y3 = format_coord(m3)

    hfss_cutouts_code += f"""
oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "{x1}", "Y:=", "{y1}", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "{x2}", "Y:=", "{y2}", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "{x3}", "Y:=", "{y3}", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "{x1}", "Y:=", "{y1}", "Z:=", "{mm(H_SUB)}"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "{name}", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
"""

hfss_subtract_code = f"""
oEditor.Subtract(["NAME:Selections", "Blank Parts:=", "Patch_Principal", "Tool Parts:=", "{','.join(cutout_names)}"], ["NAME:SubtractParameters", "KeepOriginals:=", False])
"""

def retangulo(nome, x0, y0, z0, w, h, eixo, cor="(255 128 0)"):
    return f"""oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "{mm(x0)}", "YStart:=", "{mm(y0)}", "ZStart:=", "{mm(z0)}", "Width:=", "{mm(w)}", "Height:=", "{mm(h)}", "WhichAxis:=", "{eixo}"], ["NAME:Attributes", "Name:=", "{nome}", "Flags:=", "", "Color:=", "{cor}", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])"""

# --- Laco de casamento (Fig. 3 do artigo), todas as pecas no topo do substrato (Z = H_SUB)
x_esq   = -LW / 2.0              # borda esquerda da perna esquerda
x_dir   = LW / 2.0 + L1          # borda esquerda da perna direita
x_porta = x_dir + W2 / 2.0       # centro da porta em X
y_topo_dir = Y_PORTA + GAP_PORTA # onde comeca o trecho superior da perna direita

codigo_laco = "\n".join([
    retangulo("Loop_Left",         x_esq,      0.0,        H_SUB, LW, WL, "Z"),
    retangulo("Loop_Top",          LW / 2.0,   WL - W1,    H_SUB, L1, W1, "Z"),
    retangulo("Loop_Right_Bottom", x_dir,      0.0,        H_SUB, W2, Y_PORTA, "Z"),
    retangulo("Loop_Right_Top",    x_dir,      y_topo_dir, H_SUB, W2, L2 - y_topo_dir, "Z"),
])

# Vias nas bordas do substrato (plano XZ em Y=0): Width corre em Z, Height corre em X
codigo_vias = "\n".join([
    retangulo("Via_Left",  x_esq, 0.0, 0.0, H_SUB, LW, "Y"),
    retangulo("Via_Right", x_dir, 0.0, 0.0, H_SUB, W2, "Y"),
])

codigo_porta_folha = retangulo("Port_Sheet", x_dir, Y_PORTA, H_SUB, W2, GAP_PORTA, "Z", cor="(0 0 255)")

# --- Pos-processamento: Z de entrada e S11 referenciado ao chip (potencia, Kurokawa)
#     S11_chip = (Zin - conj(Zchip)) / (Zin + Zchip)   <- e assim que o artigo obtem -29,6 dB
expr_s11_chip = (f"(Z(Port1,Port1)-cmplx({Z_CHIP_R},{-Z_CHIP_X}))"
                 f"/(Z(Port1,Port1)+cmplx({Z_CHIP_R},{Z_CHIP_X}))")

# ==============================================================================
# CONFIGURACOES DE CAMINHOS E SCRIPT BASE
# ==============================================================================
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_script_hfss = os.path.join(diretorio_atual, "script_interno_hfss.py")
caminho_projeto = os.path.join(diretorio_atual, "Antena_Fractal_SFMA_v2.aedt")
caminho_projeto_com_duplas = caminho_projeto.replace("\\", "\\\\")

codigo_hfss = f"""# -*- coding: utf-8 -*-
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "Iteracao_0", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("Iteracao_0")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oModule_Bound = oDesign.GetModule("BoundarySetup")

# 1. Variaveis Globais
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab", ["NAME:PropServers", "LocalVariables"],
            [
                "NAME:NewProps",
                ["NAME:W_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "{mm(W_SUB)}"],
                ["NAME:L_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "{mm(L_SUB)}"],
                ["NAME:L", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "{mm(L_TRI)}"],
                ["NAME:Ratio_R", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "{RATIO_R}"],
                ["NAME:W", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "Ratio_R*L"]
            ]
        ]
    ])

# 2. Material
oDefinitionManager = oProject.GetDefinitionManager()
oDefinitionManager.AddMaterial(["NAME:epoxy_Kevlar", "CoordinateSystemType:=", "Cartesian", "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]], "permittivity:=", "3.6", "dielectric_loss_tangent:=", "0"])

# 3. Substrato
oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", "{mm(-W_SUB / 2.0)}", "YPosition:=", "0mm", "ZPosition:=", "0mm", "XSize:=", "{mm(W_SUB)}", "YSize:=", "{mm(L_SUB)}", "ZSize:=", "{mm(H_SUB)}"], ["NAME:Attributes", "Name:=", "Substrato", "Flags:=", "", "Color:=", "(0 255 0)", "Transparency:=", 0.5, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"epoxy_Kevlar\\"", "SolveInside:=", True])

# 4. Plano de Terra no VERSO (Z=0mm)
{retangulo("Plano_de_Terra", -W_SUB / 2.0, 0.0, 0.0, W_SUB, H_GND, "Z")}
oModule_Bound.AssignPerfectE(["NAME:GND_PerfectE", "Objects:=", ["Plano_de_Terra"], "InfGroundPlane:=", False])

# 5. Triangulo base no TOPO (Z=H). Vertice inferior em Y={mm(Y_APICE)}; base superior em Y={mm(Y_APICE)}+4*L
oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "0mm", "Y:=", "{mm(Y_APICE)}", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "4*W", "Y:=", "{mm(Y_APICE)} + 4*L", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "-4*W", "Y:=", "{mm(Y_APICE)} + 4*L", "Z:=", "{mm(H_SUB)}"], ["NAME:PLPoint", "X:=", "0mm", "Y:=", "{mm(Y_APICE)}", "Z:=", "{mm(H_SUB)}"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Patch_Principal", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# 6. Recortes do fractal
{hfss_cutouts_code}
{hfss_subtract_code}

# 7. Circuito de casamento no TOPO (valores da Tabela 1 do artigo)
{codigo_laco}

# Unificando o cobre do TOPO
oEditor.Unite(["NAME:Selections", "Selections:=", "Patch_Principal,Loop_Left,Loop_Top,Loop_Right_Bottom,Loop_Right_Top"], ["NAME:UniteParameters", "KeepOriginals:=", False])
oModule_Bound.AssignPerfectE(["NAME:Patch_PerfectE", "Objects:=", ["Patch_Principal"], "InfGroundPlane:=", False])

# 8. VIAS verticais conectando o laco ao terra
{codigo_vias}
oModule_Bound.AssignPerfectE(["NAME:ViaLeft_E", "Objects:=", ["Via_Left"], "InfGroundPlane:=", False])
oModule_Bound.AssignPerfectE(["NAME:ViaRight_E", "Objects:=", ["Via_Right"], "InfGroundPlane:=", False])

# 9. Porta de excitacao no gap da perna direita.
#    Referencia PADRAO de 50 ohm (renormalizada). A comparacao com o chip (30-j200) e feita
#    no pos-processamento, a partir de Z(1,1), que independe da referencia da porta.
{codigo_porta_folha}
oModule_Bound.AssignLumpedPort(["NAME:Port1", "Objects:=", ["Port_Sheet"], "DoDeembed:=", False, "RenormalizeAllTerminals:=", True, ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True, ["NAME:IntLine", "Start:=", ["{mm(x_porta)}", "{mm(Y_PORTA)}", "{mm(H_SUB)}"], "End:=", ["{mm(x_porta)}", "{mm(Y_PORTA + GAP_PORTA)}", "{mm(H_SUB)}"]], "AlignmentGroup:=", 0, "CharImp:=", "Zpi", "RenormImp:=", "50ohm"]], "ShowPredefinedFieldOnPolygons:=", True])

# Seguranca: se o Subtract tiver gerado folhas extras (triangulos separados), elas tambem sao PEC
folhas_extras = [n for n in oEditor.GetObjectsInGroup("Sheets") if n not in ("Plano_de_Terra", "Patch_Principal", "Via_Left", "Via_Right", "Port_Sheet")]
if len(folhas_extras) > 0:
    oModule_Bound.AssignPerfectE(["NAME:PEC_Extras", "Objects:=", folhas_extras, "InfGroundPlane:=", False])
    oDesktop.AddMessage("", "", 1, "Subtract gerou folhas extras (PEC atribuido): " + ",".join(folhas_extras))

# 10. Caixa de Radiacao (margem >= lambda/4 em 2,45 GHz)
oEditor.CreateBox(
    ["NAME:BoxParameters", "XPosition:=", "{mm(-W_SUB / 2.0 - MARGEM_AR)}", "YPosition:=", "{mm(-MARGEM_AR)}", "ZPosition:=", "{mm(-MARGEM_AR)}", "XSize:=", "{mm(W_SUB + 2 * MARGEM_AR)}", "YSize:=", "{mm(L_SUB + 2 * MARGEM_AR)}", "ZSize:=", "{mm(H_SUB + 2 * MARGEM_AR)}"],
    ["NAME:Attributes", "Name:=", "AirBox", "Flags:=", "", "Color:=", "(0 255 255)", "Transparency:=", 0.9, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True]
)
oModule_Bound.AssignRadiation(["NAME:Radiation1", "Objects:=", ["AirBox"], "IsFssReference:=", False, "IsIncidentField:=", False])

# 11. Setup e varredura. Como |S11| a 50 ohm fica perto de 1, um erro pequeno em S vira erro
#     grande em Z; por isso MaxDeltaS menor e minimo de passes maior.
oModule_Setup = oDesign.GetModule("AnalysisSetup")
oModule_Setup.InsertSetup("HfssDriven",
    ["NAME:Setup1", "Frequency:=", "2.45GHz", "PortsOnly:=", False, "MaxDeltaS:=", 0.01, "UseMatrixConv:=", False, "MaximumPasses:=", 15, "MinimumPasses:=", 3, "MinimumConvergedPasses:=", 2]
)
oModule_Setup.InsertFrequencySweep("Setup1",
    ["NAME:Sweep1", "Type:=", "Interpolating", "IsEnabled:=", True, "RangeType:=", "LinearStep", "RangeStart:=", "1.5GHz", "RangeEnd:=", "4.0GHz", "RangeStep:=", "0.01GHz", "SaveFields:=", False, "SaveRadFields:=", False]
)

# 12. Relatorios (aparecem em Results depois do Analyze All). Se falhar, crie a mao (ver aviso).
try:
    oModule_Out = oDesign.GetModule("OutputVariable")
    oModule_Out.CreateOutputVariable("S11_chip", "{expr_s11_chip}", "Setup1 : Sweep1", "Modal Solution Data", [])
    oModule_Rep = oDesign.GetModule("ReportSetup")
    oModule_Rep.CreateReport("Z_entrada", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["re(Z(Port1,Port1))", "im(Z(Port1,Port1))"]], [])
    oModule_Rep.CreateReport("S11_chip", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["dB(S11_chip)"]], [])
    oModule_Rep.CreateReport("S11_50ohm", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["dB(S(Port1,Port1))"]], [])
except Exception as erro:
    oDesktop.AddMessage("", "", 1, "Relatorios nao criados automaticamente (" + str(erro) + "). Crie a mao: re/im(Z(Port1,Port1)) e dB(S11_chip).")

oEditor.FitAll()
oProject.SaveAs("{caminho_projeto_com_duplas}", True)
"""

print("Gerando script interno do HFSS...")
with open(caminho_script_hfss, "w", encoding="utf-8") as arquivo:
    arquivo.write(codigo_hfss)

def obter_caminho_valido(mensagem, default=""):
    while True:
        caminho = input(mensagem).strip()
        if caminho == "" and default != "":
            return default
        if caminho.lower() == 'sair':
            exit()
        elif os.path.isfile(caminho):
            return caminho
        else:
            print(f"\nO ficheiro {caminho} nao foi encontrado. Tente novamente.")

caminho_padrao = r"C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe"
print(f"\nPressione ENTER para usar o caminho padrao: {caminho_padrao}")
caminho_ansysedt = obter_caminho_valido("Ou digite o caminho correto: ", default=caminho_padrao)

comando = f'"{caminho_ansysedt}" -runscript "{caminho_script_hfss}"'
print("\nA iniciar o Ansys...")
subprocess.Popen(comando, shell=True)
time.sleep(5)