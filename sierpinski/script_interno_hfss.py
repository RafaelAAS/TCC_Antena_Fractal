# -*- coding: utf-8 -*-
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
                ["NAME:W_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "23.2mm"],
                ["NAME:L_sub", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "24.9mm"],
                ["NAME:L", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "4.8mm"],
                ["NAME:Ratio_R", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.577"],
                ["NAME:W", "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "Ratio_R*L"]
            ]
        ]
    ])

# 2. Material
oDefinitionManager = oProject.GetDefinitionManager()
oDefinitionManager.AddMaterial(["NAME:epoxy_Kevlar", "CoordinateSystemType:=", "Cartesian", "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]], "permittivity:=", "3.6", "dielectric_loss_tangent:=", "0"])

# 3. Substrato
oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", "-11.6mm", "YPosition:=", "0mm", "ZPosition:=", "0mm", "XSize:=", "23.2mm", "YSize:=", "24.9mm", "ZSize:=", "1mm"], ["NAME:Attributes", "Name:=", "Substrato", "Flags:=", "", "Color:=", "(0 255 0)", "Transparency:=", 0.5, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"epoxy_Kevlar\"", "SolveInside:=", True])

# 4. Plano de Terra no VERSO (Z=0mm)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-11.6mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "23.2mm", "Height:=", "3mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Plano_de_Terra", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oModule_Bound.AssignPerfectE(["NAME:GND_PerfectE", "Objects:=", ["Plano_de_Terra"], "InfGroundPlane:=", False])

# 5. Triangulo base no TOPO (Z=H). Vertice inferior em Y=4mm; base superior em Y=4mm+4*L
oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "0mm", "Y:=", "4mm", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "4*W", "Y:=", "4mm + 4*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-4*W", "Y:=", "4mm + 4*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "0mm", "Y:=", "4mm", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Patch_Principal", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])

# 6. Recortes do fractal

oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "2.0*W", "Y:=", "4mm + 2.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "0mm", "Y:=", "4mm + 4.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-2.0*W", "Y:=", "4mm + 2.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "2.0*W", "Y:=", "4mm + 2.0*L", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Cutout_1", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])

oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "1.0*W", "Y:=", "4mm + 1.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "0mm", "Y:=", "4mm + 2.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-1.0*W", "Y:=", "4mm + 1.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "1.0*W", "Y:=", "4mm + 1.0*L", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Cutout_2", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])

oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "3.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "2.0*W", "Y:=", "4mm + 4.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "1.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "3.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Cutout_3", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])

oEditor.CreatePolyline(["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", True, ["NAME:PolylinePoints", ["NAME:PLPoint", "X:=", "-1.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-2.0*W", "Y:=", "4mm + 4.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-3.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"], ["NAME:PLPoint", "X:=", "-1.0*W", "Y:=", "4mm + 3.0*L", "Z:=", "1mm"]], ["NAME:PolylineSegments", ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 0, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 1, "NoOfPoints:=", 2], ["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", 2, "NoOfPoints:=", 2]]], ["NAME:Attributes", "Name:=", "Cutout_4", "Flags:=", "", "Color:=", "(255 255 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])


oEditor.Subtract(["NAME:Selections", "Blank Parts:=", "Patch_Principal", "Tool Parts:=", "Cutout_1,Cutout_2,Cutout_3,Cutout_4"], ["NAME:SubtractParameters", "KeepOriginals:=", False])


# 7. Circuito de casamento no TOPO (valores da Tabela 1 do artigo)
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-0.5mm", "YStart:=", "0mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "5mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Left", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "0.5mm", "YStart:=", "4mm", "ZStart:=", "1mm", "Width:=", "5.2mm", "Height:=", "1mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Top", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "0mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "2.1mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Right_Bottom", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "3.6mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "1.7mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Loop_Right_Top", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])

# Unificando o cobre do TOPO
oEditor.Unite(["NAME:Selections", "Selections:=", "Patch_Principal,Loop_Left,Loop_Top,Loop_Right_Bottom,Loop_Right_Top"], ["NAME:UniteParameters", "KeepOriginals:=", False])
oModule_Bound.AssignPerfectE(["NAME:Patch_PerfectE", "Objects:=", ["Patch_Principal"], "InfGroundPlane:=", False])

# 8. VIAS verticais conectando o laco ao terra
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "-0.5mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "1mm", "Height:=", "1mm", "WhichAxis:=", "Y"], ["NAME:Attributes", "Name:=", "Via_Left", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "0mm", "ZStart:=", "0mm", "Width:=", "1mm", "Height:=", "1mm", "WhichAxis:=", "Y"], ["NAME:Attributes", "Name:=", "Via_Right", "Flags:=", "", "Color:=", "(255 128 0)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oModule_Bound.AssignPerfectE(["NAME:ViaLeft_E", "Objects:=", ["Via_Left"], "InfGroundPlane:=", False])
oModule_Bound.AssignPerfectE(["NAME:ViaRight_E", "Objects:=", ["Via_Right"], "InfGroundPlane:=", False])

# 9. Porta de excitacao no gap da perna direita.
#    Referencia PADRAO de 50 ohm (renormalizada). A comparacao com o chip (30-j200) e feita
#    no pos-processamento, a partir de Z(1,1), que independe da referencia da porta.
oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", "5.7mm", "YStart:=", "2.1mm", "ZStart:=", "1mm", "Width:=", "1mm", "Height:=", "1.5mm", "WhichAxis:=", "Z"], ["NAME:Attributes", "Name:=", "Port_Sheet", "Flags:=", "", "Color:=", "(0 0 255)", "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True])
oModule_Bound.AssignLumpedPort(["NAME:Port1", "Objects:=", ["Port_Sheet"], "DoDeembed:=", False, "RenormalizeAllTerminals:=", True, ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True, ["NAME:IntLine", "Start:=", ["6.2mm", "2.1mm", "1mm"], "End:=", ["6.2mm", "3.6mm", "1mm"]], "AlignmentGroup:=", 0, "CharImp:=", "Zpi", "RenormImp:=", "50ohm"]], "ShowPredefinedFieldOnPolygons:=", True])

# Seguranca: se o Subtract tiver gerado folhas extras (triangulos separados), elas tambem sao PEC
folhas_extras = [n for n in oEditor.GetObjectsInGroup("Sheets") if n not in ("Plano_de_Terra", "Patch_Principal", "Via_Left", "Via_Right", "Port_Sheet")]
if len(folhas_extras) > 0:
    oModule_Bound.AssignPerfectE(["NAME:PEC_Extras", "Objects:=", folhas_extras, "InfGroundPlane:=", False])
    oDesktop.AddMessage("", "", 1, "Subtract gerou folhas extras (PEC atribuido): " + ",".join(folhas_extras))

# 10. Caixa de Radiacao (margem >= lambda/4 em 2,45 GHz)
oEditor.CreateBox(
    ["NAME:BoxParameters", "XPosition:=", "-46.6mm", "YPosition:=", "-35mm", "ZPosition:=", "-35mm", "XSize:=", "93.2mm", "YSize:=", "94.9mm", "ZSize:=", "71mm"],
    ["NAME:Attributes", "Name:=", "AirBox", "Flags:=", "", "Color:=", "(0 255 255)", "Transparency:=", 0.9, "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\"vacuum\"", "SolveInside:=", True]
)
oModule_Bound.AssignRadiation(["NAME:Radiation1", "Objects:=", ["AirBox"], "IsFssReference:=", False, "IsIncidentField:=", False])

# 11. Esfera Infinita de Campo Distante (ganho e diagrama de radiacao em 2,45 GHz)
oModule_Rad = oDesign.GetModule("RadField")
oModule_Rad.InsertInfiniteSphereSetup([
    "NAME:Infinite Sphere1",
    "UseCustomRadiationSurface:=", False,
    "CSDefinition:=", "Theta-Phi",
    "Polarization:=", "Linear",
    "Boresight:=", "Z Axis",
    "ThetaStart:=", "0deg",
    "ThetaStop:=", "180deg",
    "ThetaStep:=", "2deg",
    "PhiStart:=", "-180deg",
    "PhiStop:=", "180deg",
    "PhiStep:=", "2deg",
    "UseLocalCS:=", False
])
oModule_Rad.InsertInfiniteSphereSetup([
    "NAME:Esfera_2D",
    "UseCustomRadiationSurface:=", False,
    "CSDefinition:=", "Theta-Phi",
    "Polarization:=", "Linear",
    "Boresight:=", "Z Axis",
    "ThetaStart:=", "-180deg",
    "ThetaStop:=", "180deg",
    "ThetaStep:=", "2deg",
    "PhiStart:=", "0deg",
    "PhiStop:=", "90deg",
    "PhiStep:=", "90deg",
    "UseLocalCS:=", False
])

# 12. Setup e varredura. Como |S11| a 50 ohm fica perto de 1, um erro pequeno em S vira erro
#     grande em Z; por isso MaxDeltaS menor e minimo de passes maior.
oModule_Setup = oDesign.GetModule("AnalysisSetup")
oModule_Setup.InsertSetup("HfssDriven",
    ["NAME:Setup1", "Frequency:=", "2.45GHz", "PortsOnly:=", False, "MaxDeltaS:=", 0.01, "UseMatrixConv:=", False, "MaximumPasses:=", 15, "MinimumPasses:=", 3, "MinimumConvergedPasses:=", 2]
)
oModule_Setup.InsertFrequencySweep("Setup1",
    ["NAME:Sweep1", "Type:=", "Interpolating", "IsEnabled:=", True, "RangeType:=", "LinearStep", "RangeStart:=", "1.5GHz", "RangeEnd:=", "4.0GHz", "RangeStep:=", "0.01GHz", "SaveFields:=", False, "SaveRadFields:=", False]
)

# 13. Relatorios (aparecem em Results depois do Analyze All). Se falhar, crie a mao (ver aviso).
try:
    oModule_Out = oDesign.GetModule("OutputVariable")
    oModule_Out.CreateOutputVariable("S11_chip", "(Z(Port1,Port1)-cmplx(30.0,200.0))/(Z(Port1,Port1)+cmplx(30.0,-200.0))", "Setup1 : Sweep1", "Modal Solution Data", [])
    oModule_Rep = oDesign.GetModule("ReportSetup")
    oModule_Rep.CreateReport("Z_entrada", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["re(Z(Port1,Port1))", "im(Z(Port1,Port1))"]], [])
    oModule_Rep.CreateReport("S11_chip", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["dB(S11_chip)"]], [])
    oModule_Rep.CreateReport("S11_50ohm", "Modal Solution Data", "Rectangular Plot", "Setup1 : Sweep1", ["Domain:=", "Sweep"], ["Freq:=", ["All"]], ["X Component:=", "Freq", "Y Component:=", ["dB(S(Port1,Port1))"]], [])
    oModule_Rep.CreateReport("Ganho_3D", "Far Fields", "3D Polar Plot", "Setup1 : LastAdaptive", ["Context:=", "Infinite Sphere1"], ["Phi:=", ["All"], "Theta:=", ["All"], "Freq:=", ["2.45GHz"]], ["Phi Component:=", "Phi", "Theta Component:=", "Theta", "Mag Component:=", ["dB(GainTotal)"]], [])
    oModule_Rep.CreateReport("Diagrama_2D_Planos", "Far Fields", "Radiation Pattern", "Setup1 : LastAdaptive", ["Context:=", "Esfera_2D"], ["Theta:=", ["All"], "Phi:=", ["0deg", "90deg"], "Freq:=", ["2.45GHz"]], ["Ang Component:=", "Theta", "Mag Component:=", ["dB(GainTotal)"]], [])
    oModule_Rep.CreateReport("Diagrama_2D_XY", "Far Fields", "Radiation Pattern", "Setup1 : LastAdaptive", ["Context:=", "Infinite Sphere1"], ["Phi:=", ["All"], "Theta:=", ["90deg"], "Freq:=", ["2.45GHz"]], ["Ang Component:=", "Phi", "Mag Component:=", ["dB(GainTotal)"]], [])
except Exception as erro:
    oDesktop.AddMessage("", "", 1, "Relatorios nao criados automaticamente (" + str(erro) + "). Crie a mao: re/im(Z(Port1,Port1)) e dB(S11_chip).")

oEditor.FitAll()
oProject.SaveAs("C:\\Users\\rafae\\TCC_Antena_Fractal\\sierpinski\\Antena_Fractal_SFMA_v2.aedt", True)
