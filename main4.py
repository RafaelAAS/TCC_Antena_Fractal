import subprocess
import time
import os

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

# 1. Variaveis Corrigidas (W_sub e L_sub invertidos para orientacao correta)
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            [
                "NAME:PropServers", "LocalVariables"
            ],
            [
                "NAME:NewProps",
                ["NAME:W_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "23.2mm"],
                ["NAME:L_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "24.9mm"],
                ["NAME:h", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1mm"],
                ["NAME:L", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "4.8mm"],
                ["NAME:Ratio_R", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.577"],
                ["NAME:W", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "Ratio_R*L"],
                ["NAME:WL", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5mm"],
                ["NAME:LW", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5.2mm"],
                ["NAME:L1", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1mm"],
                ["NAME:W1", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5.3mm"],
                ["NAME:L2", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1mm"],
                ["NAME:W2", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1mm"],
                ["NAME:GND_h", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "3mm"]
            ]
        ]
    ])

# 2. Material epoxy_Kevlar
oDefinitionManager = oProject.GetDefinitionManager()
oDefinitionManager.AddMaterial(
    [
        "NAME:epoxy_Kevlar",
        "CoordinateSystemType:=", "Cartesian",
        "BulkOrSurfaceType:=", 1,
        [
            "NAME:PhysicsTypes",
            "set:=", ["Electromagnetic"]
        ],
        "permittivity:=", "3.6",
        "dielectric_loss_tangent:=", "0"
    ])

# 3. Substrato
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "-W_sub/2",
        "YPosition:=", "0mm",
        "ZPosition:=", "0mm",
        "XSize:=", "W_sub",
        "YSize:=", "L_sub",
        "ZSize:=", "h"
    ], 
    [
        "NAME:Attributes",
        "Name:=", "Substrato",
        "Flags:=", "",
        "Color:=", "(0 255 0)",
        "Transparency:=", 0.5,
        "PartCoordinateSystem:=", "Global",
        "UDMId:=", "",
        "MaterialValue:=", "\\"epoxy_Kevlar\\"",
        "SurfaceMaterialValue:=", "\\"\\"",
        "SolveInside:=", True,
        "IsMaterialEditable:=", True,
        "UseMaterialAppearance:=", False
    ])

# 4. Plano de Terra Parcial
oEditor.CreateRectangle(
    [
        "NAME:RectangleParameters",
        "IsCovered:=", True,
        "XStart:=", "-W_sub/2",
        "YStart:=", "0mm",
        "ZStart:=", "h",
        "Width:=", "W_sub",
        "Height:=", "GND_h",
        "WhichAxis:=", "Z"
    ], 
    [
        "NAME:Attributes",
        "Name:=", "Plano_de_Terra",
        "Flags:=", "",
        "Color:=", "(255 128 0)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "UDMId:=", "",
        "MaterialValue:=", "\\"vacuum\\"",
        "SurfaceMaterialValue:=", "\\"\\"",
        "SolveInside:=", True,
        "IsMaterialEditable:=", True,
        "UseMaterialAppearance:=", False
    ])

oModule = oDesign.GetModule("BoundarySetup")
oModule.AssignPerfectE(["NAME:GND_PerfectE", "Objects:=", ["Plano_de_Terra"], "InfGroundPlane:=", False])

# 5. Desenhando o Triangulo Base (Ordem 0)
oEditor.CreatePolyline(
    [
        "NAME:PolylineParameters",
        "IsPolylineCovered:=", True,
        "IsPolylineClosed:=", True,
        [
            "NAME:PolylinePoints",
            ["NAME:PLPoint", "X:=", "0mm", "Y:=", "WL", "Z:=", "h"],
            ["NAME:PLPoint", "X:=", "4*W", "Y:=", "WL + 4*L", "Z:=", "h"],
            ["NAME:PLPoint", "X:=", "-4*W", "Y:=", "WL + 4*L", "Z:=", "h"],
            ["NAME:PLPoint", "X:=", "0mm", "Y:=", "WL", "Z:=", "h"]
        ],
        [
            "NAME:PolylineSegments",
            ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2],
            ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2],
            ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]
        ],
        [
            "NAME:PolylineXSection",
            "XSectionType:=", "None",
            "XSectionOrient:=", "Auto",
            "XSectionWidth:=", "0mm",
            "XSectionTopWidth:=", "0mm",
            "XSectionHeight:=", "0mm",
            "XSectionNumSegments:=", "0",
            "XSectionBendType:=", "Corner"
        ]
    ], 
    [
        "NAME:Attributes",
        "Name:=", "Patch_Principal",
        "Flags:=", "",
        "Color:=", "(255 128 0)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "UDMId:=", "",
        "MaterialValue:=", "\\"vacuum\\"",
        "SurfaceMaterialValue:=", "\\"\\"",
        "SolveInside:=", True,
        "IsMaterialEditable:=", True,
        "UseMaterialAppearance:=", False
    ])

oModule.AssignPerfectE(["NAME:Patch_PerfectE", "Objects:=", ["Patch_Principal"], "InfGroundPlane:=", False])

oEditor.FitAll()
oProject.SaveAs("{caminho_projeto_com_duplas}", True)
"""

print("Gerando script interno do HFSS (Iteracao 5 - Dimensoes Corrigidas)...")
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
            print(f"\nO caminho {{caminho}} nao foi encontrado. Tente novamente.")

caminho_padrao = r"C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe"
print(f"\nPressione ENTER para usar o caminho padrao: {{caminho_padrao}}")
caminho_ansysedt = obter_caminho_valido("Ou digite o caminho correto: ", default=caminho_padrao)

comando = f'"{caminho_ansysedt}" -runscript "{caminho_script_hfss}"'
print("\nIniciando o Ansys... Aguarde o desenho corrigido.")
subprocess.Popen(comando, shell=True)
time.sleep(5)