# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2016 EDF S.A.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Actions Handler
===============

Creates menu, actions, and separators for the SALOME Desktop.
"""

#-------------------------------------------------------------------------------
# Standard modules
#-------------------------------------------------------------------------------

import os, string, shutil
import subprocess
import re
import logging

#-------------------------------------------------------------------------------
# Third-party modules
#-------------------------------------------------------------------------------
from code_saturne.Base.QtCore    import *
from code_saturne.Base.QtGui     import *
from code_saturne.Base.QtWidgets import *
from code_saturne.Base import QtPage
#-------------------------------------------------------------------------------
# Salome modules
#-------------------------------------------------------------------------------

import SALOMEDS #Si on veut changer de couleur...
import salome
import SMESH
from salome.smesh import smeshBuilder

#-------------------------------------------------------------------------------
# Application modules
#-------------------------------------------------------------------------------

import CFDSTUDYGUI_DialogCollector
import CFDSTUDYGUI_DataModel
import CFDSTUDYGUI_Commons
import CFDSTUDYGUI_CommandMgr
from CFDSTUDYGUI_Agents import *
from CFDSTUDYGUI_Commons import _SetCFDCode, CFD_Code, BinCode, CFD_Saturne
from CFDSTUDYGUI_Commons import CFD_Neptune, sgPyQt, sg, CheckCFD_CodeEnv
import CFDSTUDYGUI_SolverGUI
from CFDSTUDYGUI_Message import cfdstudyMess
#-------------------------------------------------------------------------------
# log config
#-------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger("CFDSTUDYGUI_ActionsHandler")
log.setLevel(logging.NOTSET)
#-------------------------------------------------------------------------------
# Global definitions
#-------------------------------------------------------------------------------

# Actions
SetStudyAction                = 1
AddCaseAction                 = 2
LaunchGUIAction               = 4
OpenGUIAction                 = 5
UpdateObjBrowserAction        = 6
InfoCFDSTUDYAction            = 7
OpenAnExistingCase            = 8

#common actions
RemoveAction                  = 20
ViewAction                    = 21
EditAction                    = 22
MoveToDRAFTAction             = 23
CopyInDATAAction              = 24
CopyInSRCAction               = 25
CopyCaseFileAction            = 26
CloseStudyAction              = 27

#export/convert actions
ExportInParaViSAction         = 40
ExportInSMESHAction           = 41
ConvertMeshToMed              = 42

#other actions
CheckCompilationAction        = 50
RunScriptAction               = 51

#Display Actions
DisplayMESHAction              = 60
DisplayGroupMESHAction         = 61
DisplayOnlyGroupMESHAction     = 62
HideGroupMESHAction            = 63
HideMESHAction                 = 64

DisplayTypeMenu                = 70
DisplayTypePOINT               = 71
DisplayTypeWIREFRAME           = 72
DisplayTypeSHADED              = 74
DisplayTypeINSIDEFRAME         = 75
DisplayTypeSURFACEFRAME        = 76
DisplayTypeFEATURE_EDGES       = 77
DisplayTypeSHRINK              = 78

#=====SOLVER ACTIONS
#Common Actions
SolverFileMenu                 = 100
SolverSaveAction               = 101
SolverSaveAsAction             = 102
SolverCloseAction              = 103
SolverUndoAction               = 104
SolverRedoAction               = 105
SolverPreproModeAction         = 106
SolverCalculationModeAction    = 107

SolverToolsMenu                = 110
SolverOpenShellAction          = 111
SolverDisplayCurrentCaseAction = 112

SolverHelpMenu                 = 130
SolverHelpAboutAction          = 131

#Help menu
SolverHelpLicense              = 251
SolverHelpGuidesMenu           = 260
SolverHelpUserGuide            = 261
SolverHelpTutorial             = 262
SolverHelpTheory               = 263
SolverHelpRefcard              = 264
SolverHelpDoxygen              = 265
NCSolverHelpUserGuide          = 266
NCSolverHelpTutorial           = 267
NCSolverHelpTheory             = 268
NCSolverHelpDoxygen            = 269

# ObjectTR is a convenient object for traduction purpose

ObjectTR = QObject()

#-------------------------------------------------------------------------------
# Classes definition
#-------------------------------------------------------------------------------

class ActionError(Exception):
    """
    New exception definition.
    """
    def __init__(self, value):
        """
        Constructor.
        """
        self.value = value

    def __str__(self):
        """
        String representation of the attribute I{self.value}.
        """
        return repr(self.value)


class CFDSTUDYGUI_ActionsHandler(QObject):
    def __init__(self):
        """
        Constructor.
        """
        log.debug("__init__")
        QObject.__init__(self, None)

        self.l_color = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),]
        self.ul_color = []
        #intialise all dialogs
        self.DialogCollector = CFDSTUDYGUI_DialogCollector.CFDSTUDYGUI_DialogCollector()

        self._ActionMap = {}
        self._CommonActionIdMap = {}
        self._SolverActionIdMap = {}
        self._HelpActionIdMap = {}

        self._SalomeSelection = sgPyQt.getSelection()
        self._SolverGUI = CFDSTUDYGUI_SolverGUI.CFDSTUDYGUI_SolverGUI()
        self._DskAgent = Desktop_Agent()

    def createActions(self):
        """
        Creates menu, actions, and separators.
        """
        log.debug("createActions")
        menu_id = sgPyQt.createMenu(ObjectTR.tr("CFDSTUDY_MENU"),\
                                     -1,\
                                     -1,\
                                     10)
        tool_id = sgPyQt.createTool(ObjectTR.tr("CFDSTUDY_TOOL_BAR"))

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("SET_CFDSTUDY_STUDY_TEXT"),\
                                      ObjectTR.tr("SET_CFDSTUDY_STUDY_TIP"),\
                                      ObjectTR.tr("SET_CFDSTUDY_STUDY_SB"),\
                                      ObjectTR.tr("SET_CFDSTUDY_STUDY_ICON"))
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[SetStudyAction] = action_id
        action.triggered.connect(self.slotStudyLocation)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("ADD_CFDSTUDY_CASE_TEXT"),\
                                      ObjectTR.tr("ADD_CFDSTUDY_CASE_TIP"),\
                                      ObjectTR.tr("ADD_CFDSTUDY_CASE_SB"),\
                                      ObjectTR.tr("ADD_CFDSTUDY_CASE_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[AddCaseAction] = action_id
        action.triggered.connect(self.slotAddCase)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TEXT"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TIP"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_SB"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_ICON"))
        # popup open GUI on CFD CASE with slotLaunchGUI
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[LaunchGUIAction] = action_id
        action.triggered.connect(self.slotLaunchGUI)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("OPEN_CFDSTUDY_GUI_TEXT"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_TIP"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_SB"),\
                                      ObjectTR.tr("LAUNCH_CFDSTUDY_GUI_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[OpenGUIAction] = action_id
        action.triggered.connect(self.slotOpenCFD_GUI)

        # Open An Existing Case with a Menu button
        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("OPEN_EXISTING_CASE_GUI_TEXT"),\
                                      ObjectTR.tr("OPEN_EXISTING_CASE_GUI_TIP"),\
                                      ObjectTR.tr("OPEN_EXISTING_CASE_GUI_SB"),\
                                      ObjectTR.tr("OPENEXISTINGCASEFILEXML_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[OpenAnExistingCase] = action_id
        action.triggered.connect(self.slotOpenAnExistingCaseFileFromMenu)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)
        sgPyQt.createTool(action, tool_id)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("UPDATE_CFDSTUDY_OBJBROWSER_TEXT"),\
                                      ObjectTR.tr("UPDATE_CFDSTUDY_OBJBROWSER_TIP"),\
                                      ObjectTR.tr("UPDATE_CFDSTUDY_OBJBROWSER_SB"),\
                                      ObjectTR.tr("UPDATE_CFDSTUDY_OBJBROWSER_ICON"))
        sgPyQt.createMenu(action, menu_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[UpdateObjBrowserAction] = action_id
        action.triggered.connect(self.slotUpdateObjectBrowser)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("INFO_CFDSTUDY_TEXT"),\
                                      ObjectTR.tr("INFO_CFDSTUDY_TIP"),\
                                      ObjectTR.tr("INFO_CFDSTUDY_SB"),\
                                      ObjectTR.tr("INFO_CFDSTUDY_ICON"))
        sgPyQt.createMenu(action, menu_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[InfoCFDSTUDYAction] = action_id
        action.triggered.connect(self.slotInfo)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("REMOVE_ACTION_TEXT"),\
                                      ObjectTR.tr("REMOVE_ACTION_TIP"),\
                                      ObjectTR.tr("REMOVE_ACTION_SB"),\
                                      ObjectTR.tr("REMOVE_ACTION_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[RemoveAction] = action_id
        action.triggered.connect(self.slotRemoveAction)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("CLOSE_ACTION_TEXT"),\
                                      ObjectTR.tr("CLOSE_ACTION_TIP"),\
                                      ObjectTR.tr("CLOSE_ACTION_SB"),\
                                      ObjectTR.tr("CLOSE_ACTION_ICON"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CloseStudyAction] = action_id
        action.triggered.connect(self.slotCloseStudyAction)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("VIEW_ACTION_TEXT"),\
                                      ObjectTR.tr("VIEW_ACTION_TIP"),\
                                      ObjectTR.tr("VIEW_ACTION_SB"),\
                                      ObjectTR.tr("VIEW_ACTION_ICON"))
        action.triggered.connect(self.slotViewAction)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ViewAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("EDIT_ACTION_TEXT"),\
                                      ObjectTR.tr("EDIT_ACTION_TIP"),\
                                      ObjectTR.tr("EDIT_ACTION_SB"),\
                                      ObjectTR.tr("EDIT_ACTION_ICON"))
        action.triggered.connect(self.slotEditAction)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[EditAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("MOVE_TO_DRAFT_ACTION_TEXT"),\
                                      ObjectTR.tr("MOVE_TO_DRAFT_ACTION_TIP"),\
                                      ObjectTR.tr("MOVE_TO_DRAFT_ACTION_SB"),\
                                      ObjectTR.tr("MOVE_ACTION_ICON"))
        action.triggered.connect(self.slotMoveToDRAFT)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[MoveToDRAFTAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("COPY_IN_DATA_ACTION_TEXT"),\
                                      ObjectTR.tr("COPY_IN_DATA_ACTION_TIP"),\
                                      ObjectTR.tr("COPY_IN_DATA_ACTION_SB"),\
                                      ObjectTR.tr("COPY_ACTION_ICON"))
        action.triggered.connect(self.slotCopyInDATA)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CopyInDATAAction] = action_id

        action = sgPyQt.createAction(-1,\
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_TEXT"),\
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_TIP"),\
                                     ObjectTR.tr("COPY_IN_SRC_ACTION_SB"),\
                                     ObjectTR.tr("COPY_ACTION_ICON"))
        action.triggered.connect(self.slotCopyInSRC)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CopyInSRCAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("COPY_CASE_FILE_ACTION_TEXT"),\
                                      ObjectTR.tr("COPY_CASE_FILE_ACTION_TIP"),\
                                      ObjectTR.tr("COPY_CASE_FILE_ACTION_SB"),\
                                      ObjectTR.tr("COPY_ACTION_ICON"))
        action.triggered.connect(self.slotCopyCaseFile)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CopyCaseFileAction] = action_id

        #export/convert actions
        action = sgPyQt.createAction(-1,
                                      ObjectTR.tr("EXPORT_IN_PARAVIS_ACTION_TEXT"),
                                      ObjectTR.tr("EXPORT_IN_PARAVIS_ACTION_TIP"),
                                      ObjectTR.tr("EXPORT_IN_PARAVIS_ACTION_SB"),
                                      ObjectTR.tr("EXPORT_IN_PARAVIS_ACTION_ICON"))
        action.triggered.connect(self.slotExportInParavis)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ExportInParaViSAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("EXPORT_IN_SMESH_ACTION_TEXT"),\
                                      ObjectTR.tr("EXPORT_IN_SMESH_ACTION_TIP"),\
                                      ObjectTR.tr("EXPORT_IN_SMESH_ACTION_SB"),\
                                      ObjectTR.tr("EXPORT_IN_SMESH_ACTION_ICON"))
        action.triggered.connect(self.slotExportInSMESH)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ExportInSMESHAction] = action_id

# popup added to vizualise the mesh. It is not necessary to switch into SMESH Component

        action = sgPyQt.createAction(-1,\
                                      "Display mesh",\
                                      "Display mesh",\
                                      "Display mesh",\
                                      ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotDisplayMESH)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[DisplayMESHAction] = action_id

# popup added to hide the mesh.

        action = sgPyQt.createAction(-1,\
                                      "Hide mesh",\
                                      "Hide mesh",\
                                      "Hide mesh",\
                                      ObjectTR.tr("MESH_OBJ_ICON"))
        action.triggered.connect(self.slotHideMESH)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[HideMESHAction] = action_id

# popup added to vizualise the mesh groups. It is not necessary to switch into SMESH Component

        action = sgPyQt.createAction(-1,\
                                      "Display",\
                                      "Display",\
                                      "Display",\
                                      ObjectTR.tr("MESH_TREE_OBJ_ICON"))
        action.triggered.connect(self.slotDisplayMESHGroups)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[DisplayGroupMESHAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      "Display only",\
                                      "Display only",\
                                      "Display only",\
                                      ObjectTR.tr("MESH_TREE_OBJ_ICON"))
        action.triggered.connect(self.slotDisplayOnlyMESHGroups)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[DisplayOnlyGroupMESHAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      "Hide",\
                                      "Hide",\
                                      "Hide",\
                                      ObjectTR.tr("MESH_TREE_OBJ_ICON"))
        action.triggered.connect(self.slotHideMESHGroups)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[HideGroupMESHAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("ECS_CONVERT_ACTION_TEXT"),\
                                      ObjectTR.tr("ECS_CONVERT_ACTION_TIP"),\
                                      ObjectTR.tr("ECS_CONVERT_ACTION_SB"),\
                                      ObjectTR.tr("ECS_CONVERT_ACTION_ICON"))
        action.triggered.connect(self.slotMeshConvertToMed)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[ConvertMeshToMed] = action_id

        #other actions
        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("CHECK_COMPILATION_ACTION_TEXT"),\
                                      ObjectTR.tr("CHECK_COMPILATION_ACTION_TIP"),\
                                      ObjectTR.tr("CHECK_COMPILATION_ACTION_SB"),\
                                      ObjectTR.tr("CHECK_COMPILATION_ACTION_ICON"))
        action.triggered.connect(self.slotCheckCompilation)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[CheckCompilationAction] = action_id

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("RUN_SCRIPT_ACTION_TEXT"),\
                                      ObjectTR.tr("RUN_SCRIPT_ACTION_TIP"),\
                                      ObjectTR.tr("RUN_SCRIPT_ACTION_SB"),\
                                      ObjectTR.tr("RUN_SCRIPT_ACTION_ICON"))
        action.triggered.connect(self.slotRunScript)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._CommonActionIdMap[RunScriptAction] = action_id

        # Solver actions

        # File menu
        # find the menu File into the Main Menu Bar of Salome
        fileId = sgPyQt.createMenu( ObjectTR.tr("MEN_DESK_FILE"), -1, -1)

        # create my menu into  menu File at position 7
        action_id = sgPyQt.createMenu(ObjectTR.tr("SOLVER_FILE_MENU_TEXT"), fileId, -1, 7, 1)
        self._SolverActionIdMap[SolverFileMenu] = action_id

        # warning: a Separator is a QMenu item (a trait)
        # create a separator after my menu in position 8
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, fileId, -1, 8, 1)

        # Save action
        action = sgPyQt.createAction(SolverSaveAction,\
                                      ObjectTR.tr("SOLVER_SAVE_ACTION_TEXT"),\
                                      ObjectTR.tr("SOLVER_SAVE_ACTION_TIP"),\
                                      ObjectTR.tr("SOLVER_SAVE_ACTION_SB"),\
                                      ObjectTR.tr("SOLVER_SAVE_ACTION_ICON"),
                                      Qt.SHIFT+Qt.CTRL+Qt.Key_S)
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverFileMenu], 100)
        action.triggered.connect(self.slotSaveDataFile)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverSaveAction] = action_id

        # Save As action
        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("SOLVER_SAVEAS_ACTION_TEXT"),\
                                      ObjectTR.tr("SOLVER_SAVEAS_ACTION_TIP"),\
                                      ObjectTR.tr("SOLVER_SAVEAS_ACTION_SB"),\
                                      ObjectTR.tr("SOLVER_SAVEAS_ACTION_ICON"),
                                      Qt.SHIFT+Qt.CTRL+Qt.Key_A)
        sgPyQt.createTool(action, tool_id)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverFileMenu], 100)
        action.triggered.connect(self.slotSaveAsDataFile)

        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverSaveAsAction] = action_id
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, 1, 0, 2)

        # close GUI action
        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("CLOSE_CFD_GUI_ACTION_TEXT"),\
                                      ObjectTR.tr("CLOSE_CFD_GUI_ACTION_TIP"),\
                                      ObjectTR.tr("CLOSE_CFD_GUI_ACTION_SB"),\
                                      ObjectTR.tr("CLOSE_CFD_GUI_ACTION_ICON"),
                                      Qt.SHIFT+Qt.CTRL+Qt.Key_W)
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverCloseAction] = action_id
        action.triggered.connect(self.slotCloseCFD_GUI)

        # Add separator
        action = sgPyQt.createSeparator()
        sgPyQt.createTool(action, tool_id)

        # Undo action
        action = sgPyQt.createAction(-1, "Undo", "Undo", "Undo", \
                                      ObjectTR.tr("UNDO_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverUndoAction] = action_id
        action.triggered.connect(self.slotUndo)

        # Redo action
        action = sgPyQt.createAction(-1, "Redo", "Redo", "Redo", \
                                      ObjectTR.tr("REDO_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverRedoAction] = action_id
        action.triggered.connect(self.slotRedo)

        # Preprocessing Mode action
        action = sgPyQt.createAction(-1, "Preprocessing Mode", "Preprocessing Mode", "Preprocessing Mode", \
                                      ObjectTR.tr("PREPRO_MODE_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverPreproModeAction] = action_id
        action.triggered.connect(self.slotPreproMode)

        # Calculation Mode action
        action = sgPyQt.createAction(-1, "Calculation Mode", "Calculation Mode", "Calculation Mode", \
                                      ObjectTR.tr("CALCULATION_MODE_CFD_GUI_ACTION_ICON"))
        sgPyQt.createTool(action, tool_id)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverCalculationModeAction] = action_id
        action.triggered.connect(self.slotCalculationMode)

        # Tools Menu
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, menu_id, 0, -1)

        action_id = sgPyQt.createMenu(ObjectTR.tr("SOLVER_TOOLS_MENU_TEXT"), menu_id)
        self._SolverActionIdMap[SolverToolsMenu] = action_id

        # Open shell action
        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("SOLVER_OPENSHELL_ACTION_TEXT"),\
                                      ObjectTR.tr("SOLVER_OPENSHELL_ACTION_TIP"),\
                                      ObjectTR.tr("SOLVER_OPENSHELL_ACTION_SB"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverOpenShellAction] = action_id
        action.triggered.connect(self.slotOpenShell)

        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, SolverToolsMenu, 0, -1)

        action = sgPyQt.createAction(-1,\
                                      ObjectTR.tr("SOLVER_DISPLAYCASE_ACTION_TEXT"),\
                                      ObjectTR.tr("SOLVER_DISPLAYCASE_ACTION_TIP"),\
                                      ObjectTR.tr("SOLVER_DISPLAYCASE_ACTION_SB"))
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverDisplayCurrentCaseAction] = action_id
        action.triggered.connect(self.slotDisplayCurrentCase)

        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverToolsMenu])
        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, SolverToolsMenu, 0, -1)
        #for auto hide last separator in tools menu
        self._HelpActionIdMap[0] = action_id

        # Help menu: insert a Solver Menu Help to the Main Menu Help of Salome

        helpId = sgPyQt.createMenu( ObjectTR.tr("MEN_DESK_HELP"), -1, -1)
        #Info: Separator created at the end of the Menu Help (when we did not indicate a number)

        action = sgPyQt.createSeparator()
        sgPyQt.createMenu(action, helpId)
        #Info: Solver Help Menu created at the end of the Menu Help of Salome(when we did not indicate a number)
        action_id = sgPyQt.createMenu("CFD module", helpId)
        self._SolverActionIdMap[SolverHelpMenu] = action_id

        m = "About CFD"
        action = sgPyQt.createAction(-1, m, m, m)
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._SolverActionIdMap[SolverHelpAboutAction] = action_id
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverHelpMenu])
        action.triggered.connect(self.slotHelpAbout)
        self._ActionMap[action_id].setVisible(True)

        m = "License"
        action = sgPyQt.createAction(SolverHelpLicense, m, m, m)
        sgPyQt.createMenu(action, self._SolverActionIdMap[SolverHelpMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpLicense] = action_id
        action.triggered.connect(self.slotHelpLicense)

        # Guides menu
        action_id = sgPyQt.createMenu("Code_Saturne and NEPTUNE_CFD Guides", self._SolverActionIdMap[SolverHelpMenu])
        self._HelpActionIdMap[SolverHelpGuidesMenu] = action_id

        m = "Code_Saturne user guide"
        action = sgPyQt.createAction(SolverHelpUserGuide, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpUserGuide] = action_id
        action.triggered.connect(self.slotHelpUserGuide)

        m = "Code_Saturne tutorial"
        action = sgPyQt.createAction(SolverHelpTutorial, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpTutorial] = action_id
        action.triggered.connect(self.slotHelpTutorial)

        m = "Code_Saturne theoretical guide"
        action = sgPyQt.createAction(SolverHelpTheory, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpTheory] = action_id
        action.triggered.connect(self.slotHelpTheory)

        m = "Reference card"
        action = sgPyQt.createAction(SolverHelpRefcard, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpRefcard] = action_id
        action.triggered.connect(self.slotHelpRefcard)

        m = "Code_Saturne doxygen"
        action = sgPyQt.createAction(SolverHelpDoxygen, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[SolverHelpDoxygen] = action_id
        action.triggered.connect(self.slotHelpDoxygen)

        m = "NEPTUNE_CFD user guide"
        action = sgPyQt.createAction(NCSolverHelpUserGuide, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpUserGuide] = action_id
        action.triggered.connect(self.slotHelpNCUserGuide)

        m = "NEPTUNE_CFD tutorial"
        action = sgPyQt.createAction(NCSolverHelpTutorial, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpTutorial] = action_id
        action.triggered.connect(self.slotHelpNCTutorial)

        m = "NEPTUNE_CFD theoretical guide"
        action = sgPyQt.createAction(NCSolverHelpTheory, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpTheory] = action_id
        action.triggered.connect(self.slotHelpNCTheory)

        m = "NEPTUNE_CFD doxygen"
        action = sgPyQt.createAction(NCSolverHelpDoxygen, m, m, m)
        sgPyQt.createMenu(action, self._HelpActionIdMap[SolverHelpGuidesMenu])
        action_id = sgPyQt.actionId(action)
        self._ActionMap[action_id] = action
        self._HelpActionIdMap[NCSolverHelpDoxygen] = action_id
        action.triggered.connect(self.slotHelpNCDoxygen)

        self.updateActions()


    def updateActions(self):
        """
        Updates all action according with current selection and study states.
        This function connected to selection change signal.
        """
        log.debug("updateActions")
        component = CFDSTUDYGUI_DataModel._getComponent()
        if component == None:
            #disable all actions except Study Location
            for i in self._CommonActionIdMap:
                if not i == InfoCFDSTUDYAction:
                    if i == SetStudyAction or i == OpenAnExistingCase:
                        self.commonAction(i).setEnabled(True)
                    else:
                        self.commonAction(i).setEnabled(False)
        else:
            #enable all actions
            for i in self._CommonActionIdMap:
                if not i == InfoCFDSTUDYAction:
                    self.commonAction(i).setEnabled(True)

        # selection handler
        sobj = self._singleSelectedObject()
        if sobj == None : #multiple selection not authorized
            for i in self._CommonActionIdMap:
                if i != InfoCFDSTUDYAction:
                    if i == SetStudyAction or i == OpenAnExistingCase:
                        self.commonAction(i).setEnabled(True)
                    else:
                        self.commonAction(i).setEnabled(False)#multiple selection not authorized

        if sobj != None:
            isStudy = CFDSTUDYGUI_DataModel.checkType(sobj, CFDSTUDYGUI_DataModel.dict_object["Study"])
            self.commonAction(AddCaseAction).setEnabled(isStudy)
            aStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(sobj)
            aCase = CFDSTUDYGUI_DataModel.GetCase(sobj)

            if aCase != None:
                code = CFDSTUDYGUI_DataModel.checkCode(aCase)
                _SetCFDCode(code)
                dialog = self.DialogCollector.InfoDialog
                dialog.update(code)

            if aStudy != None and aCase != None:
                self.commonAction(LaunchGUIAction).setEnabled(CFDSTUDYGUI_DataModel.checkCaseLaunchGUI(aCase))
                self.commonAction(OpenGUIAction).setEnabled(CFDSTUDYGUI_DataModel.checkCaseLaunchGUI(aCase))
            else:
                self.commonAction(LaunchGUIAction).setEnabled(False)
        else:
            self.commonAction(AddCaseAction).setEnabled(False)
        #enable / disable solver actions
        isActivatedView = self._SolverGUI.isActive() # Main GUI Window is active

        for a in self._SolverActionIdMap:
            if a != SolverFileMenu and a != SolverToolsMenu and a != SolverHelpMenu:
                self.solverAction(a).setEnabled(isActivatedView)

        try:
            from nc_package import package
        except:
            self.solverAction(NCSolverHelpUserGuide).setEnabled(False)
            self.solverAction(NCSolverHelpTutorial).setEnabled(False)
            self.solverAction(NCSolverHelpTheory).setEnabled(False)
            self.solverAction(NCSolverHelpDoxygen).setEnabled(False)

        if sobj != None:
            self.updateActionsXmlFile(sobj)


    def updateActionsXmlFile(self, XMLSobj) :

        if XMLSobj != None:
            if CFDSTUDYGUI_DataModel.checkType(XMLSobj, CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]):
                self.solverAction(SolverCloseAction).setEnabled(False)
                self.solverAction(SolverSaveAction).setEnabled(False)
                self.solverAction(SolverSaveAsAction).setEnabled(False)
                self.solverAction(SolverUndoAction).setEnabled(False)
                self.solverAction(SolverRedoAction).setEnabled(False)
                self.solverAction(SolverPreproModeAction).setEnabled(False)
                self.solverAction(SolverCalculationModeAction).setEnabled(False)

                case   = CFDSTUDYGUI_DataModel.GetCase(XMLSobj)
                study  = CFDSTUDYGUI_DataModel.GetStudyByObj(XMLSobj)
                if case != None and study != None:

                    if CFDSTUDYGUI_SolverGUI._c_CFDGUI.findDock(XMLSobj.GetName(), case.GetName(),study.GetName()):
                        self.solverAction(SolverCloseAction).setEnabled(True)
                        self.commonAction(OpenGUIAction).setEnabled(False)
                        self.solverAction(SolverSaveAction).setEnabled(True)
                        self.solverAction(SolverSaveAsAction).setEnabled(True)
                        self.solverAction(SolverUndoAction).setEnabled(True)
                        self.solverAction(SolverRedoAction).setEnabled(True)
                        self.solverAction(SolverPreproModeAction).setEnabled(True)
                        self.solverAction(SolverCalculationModeAction).setEnabled(True)

    def customPopup(self, id, popup):
        """
        Callback for fill popup menu according current selection state.
        Function called by C{createPopupMenu} from CFDSTUDYGUI.py

        @type id: C{int}
        @param id: type of the branch tree slected in the Object Brower.
        @type popup: C{QPopupMenu}
        @param popup: popup menu from the Object Browser.
        """
        log.debug("customPopup")
        if id == CFDSTUDYGUI_DataModel.dict_object["Study"]:
            popup.addAction(self.commonAction(AddCaseAction))
            popup.addAction(self.commonAction(UpdateObjBrowserAction))
            popup.addAction(self.commonAction(CloseStudyAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["Case"]:
            popup.addAction(self.commonAction(LaunchGUIAction))
            popup.addAction(self.commonAction(RemoveAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(MoveToDRAFTAction))
#            popup.addAction(self.commonAction(CopyCaseFileAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATADRAFTFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(CopyInDATAAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["REFERENCEDATAFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(CopyInDATAAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATALaunch"]:
            popup.addAction(self.commonAction(LaunchGUIAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]:
            popup.addAction(self.commonAction(OpenGUIAction))
            popup.addAction(self.solverAction(SolverCloseAction))
#            popup.addAction(self.commonAction(CopyCaseFileAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SRCFolder"]:
            popup.addAction(self.commonAction(CheckCompilationAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SRCFile"]:
            popup.addAction(self.commonAction(CheckCompilationAction))
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(MoveToDRAFTAction))
#            popup.addAction(self.commonAction(CopyCaseFileAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SRCDRAFTFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RemoveAction))
            popup.addAction(self.commonAction(CopyInSRCAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["LOGSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["USRSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(CopyInSRCAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUSubFolder"]:
            popup.addAction(self.commonAction(RemoveAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESUSubErrFolder"]:
            popup.addAction(self.commonAction(RemoveAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESSRCFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["HISTFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(ExportInParaViSAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["RESMEDFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["RESENSIGHTFile"]:
            popup.addAction(self.commonAction(ExportInParaViSAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SCRPTLanceFile"]:
            popup.addAction(self.commonAction(ViewAction))
            popup.addAction(self.commonAction(RunScriptAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SCRPTScriptFile"]:
            popup.addAction(self.commonAction(EditAction))
            popup.addAction(self.commonAction(RunScriptAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["SCRPTFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DESFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["CGNSFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["GeomFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["CaseFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["NeuFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["MSHFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["HexFile"] \
             or id == CFDSTUDYGUI_DataModel.dict_object["UnvFile"]:
            popup.addAction(self.commonAction(ConvertMeshToMed))
        elif id == CFDSTUDYGUI_DataModel.dict_object["MEDFile"]:
            popup.addAction(self.commonAction(ExportInSMESHAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["MESHFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["DATFile"]:
            popup.addAction(self.commonAction(EditAction))
        elif id == CFDSTUDYGUI_DataModel.dict_object["POSTFile"]:
            popup.addAction(self.commonAction(ViewAction))
        elif id == "VTKViewer":
            popup.addAction(self.commonAction(DisplayTypeSHADED))
            popup.addAction(self.commonAction(DisplayTypeWIREFRAME))
        else:

            for sobj in self._multipleSelectedObject():
                if sobj != None:
                    if sobj.GetFatherComponent().GetName() == "Mesh":
                        if sobj.GetFather().GetName() == "Mesh":
                            #Comment: mesh under Mesh module root in the Object browser

                            CFDSTUDYGUI_DataModel.SetAutoColor(sobj.GetFather())

                            for i in [DisplayMESHAction, HideMESHAction]:
                                popup.addAction(self.commonAction(i))
                                self.commonAction(i).setEnabled(True)

                        meshGroupObject, group = CFDSTUDYGUI_DataModel.getMeshFromGroup(sobj) # on teste et on recupere le groupe

                        if meshGroupObject <> None:
                            if len(self.l_color) == 0:
                                self.l_color = self.ul_color
                            if len(self.l_color) <> 0:
                                a = self.l_color[0]
                                self.ul_color.append(a)
                                self.l_color.remove(a)
                                x,y,z=a
                                group.SetColor(SALOMEDS.Color(x,y,z))

                            for i in [DisplayGroupMESHAction, DisplayOnlyGroupMESHAction, HideGroupMESHAction]:
                                popup.addAction(self.commonAction(i))
                                self.commonAction(i).setEnabled(True)


    def slotStudyLocation(self):
        """
        Loads the CFD study location. If the name of the CFD study
        does not exists, the corresponding folder is created.
        """
        log.debug("slotStudyLocation")
        dialog = self.DialogCollector.SetTreeLocationDialog
        dialog.__init__()
        dialog.exec_()
        if not self.DialogCollector.SetTreeLocationDialog.result() == QDialog.Accepted:
            return
        cursor = QCursor(Qt.BusyCursor)
        QApplication.setOverrideCursor(cursor)

        _SetCFDCode(dialog.code)

        iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theStudyPath = dialog.StudyPath,
                                                      theCaseNames = dialog.CaseNames,
                                                      theCreateOpt = dialog.CreateOption,
                                                      theCopyOpt   = dialog.CopyFromOption,
                                                      theNameRef   = dialog.CaseRefName)
        if iok:
            studyId = sgPyQt.getStudyId()
            sgPyQt.updateObjBrowser(studyId, 1)
            self.updateActions()
        QApplication.restoreOverrideCursor()


    def slotAddCase(self):
        """
        Builds new CFD cases.
        """
        log.debug("slotAddCase")
        dialog = self.DialogCollector.SetTreeLocationDialog
        dialog.__init__()
        dialog.setCaseMode()

        studyObj = self._singleSelectedObject()
        if studyObj == None:
            return

        dialog.StudyPath = CFDSTUDYGUI_DataModel._GetPath(studyObj)
        dialog.StudyDirName.setText(os.path.dirname(CFDSTUDYGUI_DataModel._GetPath(studyObj)))
        dialog.StudyLineEdit.setText(studyObj.GetName())
        
        if not os.path.exists(dialog.StudyPath):
            mess = str(self.tr("ENV_DLG_INVALID_DIRECTORY"))%(dialog.StudyPath) +str(self.tr("STMSG_UPDATE_STUDY_INCOMING"))
            QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
            return
        dialog.exec_()
        if self.DialogCollector.SetTreeLocationDialog.result() != QDialog.Accepted:
            #reinitialization
            dialog.setCaseMode()
            return
        _SetCFDCode(dialog.code)
#Get existing case name list of a CFD study
        ExistingCaseNameList = CFDSTUDYGUI_DataModel.GetCaseNameList(studyObj)
        if dialog.CaseNames != "" :
            newCaseList = string.split(string.strip(dialog.CaseNames)," ")
            for i in newCaseList:
                if i in ExistingCaseNameList:
                    mess = str(self.tr("CASE_ALREADY_EXISTS"))%(i,CFDSTUDYGUI_DataModel._GetPath(studyObj))

                    QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                else :
                    iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theStudyPath = dialog.StudyPath,
                                                                  theCaseNames = i,
                                                                  theCreateOpt = dialog.CreateOption,
                                                                  theCopyOpt   = dialog.CopyFromOption,
                                                                  theNameRef   = dialog.CaseRefName)
        if string.strip(dialog.CaseNames) == "" :
            if "CASE1" in ExistingCaseNameList:
                mess = str(self.tr("DEFAULT_CASE_ALREADY_EXISTS"))%("CASE1",CFDSTUDYGUI_DataModel._GetPath(studyObj))
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
            else :
                iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theStudyPath = dialog.StudyPath,
                                                              theCaseNames = "CASE1",
                                                              theCreateOpt = dialog.CreateOption,
                                                              theCopyOpt   = dialog.CopyFromOption,
                                                              theNameRef   = dialog.CaseRefName)            
        self.updateObjBrowser()


    def slotInfo(self):
        """
        Shows the QDialog with the info from CFDSTUDY:
            - CFD code selected
            - environnement variables defined
        """
        log.debug("slotInfo")
        dialog = self.DialogCollector.InfoDialog
        dialog.show()
        self.updateActions()


    def slotUpdateObjectBrowser(self):
        """
        Re-reads the unix folders and updates the complete representation
        of the CFD studies in the Object Browser.
        """
        self.updateObjBrowser()


    def updateObjBrowser(self, Object=None):
        """
        Updates CFD study sub-tree from the argument object.

        @type theObject: C{SObject}
        @param theObject: branch of a tree of data to update.
        """
        log.debug("updateObjBrowser")
        cursor = QCursor(Qt.BusyCursor)
        QApplication.setOverrideCursor(cursor)

        CFDSTUDYGUI_DataModel.UpdateSubTree(Object)

        QApplication.restoreOverrideCursor()


    def slotViewAction(self):
        """
        Edits in the read only mode the file selected in the Object Browser.
        Warning, the editor is always emacs!
        """
        viewerName = str( sgPyQt.stringSetting( "CFDSTUDY", "ExternalEditor", str(self.tr("CFDSTUDY_PREF_EDITOR")).strip() ) )
        if viewerName != "":
            sobj = self._singleSelectedObject()
            if sobj is not None:
                path = CFDSTUDYGUI_DataModel._GetPath(sobj)
                if re.match(".*emacs$", viewerName):
                    subprocess.Popen([viewerName, path, "-f", "toggle-read-only"])
                elif re.match("vi", viewerName) or re.match("vim", viewerName):
                    subprocess.call("xterm -sb -e vi " + path, shell=True)
                else:
                    subprocess.Popen([viewerName, path])


    def slotEditAction(self):
        """
        Edits in the user's editor the file selected in the Object Browser.
        """
        viewerName = str( sgPyQt.stringSetting( "CFDSTUDY", "ExternalEditor", str(self.tr("CFDSTUDY_PREF_EDITOR") ).strip() ))

        if viewerName != "":
            #viewerName = str(viewer.toLatin1())
            sobj = self._singleSelectedObject()
            if not sobj == None:
                path = CFDSTUDYGUI_DataModel._GetPath(sobj)
                subprocess.Popen([viewerName, path])

    def slotCloseStudyAction(self):
        """
        Close file or folder and children from the Object Browser.
        Delete dock windows cases attached to a CFD Study if this study is being closed from the Object Browser.
        """
        log.debug("slotCloseStudyAction")
        theStudy = self._singleSelectedObject()
        caseList = []
        xmlcaseList= []
        if theStudy != None:
            theStudypath = CFDSTUDYGUI_DataModel._GetPath(theStudy)
            mess = str(ObjectTR.tr("CLOSE_ACTION_CONFIRM_MESS"))%(theStudypath)#sobj.GetName())
            if QMessageBox.warning(None, "Warning", mess, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                return
        caseList = CFDSTUDYGUI_DataModel.GetCaseList(theStudy)
        if caseList != []:
            for aCase in caseList:
                self._SolverGUI.removeDockWindowfromStudyAndCaseNames(theStudy.GetName(), aCase.GetName())
        CFDSTUDYGUI_DataModel.closeCFDStudyTree(theStudy)

        self.updateObjBrowser()


    def slotRemoveAction(self):
        """
        Deletes file or folder from the Object Browser, and from the unix system files.
        Delete dock windows attached to a CFD Study if this study is deleted from the Object Browser.
        """
        log.debug("slotRemoveAction")
        sobj = self._singleSelectedObject()
        if sobj != None:
            sobjpath = CFDSTUDYGUI_DataModel._GetPath(sobj)
            mess = str(ObjectTR.tr("REMOVE_ACTION_CONFIRM_MESS"))%(sobjpath)#sobj.GetName())
            if QMessageBox.warning(None, "Warning", mess, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                return

            c = CFDSTUDYGUI_DataModel.GetCase(sobj).GetName()
            caseName  = sobj.GetName()
            studyObj = CFDSTUDYGUI_DataModel.GetStudyByObj(sobj)
            studyName = studyObj.GetName()
            father = sobj.GetFather()
            fatherpath = CFDSTUDYGUI_DataModel._GetPath(father)
            fathername = father.GetName()

            if c == caseName:
                XmlCaseNameList = CFDSTUDYGUI_DataModel.getXmlCaseNameList(sobj)
                if XmlCaseNameList != [] :
                    for i in XmlCaseNameList :
                        self._SolverGUI.removeDockWindow(studyName, caseName,i)

            watchCursor = QCursor(Qt.WaitCursor)
            QApplication.setOverrideCursor(watchCursor)
#           As we remove case directory which can be the current working directory, we need to change the current working directory eitherwise there is a problem with os.getcwd() or equivalent
            os.chdir(fatherpath)
            if os.path.isdir(sobjpath):
                shutil.rmtree(sobjpath)
            elif os.path.isfile(sobjpath):
                os.remove(sobjpath)
            QApplication.restoreOverrideCursor()
            self.updateObjBrowser(father)


    def slotCopyInDATA(self):
        """
        """
        sobj = self._singleSelectedObject()
        if sobj != None:
            studyId = sgPyQt.getStudyId()
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            study = CFDSTUDYGUI_DataModel._getStudy()
            builder = study.NewBuilder()

            attr = builder.FindOrCreateAttribute(sobj, "AttributeLocalID")
            parent = sobj.GetFather()
            if not parent == None:
                parent = parent.GetFather()

                if not parent == None and parent.GetName() == "DATA":
                    parentPath = CFDSTUDYGUI_DataModel._GetPath(parent)
                    newpath = os.path.join(parentPath, sobj.GetName())
                    mess = ObjectTR.tr("OVERWRITE_CONFIRM_MESS")
                    if os.path.exists(newpath):
                        mess = ObjectTR.tr("OVERWRITE_CONFIRM_MESS")
                        if QMessageBox.warning(None, "Warning", mess, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                            return

                    shutil.copy2(path, parentPath)
                    self.updateObjBrowser(parent)


    def slotCopyInSRC(self):
        """
        """
        sobj = self._singleSelectedObject()
        if sobj != None:
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            parent = sobj.GetFather()
            if not parent == None:
                if not parent == None and (parent.GetName() != "DRAFT" and parent.GetName() != "REFERENCE" and parent.GetName() != "EXAMPLES" ):
                    parent = parent.GetFather()
                if not parent == None and (parent.GetName() == "REFERENCE" or parent.GetName() == "DRAFT" or parent.GetName() == "EXAMPLES"):
                    parentName = parent.GetName()
                    parent = parent.GetFather()
                    if not parent == None and parent.GetName() == "SRC":
                        parentPath = CFDSTUDYGUI_DataModel._GetPath(parent)
                        destPath = os.path.join(parentPath, sobj.GetName())
                        if parentName == "EXAMPLES" and '-' in path :
                            a,b = string.split(sobj.GetName(),'-')
                            c = string.split(b,'.')[-1]
                            newName = string.join([a,c],'.')
                            destPath = os.path.join(parentPath,newName)
                        if os.path.exists(destPath):
                            mess = ObjectTR.tr("OVERWRITE_CONFIRM_MESS")
                            if QMessageBox.warning(None, "Warning", mess, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                                return
                        shutil.copy2(path, parentPath)
                        if parentName == "EXAMPLES" and '-' in path :
                            os.rename(os.path.join(parentPath,sobj.GetName()),
                                      os.path.join(parentPath,newName))
                        self.updateObjBrowser(parent)

    def slotMoveToDRAFT(self):
        """
        """
        sobj = self._singleSelectedObject()
        if not sobj == None:
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            parent = sobj.GetFather()
            if not parent == None:
                parentPath = os.path.join(CFDSTUDYGUI_DataModel._GetPath(parent), 'DRAFT')
                destPath = os.path.join(parentPath, sobj.GetName())
                if os.path.exists(destPath):
                    mess = ObjectTR.tr("OVERWRITE_CONFIRM_MESS")
                    if QMessageBox.warning(None, "Warning", mess, QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                        return
                    else:
                        os.remove(destPath)

                if os.path.exists(parentPath) == False:
                    os.mkdir(parentPath)

                shutil.move(path, parentPath)
                self.updateObjBrowser(parent)


    def _singleSelectedObject(self):
        """
        """
        study = CFDSTUDYGUI_DataModel._getStudy()
        if sg.SelectedCount() == 1:
            entry = sg.getSelected(0)
            if entry != '':
                return study.FindObjectID(entry)
        return None


    def _multipleSelectedObject(self):
        """
        """
        study = CFDSTUDYGUI_DataModel._getStudy()

        i = 0
        liste_SObj = []
        while i < sg.SelectedCount():
            entry = sg.getSelected(i)
            if entry != '':
                liste_SObj.append(study.FindObjectID(entry))
            i = i+1
        return liste_SObj

    def slotExportInParavis(self):
        """
        Not used now, but will be used when PARAVIS API will run correctly
        """

        sobj = self._singleSelectedObject()
        if not sobj == None:
            import pvsimple
            import salome
            pvsimple.ShowParaviewView()
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            if re.match(".*\.med$", sobj.GetName()) or re.match(".*\.case$", sobj.GetName()):
                #export Med file from CFDSTUDY into PARAVIS
                engine = salome.lcc.FindOrLoadComponent("FactoryServer", "PARAVIS")
                renderView1 = pvsimple.GetActiveViewOrCreate('RenderView')
                pvsimple.OpenDataFile(path)
                DataRepresentation = pvsimple.Show()
                renderView1.ResetCamera()

            if re.match(".*\.csv$", sobj.GetName()) :
                #export csv file from CFDSTUDY into PARAVIS
                engine = salome.lcc.FindOrLoadComponent("FactoryServer", "PARAVIS")
                coord_path = pvsimple.CSVReader(FileName=[path])
                renderView1 = pvsimple.GetActiveViewOrCreate('RenderView')
                viewLayout1 = pvsimple.GetLayout()
                pvsimple.OpenDataFile(path)
                # Create a new 'SpreadSheet View'
                spreadSheetView1 = pvsimple.CreateView('SpreadSheetView')
                # place view in the layout
                #viewLayout1.AssignView(2, spreadSheetView1)
                # show data in view
                coord_Display = pvsimple.Show(coord_path, spreadSheetView1)

            if salome.sg.hasDesktop():
                salome.sg.updateObjBrowser(1)
        QApplication.restoreOverrideCursor()


    def slotExportInSMESH(self):
        """
        smesh_component         is a smeshDC.smeshDC instance
        SO_SMESH_COMPONENT         is a SALOMEDS._objref_SComponent instance
        aMeshes                 is a list of smeshDC.Mesh instances of the meshes into the med file
        meshDC.GetMesh()         is a Corba SMESH._objref_SMESH_Mesh instance
        SO_SMESH                 is a SALOMEDS._objref_SObject instance representing mesh object into
                                      Object browser under SMESH Component
        Create Med structure of the med file whose complete name is path,
             into smesh component and puplication of the mesh into Object Browser
             aMeshes is a list of smeshDC.Mesh instances of the meshes into the med file
             (we can have several meshes into a med file)

        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        sobj = self._singleSelectedObject()
        if not sobj == None:
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)
            studyId = salome.sg.getActiveStudyId()
            if smeshBuilder and re.match(".*\.med$", sobj.GetName()):
                smesh = smeshBuilder.New(salome.myStudy)
                aMeshes, aStatus = smesh.CreateMeshesFromMED(path)
                if not aStatus:
                    QApplication.restoreOverrideCursor()
                    mess = ObjectTR("EXPORT_IN_SMESH_ACTION_WARNING")
                    QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
                    return

                (reppath,fileName)=   os.path.split(path)
                for aMeshDC in aMeshes:
                    aMeshDC.SetAutoColor(1)
                    mesh = aMeshDC.GetMesh()

            sgPyQt.updateObjBrowser(studyId, 1)

        QApplication.restoreOverrideCursor()


    def slotDisplayMESH(self):
        """
        Changed on November 2010 for the popup menu: SMESH Mesh objects can have the slotDisplayMESH directly
        the old code with referenced objects is deleted
        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        if self._multipleSelectedObject() == None:
            mess = "Display MESH: No object selected into Object Browser"
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
            return
        smeshgui = salome.ImportComponentGUI("SMESH")
        studyId = salome.sg.getActiveStudyId()
        smeshgui.Init(studyId)

        log.debug("slotDisplayMESH -> self._multipleSelectedObject()[0].GetName()= %s" % self._multipleSelectedObject()[0].GetName())
        for  sobj in self._multipleSelectedObject():
            if sobj != None:
                entry = sobj.GetID()
                if entry == None:
                    mess = "slotDisplayMESH: No mesh with the Name: " + sobj.GetName() + ", under Mesh into Object Browser"
                    QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
                    QApplication.restoreOverrideCursor()
                    return
                #Displaying Mesh
                if CFDSTUDYGUI_DataModel.getMeshFromMesh(sobj):
                    smeshgui.CreateAndDisplayActor(entry)
                    sgPyQt.updateObjBrowser(studyId,1)
                    salome.sg.UpdateView()
                    salome.sg.FitAll()
            else:
                mess = "slotDisplayMESH: Entry Id not stored for the mesh: " + sobj.GetName()
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
        QApplication.restoreOverrideCursor()


    def slotDisplayMESHGroups(self):
        """
        Changed on November 2010 for the popup menu: SMESH Group Mesh objects can have the slotDisplayMESHGroups directly
        the old code with referenced objects is deleted
        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        if self._multipleSelectedObject() == None:
            mess = "Display MESH Groups: No object selected into Object Browser"
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
            return
        smeshgui = salome.ImportComponentGUI("SMESH")

        for sobj_group in self._multipleSelectedObject():
            if sobj_group != None:
                meshgroup,group = CFDSTUDYGUI_DataModel.getMeshFromGroup(sobj_group)
                if meshgroup:
                    smeshgui.CreateAndDisplayActor(sobj_group.GetID())
            else:
                mess = "No group "+ sobj_group.GetName() + " whose mesh father name is:",sobj_group.GetFatherComponent().GetName() #GetFather().GetFather().GetName()
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
        salome.sg.UpdateView()
        salome.sg.FitAll()

        QApplication.restoreOverrideCursor()


    def slotDisplayOnlyMESHGroups(self):
        """
        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        sobj = self._singleSelectedObject()
        id = sobj.GetID()
        if id:
            salome.sg.EraseAll()
            #salome.sg.Display(entryIdGroup)#Only(entryIdGroup)
            smeshgui = salome.ImportComponentGUI("SMESH")
            smeshgui.CreateAndDisplayActor(id)
        else:
            mess = "No Entry Id for group "+ sobj.GetName() + " whose mes Name is:",sobj.GetFatherComponent().GetName() #GetFather().GetFather().GetName()
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
        salome.sg.UpdateView()
        salome.sg.FitAll()

        QApplication.restoreOverrideCursor()


    def slotHideMESHGroups(self):
        """
        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        if self._multipleSelectedObject() == None:
            mess = "Hide MESH Groups: No object selected into Object Browser"
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
            return

        for sobj in self._multipleSelectedObject():
            id = sobj.GetID()
            if id:
                meshgroup,group = CFDSTUDYGUI_DataModel.getMeshFromGroup(sobj)
                if meshgroup:
                    salome.sg.Erase(id)
            else:
                mess = "No Entry Id for group "+ sobj.GetName() + " whose mesh Name is:",sobj.GetFatherComponent().GetName() # sobj.GetFather().GetFather().GetName()
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
        salome.sg.UpdateView()
        salome.sg.FitAll()

        QApplication.restoreOverrideCursor()


    def slotHideMESH(self):
        """
        Changed on November 2010 for the popup menu: SMESH Mesh objects can have the slotHideMESH directly
        """
        waitCursor = QCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(waitCursor)

        if self._multipleSelectedObject() == None:
            mess = "Hide MESH: No object selected into Object Browser"
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
            return

        for sobj in self._multipleSelectedObject():
            id = sobj.GetID()
            if id:
                if CFDSTUDYGUI_DataModel.getMeshFromMesh(sobj):
                    salome.sg.Erase(id)
            else:
                mess = "No Entry Id for mesh "+ sobj.GetName()
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
        salome.sg.UpdateView()
        salome.sg.FitAll()

        QApplication.restoreOverrideCursor()


    def OpenCFD_GUI(self,sobj):
        """
        Open into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        log.debug("OpenCFD_GUI")
        import os
        if sobj != None:
            if not os.path.exists(CFDSTUDYGUI_DataModel._GetPath(sobj)):
                mess = str(self.tr("ENV_DLG_INVALID_FILE"))%("CFD_Code",CFDSTUDYGUI_DataModel._GetPath(sobj))+ str(self.tr("STMSG_UPDATE_STUDY_INCOMING"))
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                self.updateObjBrowser()
                return
            if CFDSTUDYGUI_DataModel.checkType(sobj, CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]):
                aXmlFileName = sobj.GetName()
                aCase = CFDSTUDYGUI_DataModel.GetCase(sobj)
                aStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(sobj)
                if aCase:
                    aCaseName = aCase.GetName()
                else:
                    mess = "Error: "+ aXmlFileName + " file has no CFD Case into the Salome Object browser"
                    QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, QMessageBox.NoButton)
                    return
                if aStudy:
                    aStudyName = aStudy.GetName()
                else:
                    mess = "Error: "+ aXmlFileName + " file has no CFD Study into the Salome Object browser"
                    QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, QMessageBox.NoButton)
                    return
                if CFDSTUDYGUI_SolverGUI.findDockWindow(aXmlFileName, aCaseName,aStudyName):
                    mess = aStudyName + " " + aCaseName + ": " + aXmlFileName + " is already opened"
                    QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                    return

                # xml case file not already opened
                aCmd = []
                aCmd.append('-p')
                aCmd.append(aXmlFileName)
                aXmlFile = sobj
                wm = self._SolverGUI.ExecGUI(self.dskAgent().workspace(), aXmlFile, aCase, aCmd)
                self.updateActions()


    def slotOpenCFD_GUI(self):
        """
        Open into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        log.debug("slotOpenCFD_GUI")
        sobj = self._singleSelectedObject()
        if sobj != None:
            import os
            if not os.path.exists(CFDSTUDYGUI_DataModel._GetPath(sobj)):
                mess = str(self.tr("ENV_DLG_INVALID_FILE"))%("CFD_Code",CFDSTUDYGUI_DataModel._GetPath(sobj))+ str(self.tr("STMSG_UPDATE_STUDY_INCOMING"))
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                self.updateObjBrowser()
                return
            self.OpenCFD_GUI(sobj)

    def slotOpenAnExistingCaseFileFromMenu(self):
        """
        Open into Salome the CFD GUI an existing XML file case from the Gui menu and not from Object browser
        """     
        log.debug("slotOpenAnExistingCaseFileFromMenu")
        boo         = False
        StudyPath   = ""
        CaseName    = ""
        xmlfileName = ""
        title = str(self.tr("Open An Existing Case"))
        xmlfileName, _ = QFileDialog.getOpenFileName(None,title,QDir.currentPath(), "*.xml")
        if xmlfileName == "" :
            return
        boo,StudyPath,CasePath = self.checkCFDCaseDir(str(xmlfileName))
        if boo and StudyPath != "" and CasePath != "" :
            CaseName = os.path.basename(CasePath)
            iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theStudyPath = StudyPath,
                                                          theCaseNames = CasePath,
                                                          theCreateOpt = False,
                                                          theCopyOpt   = False,
                                                          theNameRef   = "")
            studyObj = CFDSTUDYGUI_DataModel.FindStudyByPath(StudyPath)
            caseObj  = CFDSTUDYGUI_DataModel.getSObject(studyObj,CaseName)
            DATAObj  = CFDSTUDYGUI_DataModel.getSObject(caseObj,"DATA")
            XMLObj   = CFDSTUDYGUI_DataModel.getSObject(DATAObj,os.path.basename(xmlfileName))
            codeName = CFDSTUDYGUI_DataModel.getNameCodeFromXmlCasePath(xmlfileName)
            self.OpenCFD_GUI(XMLObj)
            self.updateActionsXmlFile(XMLObj)


    def checkCFDCaseDir(self,filepath) :
        """
        Check if filepath is an XML file which belong to a CFD case directory
        The structure of the case directory must include DATA RESU SCRIPTS SRC directory
        """
        log.debug("checkCFDCaseDir")
        boo = True
        StudyPath = ""
        CasePath  = ""

        if not os.path.exists(filepath):
            mess = str(self.tr("ENV_DLG_INVALID_FILE"))%("CFD_Code",filepath)
            QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
            return False,StudyPath,CasePath

        # Test if filepath is a CFD xml file for Code_Saturne or NEPTUNE_CFD
        codeName = CFDSTUDYGUI_DataModel.getNameCodeFromXmlCasePath(filepath)
        if codeName == "":
            boo = False
            mess = str(self.tr("ENV_DLG_INVALID_FILE_XML"))%("CFD_Code",filepath)
            QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
            return boo,StudyPath,CasePath
        else :
            _SetCFDCode(codeName)

        repDATA = os.path.dirname(filepath)
        if os.path.isdir(repDATA) and os.path.basename(repDATA) == "DATA":
            CasePath = os.path.dirname(repDATA)
            repListe = os.listdir(CasePath)
            for i in ['SRC', 'RESU', 'DATA', 'SCRIPTS'] :
                boo = boo and os.path.isdir(os.path.join(CasePath,i))
            if not boo :
                mess = str(self.tr("ENV_DLG_CASE_FILE"))%(filepath,CasePath)
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                return boo,StudyPath,CasePath
            StudyPath = os.path.dirname(CasePath)
        else:
            boo = False
            mess = str(self.tr("ENV_INVALID_DATA_FILE_XML"))%("CFD_Code",filepath)
            QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, QMessageBox.NoButton)
        return boo,StudyPath,CasePath
                

    def CloseCFD_GUI(self, sobj):
        """
        Close into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        log.debug("CloseCFD_GUI")
        if sobj != None and CFDSTUDYGUI_DataModel.checkType(sobj, CFDSTUDYGUI_DataModel.dict_object["DATAfileXML"]):
            aXmlFileName = sobj.GetName()
            aCase = CFDSTUDYGUI_DataModel.GetCase(sobj)
            aStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(sobj)
            if aCase:
                aCaseName = aCase.GetName()
            else:
                mess = str(self.tr("INFO_DLG_NO_CASE_INTO_OB"))%(aXmlFileName)
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
                return
            if aStudy:
                aStudyName = aStudy.GetName()
            else:
                mess = str(self.tr("INFO_DLG_NO_CFD_STUDY_INTO_OB"))%(aXmlFileName)
                QMessageBox.warning(None, "Warning", mess, QMessageBox.Ok, 0)
                return
        else:
            # close the active CFDGUI window with the icon button CLOSE_CFD_GUI_ACTION_ICON in the tool bar
            aStudyName, aCaseName, aXmlFileName = self._SolverGUI.getStudyCaseXmlNames(self._SolverGUI._CurrentWindow)

        log.debug("CloseCFD_GUI %s %s %s" % (aStudyName, aCaseName, aXmlFileName))
        if self._SolverGUI.okToContinue():
            self._SolverGUI.removeDockWindow(aStudyName, aCaseName, aXmlFileName)
            self.commonAction(OpenGUIAction).setEnabled(True)
            self.solverAction(SolverCloseAction).setEnabled(False)
            self.updateActions()


    def slotCloseCFD_GUI(self):
        """
        Close into Salome the CFD GUI from an XML file whose name is sobj.GetName()
        """
        log.debug("slotCloseCFD_GUI")
        sobj = self._singleSelectedObject()
        self.CloseCFD_GUI(sobj)


    def slotUndo(self):
        self._SolverGUI.onUndo()


    def slotRedo(self):
        self._SolverGUI.onRedo()

    def slotPreproMode(self):
        self._SolverGUI.onPreproMode()

    def slotCalculationMode(self):
        self._SolverGUI.onCalculationMode()

    def slotLaunchGUI(self, study=None, case=None):
        """
        Build the command line for the GUI of Code_Saturne/NEPTUNE_CFD.
        Launch a new CFD IHM with popup menu on case object into SALOME Object browser
        """
        log.debug("slotLaunchGUI")
        #get current selection
        sobj = self._singleSelectedObject()
        if study:
            aStudy = study
        else:
            aStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(sobj)

        if aStudy == None:
            return
        # get current case
        if case:
            aCase = case
        else:
            aCase = CFDSTUDYGUI_DataModel.GetCase(sobj)
        import os
        if not os.path.exists(CFDSTUDYGUI_DataModel._GetPath(aCase)):
            mess = str(self.tr("ENV_DLG_INVALID_DIRECTORY"))%(CFDSTUDYGUI_DataModel._GetPath(aCase)) + str(self.tr("STMSG_UPDATE_STUDY_INCOMING"))
            QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
            self.updateObjBrowser()
            return

        # get current case name
        aCaseName = aCase.GetName()
        aXmlFile = None
        aCmd = []

        # object of DATA folder
        aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aCase, "^DATA$")
        if not len(aChildList) == 1:
            # no DATA folder
            return

        aDataObj =  aChildList[0]
        aDataPath = CFDSTUDYGUI_DataModel._GetPath(aDataObj)
        # object of 'CFDSTUDYGUI' file
        import sys
        if CFD_Code() == CFD_Saturne:
            if sys.platform.startswith("win"):
                aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aDataObj, "^SaturneGUI.bat$")
            else:
                aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aDataObj, "^SaturneGUI$")
            if len(aChildList) == 0:
                # no 'CFDSTUDYGUI' file
                mess = "No SaturneGUI file found into DATA directory case name "+ aCaseName
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                return
        elif CFD_Code() == CFD_Neptune:
            if sys.platform.startswith("win"):
                aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aDataObj, "^NeptuneGUI.bat$")
            else:
                aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aDataObj, "^NeptuneGUI$")
            if len(aChildList) == 0:
                # no 'CFDSTUDYGUI' file
                mess = "No NeptuneGUI file found into DATA directory case name "+ aCaseName
                QMessageBox.information(None, "Information", mess, QMessageBox.Ok, QMessageBox.NoButton)
                return
        aCmd.append('-n')
        sobjxml = None
        wm = self._SolverGUI.ExecGUI(self.dskAgent().workspace(), sobjxml, aCase, aCmd)
        self.updateActions()


    def __compile(self, aCaseObject):
        """
        Private method.
        Build the 'code_saturne compile -t' or the 'neptune_cfd compile -t' command.

        @type theCase: C{SObject}
        @param theCase: object from the Object Browser.
        @rtype: C{String}
        @return: command line
        """
        # object of SRC folder
        cmd = ""
        aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aCaseObject, "SRC")
        if not len(aChildList) == 1:
            raise ValueError, "There is a mistake with the SRC directory"

        env_code, mess = CheckCFD_CodeEnv(CFD_Code())
        if not env_code:
            QMessageBox.critical(self,"Error", mess, QMessageBox.Ok, 0)
        else:
            b, c,mess = BinCode()
            if mess == "":
                cmd = b + " compile -t"
            else:
                QMessageBox.critical(self,"Error", mess, QMessageBox.Ok, 0)
        return cmd


    def slotMeshConvertToMed(self):
        """
        """
        study = CFDSTUDYGUI_DataModel._getStudy()

        sg = CFDSTUDYGUI_DataModel.sg
        if sg.SelectedCount() != 1:
            # no selection
            return
        elif sg.SelectedCount() == 1:
            sobj = self._singleSelectedObject()
            medFile = str(QFileInfo(sobj.GetName()).baseName())
            self.DialogCollector.ECSConversionDialog.setResultFileName(medFile)

        self.DialogCollector.ECSConversionDialog.exec_()
        if not self.DialogCollector.ECSConversionDialog.result() == QDialog.Accepted:
            return

        aFirtsObj = None
        if sg.SelectedCount() == 1:
            aFirtsObj = self._singleSelectedObject()
        else:
            list_obj  = self._multipleSelectedObject()
            if not list_obj == []:
                aFirtsObj = list_obj[0]
            else:
                return

        aStudyObj = CFDSTUDYGUI_DataModel.GetStudyByObj(aFirtsObj)
        aChList = CFDSTUDYGUI_DataModel.ScanChildren(aStudyObj, "MESH")
        if not len(aChList) == 1:
            mess = "Directory MESH does not exist !"
            QMessageBox.critical(self, "Error", mess, QMessageBox.Ok, 0)
            return

        aMeshFold = aChList[0]
        thePath = CFDSTUDYGUI_DataModel._GetPath(aMeshFold)

        log.debug("slotMeshConvertToMed -> thePath = %s" % thePath)
        args = ""

        b, c, mess = BinCode()
        if mess != "":
            QMessageBox.critical(self,"Error", mess, QMessageBox.Ok, 0)
        else:
            args = c

            outfile = self.DialogCollector.ECSConversionDialog.resultFileName()

            args += " --no-write "
            args += " --case "
            args += os.path.join(thePath, outfile)
            args += " --post-volume "
            args += " med "
            args += CFDSTUDYGUI_DataModel._GetPath(sobj)

            log.debug("slotMeshConvertToMed -> args = %s" % args)
            dlg = CFDSTUDYGUI_CommandMgr.CFDSTUDYGUI_QProcessDialog(sgPyQt.getDesktop(),
                                                                    self.tr("STMSG_ECS_CONVERT"),
                                                                    [args],
                                                                    sobj.GetFather(),
                                                                    thePath)
            dlg.show()


    def slotCopyCaseFile(self):
        """
        Copy data xml file from a study case to another with popup menu attached to the xml file
        Copy into another case: COPY_CASE_FILE_ACTION_TEXT
        """
        sobj = self._singleSelectedObject()
        if sobj == None:
            return

        self.DialogCollector.CopyDialog.setCurrentObject(sobj)
        self.DialogCollector.CopyDialog.show()

        if not self.DialogCollector.CopyDialog.result() == QDialog.Accepted:
            return
        # update Object Browser
        # aDirPath: path directory where the xml file is copied
        aDirPath = self.DialogCollector.CopyDialog.destCaseName()
        aDirObject = CFDSTUDYGUI_DataModel.findMaxDeepObject(aDirPath)

        if aDirObject != None:
            self.updateObjBrowser(CFDSTUDYGUI_DataModel.GetCase(aDirObject))
        # BUG if direct call to self.updateObjBrowser(aDirObject)


    def slotCheckCompilation(self):
        """
        """
        #get current selection
        sobj = self._singleSelectedObject()
        if sobj == None:
            return

        # get current case
        aCase = CFDSTUDYGUI_DataModel.GetCase(sobj)
        if aCase == None:
            return
        cmd = self.__compile(aCase)
        if cmd != "":
            aChildList = CFDSTUDYGUI_DataModel.ScanChildren(aCase, "SRC")
            aSRCObj =  aChildList[0]
            aSRCPath = CFDSTUDYGUI_DataModel._GetPath(aSRCObj)

            dlg = CFDSTUDYGUI_CommandMgr.CFDSTUDYGUI_QProcessDialog(sgPyQt.getDesktop(),
                                                                    self.tr("STMSG_CHECK_COMPILATION"),
                                                                    [cmd],
                                                                    None,
                                                                    aSRCPath)
            dlg.show()


    def slotRunScript(self):
        """
        """
        log.debug("slotRunScript")
        sobj = self._singleSelectedObject()
        if sobj:
            curd = os.path.abspath('.')
            father = sobj.GetFather()
            fatherpath = CFDSTUDYGUI_DataModel._GetPath(father)
            path = CFDSTUDYGUI_DataModel._GetPath(sobj)

            # check exec rights
            if not os.access(path, os.F_OK or os.X_OK):
                mess = str(self.tr("RUN_SCRIPT_ACTION_ACCESS_ERROR"))
                QMessageBox.critical(None, "Error", mess, QMessageBox.Ok, 0)
                return

            dlg = CFDSTUDYGUI_CommandMgr.CFDSTUDYGUI_QProcessDialog(sgPyQt.getDesktop(),
                                                                    self.tr("STMSG_RUN_SCRIPT"),
                                                                    [path],
                                                                    father,
                                                                    fatherpath)
            dlg.show()


    def slotSaveDataFile(self):
        """
        Redirects B{Save} method to GUI of current solver
        """
        log.debug("slotSaveDataFile")
        if self._SolverGUI._CurrentWindow != None:
            if self._SolverGUI._CurrentWindow.case['xmlfile'] != "":
                self._SolverGUI._CurrentWindow.fileSave()
            else:
                self.slotSaveAsDataFile()


    def slotSaveAsDataFile(self):
        """
        Redirects B{SaveAs} method to GUI of current solver
        """
        log.debug("slotSaveAsDataFile")
        old_sobj = None
        new_sobj = None
        oldCase = self._SolverGUI.getCase(self._SolverGUI._CurrentWindow)
        oldStudy = CFDSTUDYGUI_DataModel.GetStudyByObj(oldCase)
        old_xml_file, xml_file = self._SolverGUI.SaveAsXmlFile()
        if old_xml_file == None and xml_file != None:
            #MP 25/04/2012 - A faire: tester si le fichier xml_file est deja ouvert dans le GUI dans une etude SALOME avec CFDSTUDYGUI_Management.py
            # classe CFDGUI_Management, methode findElem(xmlName, caseName, studyCFDName)
            # emettre un warning car on vient de sauvegarder dans un fichier xml existant et de plus ouvert dans une etude salome ==> #MP 2016/12/14 Corrections a faire
            theNewStudyPath = os.path.dirname(os.path.dirname(os.path.dirname(xml_file)))
            study = CFDSTUDYGUI_DataModel.FindStudyByPath(theNewStudyPath)
            theCaseName = os.path.basename(os.path.dirname(os.path.dirname(xml_file)))
            if study == None:
                theCaseName = os.path.basename(os.path.dirname(os.path.dirname(xml_file)))

                iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theNewStudyPath, theCaseName,
                                                      theCreateOpt = False,
                                                      theCopyOpt   = False,
                                                      theNameRef   = "")
                if iok:
                    study = CFDSTUDYGUI_DataModel.FindStudyByPath(theNewStudyPath)
                    obj = CFDSTUDYGUI_DataModel.checkPathUnderObject(study, xml_file)
                    if obj:
                        NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                        if  NewSObj != None:
                            self.OpenCFD_GUI(NewSObj)
                            self._SolverGUI.removeDockWindow(oldStudy.GetName(), oldCase.GetName(), "unnamed")
            else:
                theCaseName = os.path.basename(os.path.dirname(os.path.dirname(xml_file)))
                theCaseObj = CFDSTUDYGUI_DataModel.getSObject(study,theCaseName)
                if theCaseObj != None:
                    obj = CFDSTUDYGUI_DataModel.getSObject(theCaseObj,"DATA")
                    if obj != None:
                        NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                        if  NewSObj != None:
                            self._SolverGUI.removeDockWindow(oldStudy.GetName(), oldCase.GetName(), "unnamed")
                            self.CloseCFD_GUI(NewSObj)
                            self.OpenCFD_GUI(NewSObj)
                        else:
                            CFDSTUDYGUI_DataModel._CreateItem(obj,os.path.basename(xml_file))
                            NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                            if  NewSObj != None:
                                self._SolverGUI.removeDockWindow(study.GetName(),theCaseName , "unnamed")
                                self.OpenCFD_GUI(NewSObj)
                    else:
                        mess = "DATA directory is not found into Object Browser for case " +  theCaseName + "and study = " + study.GetName()
                        QMessageBox.critical(None, "Error", mess, QMessageBox.Ok, 0)
            return

        if xml_file != None and xml_file != old_xml_file and old_xml_file != None:
            theOldStudyPath = os.path.dirname(os.path.dirname(os.path.dirname(old_xml_file)))
            theOldStudyName = os.path.basename(theOldStudyPath)
            theNewStudyPath = os.path.dirname(os.path.dirname(os.path.dirname(xml_file)))
            theNewStudyName = os.path.basename(theNewStudyPath)
            oldStudy = CFDSTUDYGUI_DataModel.FindStudyByPath(theOldStudyPath)
            Old_obj = CFDSTUDYGUI_DataModel.checkPathUnderObject(oldStudy, old_xml_file) #parent DATA path object for old_xml_file
            if Old_obj:
                OldSobj = CFDSTUDYGUI_DataModel.getSObject(Old_obj,os.path.basename(old_xml_file))
                if OldSobj != None:
                    self.CloseCFD_GUI(OldSobj)

            if theOldStudyName == theNewStudyName:
                study = oldStudy
                obj = CFDSTUDYGUI_DataModel.checkPathUnderObject(study, xml_file) #parent DATA path object for xml_file
                if obj:
                    if os.path.exists(xml_file):
                        CFDSTUDYGUI_DataModel._CreateItem(obj,os.path.basename(xml_file))
                        NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                        if  NewSObj != None:
                            self.OpenCFD_GUI(NewSObj)

            else:
                study = CFDSTUDYGUI_DataModel.FindStudyByPath(theNewStudyPath)
                if study == None:
                    theCaseName = os.path.basename(os.path.dirname(os.path.dirname(xml_file)))
                    iok = CFDSTUDYGUI_DataModel._SetStudyLocation(theNewStudyPath, theCaseName,
                                                      theCreateOpt = False,
                                                      theCopyOpt   = False,
                                                      theNameRef   = "")
                    if iok:
                        study = CFDSTUDYGUI_DataModel.FindStudyByPath(theNewStudyPath)
                        obj = CFDSTUDYGUI_DataModel.checkPathUnderObject(study, xml_file)
                        if obj:
                            NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                            if  NewSObj != None:
                                self.OpenCFD_GUI(NewSObj)
                else:
                   obj = CFDSTUDYGUI_DataModel.checkPathUnderObject(study, xml_file)
                   NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                   if  NewSObj != None:
                       self.CloseCFD_GUI(NewSObj)
                       self.OpenCFD_GUI(NewSObj)
                   else:
                       CFDSTUDYGUI_DataModel._CreateItem(obj,os.path.basename(xml_file))
                       NewSObj = CFDSTUDYGUI_DataModel.getSObject(obj,os.path.basename(xml_file))
                       if  NewSObj != None:
                           self.OpenCFD_GUI(NewSObj)


    def slotOpenShell(self):
        """
        Redirects B{OpenShell} method to GUI of current solver
        """
        self._SolverGUI.onOpenShell()


    def slotDisplayCurrentCase(self):
        """
        Redirects B{Display Current Case} method to GUI of current solver
        """
        self._SolverGUI.onDisplayCase()


    def slotHelpAbout(self):
        """
        Redirects B{About QDialog} display to GUI of current solver
        """
        self._SolverGUI.onHelpAbout()


    def slotHelpLicense(self):
        self._SolverGUI.onSaturneHelpLicense()


    def slotHelpUserGuide(self):
        self._SolverGUI.onSaturneHelpManual()


    def slotHelpTutorial(self):
        self._SolverGUI.onSaturneHelpTutorial()


    def slotHelpTheory(self):
        self._SolverGUI.onSaturneHelpKernel()


    def slotHelpRefcard(self):
        self._SolverGUI.onSaturneHelpRefcard()


    def slotHelpDoxygen(self):
        self._SolverGUI.onSaturneHelpDoxygen()


    def slotHelpNCUserGuide(self):
        self._SolverGUI.onNeptuneHelpManual()


    def slotHelpNCTutorial(self):
        self._SolverGUI.onNeptuneHelpTutorial()


    def slotHelpNCTheory(self):
        self._SolverGUI.onNeptuneHelpKernel()


    def slotHelpNCDoxygen(self):
        self._SolverGUI.onNeptuneHelpDoxygen()


    def commonAction(self, theId):
        """
        Returns action by id from common action map of module
        """
        if not theId in self._CommonActionIdMap:
            raise ActionError, "Invalid action id"

        action_id = self._CommonActionIdMap[theId]

        if action_id == None or not action_id in self._ActionMap:
            raise ActionError, "Invalid action map content"
        return self._ActionMap[action_id]


    def solverAction(self, theId):
        """
        Returns action by id from solver action maps of module
        """
        action_id = None

        if theId in self._SolverActionIdMap:
            action_id =  self._SolverActionIdMap[theId]
        elif theId in self._HelpActionIdMap:
            action_id = self._HelpActionIdMap[theId]

        if action_id == None:
            raise ActionError, "Invalid action id"

        if not action_id in self._ActionMap:
            raise ActionError, "Invalid action map content"

        return self._ActionMap[action_id]


    def actionId(self, theId):
        """
        """
        action_id = None

        if theId in self._CommonActionIdMap:
            action_id =  self._CommonActionIdMap[theId]
        elif theId in self._SolverActionIdMap:
            action_id =  self._SolverActionIdMap[theId]
        elif theId in self._HelpActionIdMap:
            action_id = self._HelpActionIdMap[theId]

        if action_id == None:
            raise ActionError, "Invalid action id"

        return action_id


    def dskAgent(self):
        """
        Returns the dekstop Agent.
        """
        return self._DskAgent


    def disconnectSolverGUI(self):
        """
        Hide all the dock windows of CFDSTUDY, when activating another Salome Component
        We can have one or several of them with the right click on the main menu bar of
        Salome
        """
        log.debug("disconnectSolverGUI")
        self._SolverGUI.disconnectDockWindows()


    def connectSolverGUI(self):
        """
        Show all the dock windows of CFDSTUDY, when activating another Salome Component
        """
        log.debug("connectSolverGUI")
        self._SolverGUI.connectDockWindows()

