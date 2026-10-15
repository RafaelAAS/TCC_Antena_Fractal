import subprocess
import time
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_script_hfss = os.path.join(diretorio_atual, "script_interno_hfss.py")
caminho_projeto = os.path.join(diretorio_atual, "Antena_Fractal_Leitor_RFID.aedt")
caminho_projeto_com_duplas = caminho_projeto.replace("\\", "\\\\")

codigo_hfss = f"""# -*- coding: utf-8 -*-
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "Iteracao_0", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("Iteracao_0")
oEditor = oDesign.SetActiveEditor("3D Modeler")

# 1. Novas Variaveis do Artigo
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
                    "Value:=", "80mm"
                ],
                [
                    "NAME:h",
                    "PropType:=", "VariableProp",
                    "UserDef:=", True,
                    "Value:=", "1.6mm"
                ]
            ]
        ]
    ])

# 2. Desenhando o Substrato Rígido (FR-4)
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
        "MaterialValue:=", "\\"FR4_epoxy\\"",
        "SurfaceMaterialValue:=", "\\"\\"",
        "SolveInside:=", True,
        "IsMaterialEditable:=", True,
        "UseMaterialAppearance:=", False
    ])

# O Plano de Terra inferior (Z=0) foi totalmente removido para acomodar a topologia CPW.

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
            print(f"\\nO caminho {{caminho}} não foi encontrado. Tente novamente.")

caminho_padrao = r"C:\Program Files\AnsysEM\Ansys Student\v252\Win64\ansysedt.exe"
print(f"\nPressione ENTER para usar o caminho padrão: {caminho_padrao}")
caminho_ansysedt = obter_caminho_valido("Ou digite o caminho correto: ", default=caminho_padrao)

comando = f'"{caminho_ansysedt}" -runscript "{caminho_script_hfss}"'
print("\nIniciando o Ansys Electronics Desktop... Aguarde a geracao da nova base.")
subprocess.Popen(comando, shell=True)

time.sleep(5)