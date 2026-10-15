import subprocess
import time
import os

# ==============================================================================
# CONFIGURAÇÕES DE CAMINHOS AUTOMÁTICAS
# ==============================================================================
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_script_hfss = os.path.join(diretorio_atual, "script_interno_hfss.py")
caminho_projeto = os.path.join(diretorio_atual, "Antena_Fractal_TCC.aedt")
caminho_projeto_com_duplas = caminho_projeto.replace("\\", "\\\\")

# ==============================================================================
# SCRIPT IRONPYTHON NATIVO (Rodará dentro do Ansys)
# ==============================================================================
codigo_hfss = f"""# -*- coding: utf-8 -*-
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "Iteracao_0", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("Iteracao_0")
oEditor = oDesign.SetActiveEditor("3D Modeler")

# 1. Criando as Variaveis no HFSS
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            [
                "NAME:PropServers", 
                "LocalVariables"
            ],
            [
                "NAME:NewProps",
                [
                    "NAME:W_sub",
                    "PropType:=", "VariableProp",
                    "UserDef:=", True,
                    "Value:=", "60mm"
                ],
                [
                    "NAME:L_sub",
                    "PropType:=", "VariableProp",
                    "UserDef:=", True,
                    "Value:=", "60mm"
                ],
                [
                    "NAME:h",
                    "PropType:=", "VariableProp",
                    "UserDef:=", True,
                    "Value:=", "0.05mm"
                ]
            ]
        ]
    ])

# 1.5. Criando o material customizado da TAG Alien (PET)
oDefinitionManager = oProject.GetDefinitionManager()
oDefinitionManager.AddMaterial(
    [
        "NAME:PET_Alien",
        "CoordinateSystemType:=", "Cartesian",
        "BulkOrSurfaceType:=", 1,
        [
            "NAME:PhysicsTypes",
            "set:=", ["Electromagnetic"]
        ],
        "permittivity:=", "3.2"
    ])

# 2. Desenhando o Substrato com o novo material (PET_Alien)
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "-W_sub/2",
        "YPosition:=", "-L_sub/2",
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
        "MaterialValue:=", "\\"PET_Alien\\"",
        "SurfaceMaterialValue:=", "\\"\\"",
        "SolveInside:=", True,
        "IsMaterialEditable:=", True,
        "UseMaterialAppearance:=", False
    ])

# 3. Desenhando o Plano de Terra
oEditor.CreateRectangle(
    [
        "NAME:RectangleParameters",
        "IsCovered:=", True,
        "XStart:=", "-W_sub/2",
        "YStart:=", "-L_sub/2",
        "ZStart:=", "0mm",
        "Width:=", "W_sub",
        "Height:=", "L_sub",
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

# 4. Atribuindo Condicao de Contorno (Perfect E)
oModule = oDesign.GetModule("BoundarySetup")
oModule.AssignPerfectE(
    [
        "NAME:GND_PerfectE",
        "Objects:=", ["Plano_de_Terra"],
        "InfGroundPlane:=", False
    ])

# Enquadrar a camera e salvar
oEditor.FitAll()
oProject.SaveAs("{caminho_projeto_com_duplas}", True)
"""

# ==============================================================================
# EXECUÇÃO NO WINDOWS
# ==============================================================================
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
            print(f"\nO caminho {{caminho}} não foi encontrado. Tente novamente.")

caminho_padrao = r"C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe"
print(f"\nPressione ENTER para usar o caminho padrão: {caminho_padrao}")
caminho_ansysedt = obter_caminho_valido("Ou digite o caminho correto (ex: C:\\...\\ansysedt.exe): ", default=caminho_padrao)

comando = f'"{caminho_ansysedt}" -runscript "{caminho_script_hfss}"'

print("\nIniciando o Ansys Electronics Desktop... Aguarde enquanto as geometrias são geradas.")
subprocess.Popen(comando, shell=True)

time.sleep(5)
print("Comando enviado com sucesso! Verifique a janela do Ansys que acabou de abrir.")