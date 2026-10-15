import subprocess
import time
import os

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

build_sierpinski_sym((0.0, 0.0), (4.0, 4.0), (-4.0, 4.0), order=2) 

# ==============================================================================
# GERACAO DINAMICA DOS COMANDOS HFSS (IRONPYTHON)
# ==============================================================================
hfss_cutouts_code = ""
cutout_names = []

for i, (m1, m2, m3) in enumerate(cutouts_sym):
    name = f"Cutout_{i+1}"
    cutout_names.append(name)
    def format_coord(c):
        cw, cl = c
        x_str = f"{cw}*W" if cw != 0 else "0mm"
        y_str = f"WL + {cl}*L" if cl != 0 else "WL"
        return x_str, y_str
    x1, y1 = format_coord(m1)
    x2, y2 = format_coord(m2)
    x3, y3 = format_coord(m3)

    hfss_cutouts_code += f"""
oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "{x1}", "Y:=", "{y1}", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "{x2}", "Y:=", "{y2}", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "{x3}", "Y:=", "{y3}", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "{x1}", "Y:=", "{y1}", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "{name}", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
"""

hfss_subtract_code = f"""
oEditor.Subtract(["NAME:Selections", "Blank Parts:=", "Patch_Principal", "Tool Parts:=", "{','.join(cutout_names)}"], ["NAME:SubtractParameters", "KeepOriginals:=", False])
"""

# ==============================================================================
# CONFIGURAÇÕES DE CAMINHOS E SCRIPT BASE
# ==============================================================================
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_script_hfss = os.path.join(diretorio_atual, "script_interno_hfss.py")
caminho_projeto = os.path.join(diretorio_atual, "Antena_Fractal_SFMA.aedt")
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

# 1. Variaveis Matematicas Iniciais
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab", ["NAME:PropServers", "LocalVariables"],
            [
                "NAME:NewProps",
                ["NAME:L", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "4.8mm"],
                ["NAME:Ratio_R", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.577"],
                ["NAME:W", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "Ratio_R*L"],
                ["NAME:WL", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5mm"]
            ]
        ]
    ])

# 2. Material
oDefinitionManager = oProject.GetDefinitionManager()
oDefinitionManager.AddMaterial(["NAME:epoxy_Kevlar", "CoordinateSystemType:=", "Cartesian", "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]], "permittivity:=", "3.6", "dielectric_loss_tangent:=", "0"])

# 3. Substrato (Centralizado em X=0, Y de 0 a 24.9mm)
oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", "-11.6mm", "YPosition:=", "0mm", "ZPosition:=", "0mm", "XSize:=", "23.2mm", "YSize:=", "24.9mm", "ZSize:=", "1mm"], ["NAME:Attributes", "Name:=", "Substrato", "Flags:=", "", "Color:=", "(0 255 0)", "Transparency:=", 0.5, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"epoxy_Kevlar\\"", "SolveInside:=", True])

# 4. Plano de Terra no Verso (Z=0mm, Y de 0 a 3mm)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-11.6mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "23.2mm", "Height:=", "3mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Plano_de_Terra", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
oModule_Bound.AssignPerfectE(["NAME:GND_PerfectE", "Objects:=", ["Plano_de_Terra"], "InfGroundPlane:=", False])

# 5. Desenhando o Triangulo Base no Topo (Z=1mm)
oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "0mm", "Y:=", "WL", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "4*W", "Y:=", "WL + 4*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-4*W", "Y:=", "WL + 4*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "0mm", "Y:=", "WL", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Patch_Principal", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# 6. Injetando os recortes do fractal
{hfss_cutouts_code}
{hfss_subtract_code}

# 7. Circuito de Casamento (Coordenadas Absolutas Cravadas e Corrigidas)
# Loop_Left: Largura 1mm (X de -0.5 a 0.5), Altura 5.5mm (Y de 0 a 5.5) para conectar com folga no triangulo
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-0.5mm", "YStart:=", "0mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "5.5mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Left", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# Loop_Top: Comprimento 5.2mm (X de 0.5 a 5.7), Largura 1mm (Y de 4.0 a 5.0)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "0.5mm", "YStart:=", "4mm", "ZStart:=", "1mm", "Width:=", "5.2mm", "Height:=", "1mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Top", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# Loop_Right_Bottom: Largura 1mm (X de 5.7 a 6.7), Altura 2.1mm (Y de 0 a 2.1)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "0mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "2.1mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Right_Bottom", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# Loop_Right_Top: Largura 1mm (X de 5.7 a 6.7), Altura 1.4mm (Y de 3.6 a 5.0)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "3.6mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "1.4mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Right_Top", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])

# Unificando o Cobre do Topo
oEditor.Unite(["NAME:Selections", "Selections:=", "Patch_Principal,Loop_Left,Loop_Top,Loop_Right_Bottom,Loop_Right_Top"], ["NAME:UniteParameters", "KeepOriginals:=", False])
oModule_Bound.AssignPerfectE(["NAME:Patch_PerfectE", "Objects:=", ["Patch_Principal"], "InfGroundPlane:=", False])

# 8. VIAS Verticais no Eixo Y (Ligando as bases do loop em Z=1mm ao terra em Z=0mm)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-0.5mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "1mm", "Height:=", "1mm", "WhichAxis:=", "Y"], ["NAME:Attributes", "Name:=", "Via_Left", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "1mm", "Height:=", "1mm", "WhichAxis:=", "Y"], ["NAME:Attributes", "Name:=", "Via_Right", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
oModule_Bound.AssignPerfectE(["NAME:ViaLeft_E", "Objects:=", ["Via_Left"], "InfGroundPlane:=", False])
oModule_Bound.AssignPerfectE(["NAME:ViaRight_E", "Objects:=", ["Via_Right"], "InfGroundPlane:=", False])

# 9. Porta de Excitacao (Completando exatamente o Gap de Y=2.1 a 3.6mm)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "2.1mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "1.5mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Port_Sheet", "Flags:=", "", "Color:=", "(0 0 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True])
oModule_Bound.AssignLumpedPort(["NAME:Port1", "Objects:=", ["Port_Sheet"], "DoDeembed:=", False, "RenormalizeAllTerminals:=", True, ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True, ["NAME:IntLine", "Start:=", ["6.2mm", "2.1mm", "1mm"], "End:=", ["6.2mm", "3.6mm", "1mm"]], "AlignmentGroup:=", 0, "CharImp:=", "Z0", "RenormImp:=", "30-200j ohm"]], "ShowPredefinedFieldOnPolygons:=", True])

# 10. Caixa de Radiacao (Airbox)
oEditor.CreateBox(
    ["NAME:BoxParameters", "XPosition:=", "-40mm", "YPosition:=", "-30mm", "ZPosition:=", "-30mm", "XSize:=", "80mm", "YSize:=", "85mm", "ZSize:=", "61mm"], 
    ["NAME:Attributes", "Name:=", "AirBox", "Flags:=", "", "Color:=", "(0 255 255)", "Transparency:=", 0.9, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True]
)
oModule_Bound.AssignRadiation(["NAME:Radiation1", "Objects:=", ["AirBox"], "IsFssReference:=", False, "IsIncidentField:=", False])

# 11. Configurando o Setup e a Varredura
oModule_Setup = oDesign.GetModule("AnalysisSetup")
oModule_Setup.InsertSetup("HfssDriven", 
    ["NAME:Setup1", "Frequency:=", "2.45GHz", "PortsOnly:=", False, "MaxDeltaS:=", 0.02, "UseMatrixConv:=", False, "MaximumPasses:=", 15, "MinimumPasses:=", 1, "MinimumConvergedPasses:=", 1]
)
oModule_Setup.InsertFrequencySweep("Setup1", 
    ["NAME:Sweep1", "Type:=", "Interpolating", "IsEnabled:=", True, "RangeType:=", "LinearStep", "RangeStart:=", "1.5GHz", "RangeEnd:=", "4.0GHz", "RangeStep:=", "0.01GHz", "SaveFields:=", False, "SaveRadFields:=", False]
)

oEditor.FitAll()
oProject.SaveAs("{caminho_projeto_com_duplas}", True)
"""

print("Gerando script interno do HFSS (Iteracao 12 - Coordenadas Cravadas e Vias Corrigidas)...")
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
            print(f"\nO ficheiro {{caminho}} nao foi encontrado. Tente novamente.")

caminho_padrao = r"C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe"
print(f"\nPressione ENTER para usar o caminho padrao: {{caminho_padrao}}")
caminho_ansysedt = obter_caminho_valido("Ou digite o caminho correto: ", default=caminho_padrao)

comando = f'"{caminho_ansysedt}" -runscript "{caminho_script_hfss}"'
print("\nA iniciar o Ansys... Reconstruindo a antena com a matematica 100% alinhada.")
subprocess.Popen(comando, shell=True)
time.sleep(5)