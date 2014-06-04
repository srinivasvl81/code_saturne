# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------

# This file is part of Code_Saturne, a general-purpose CFD tool.
#
# Copyright (C) 1998-2014 EDF S.A.
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

#-------------------------------------------------------------------------------

"""
This module defines the 'Additional user's scalars' page.

This module defines the following classes:
- DefineUserScalarsModel
"""

#-------------------------------------------------------------------------------
# Library modules import
#-------------------------------------------------------------------------------

import string
import unittest

#-------------------------------------------------------------------------------
# Application modules import
#-------------------------------------------------------------------------------

from Base.Common import *
import Base.Toolbox as Tool
from Base.XMLvariables import Variables
from Base.XMLvariables import Model
from Base.XMLmodel import XMLmodel, ModelTest

#-------------------------------------------------------------------------------
# Define User Scalars model class
#-------------------------------------------------------------------------------

class DefineUserScalarsModel(Variables, Model):
    """
    Useful methods for operation of the page.
    __method : private methods for the Model class.
    _method  : private methods for the View Class
    """
    def __init__(self, case):
        """
        Constructor
        """
        self.case = case

        self.scalar_node = self.case.xmlGetNode('additional_scalars')
        self.node_models = self.case.xmlGetNode('thermophysical_models')
        self.node_therm  = self.node_models.xmlGetNode('thermal_scalar')
        self.node_bc     = self.case.xmlGetNode('boundary_conditions')


    def defaultScalarValues(self):
        """Return the default values - Method also used by ThermalScalarModel"""
        default = {}
        default['scalar_label']          = "scalar"
        default['variance_label']        = "variance"
        default['coefficient_label']     = "Dscal"
        default['diffusion_coefficient'] = 1.83e-05
        default['diffusion_choice']      = 'constant'
        default['zone_id']               = 1
        default['GGDH']                  = "SGDH"
        if self.getScalarLabelsList():
            default['variance']          = self.getScalarLabelsList()[0]
        else:
            default['variance']          = "no scalar"

        return default


    def __removeScalarChildNode(self, label, tag):
        """
        Private method.
        Delete 'variance' or 'property' markup from scalar named I{label}
        """
        for node in self.scalar_node.xmlGetNodeList('variable'):
            if node['label'] == label:
                node.xmlRemoveChild(tag)


    def __deleteScalarBoundaryConditions(self, label):
        """
        Private method.
        Delete boundary conditions for scalar I{label}
        """
        for nature in ('inlet', 'outlet', 'wall'):
            for node in self.node_bc.xmlGetChildNodeList(nature):
                for n in node.xmlGetChildNodeList('variable'):
                    if n['label'] == label:
                        n.xmlRemoveNode()


    def __defaultScalarNameAndDiffusivityLabel(self, scalar_label=None):
        """
        Private method.
        Return a default name and label for a new scalar.
        Create a default name for the associated diffusion coefficient to.
        """
        __coef = {}
        for l in self.getScalarLabelsList():
            __coef[l] = self.getScalarDiffusivityLabel(l)
        length = len(__coef)
        Lscal = self.defaultScalarValues()['scalar_label']
        Dscal = self.defaultScalarValues()['coefficient_label']

        # new scalar: default value for both scalar and diffusivity

        if not scalar_label:
            if length != 0:
                i = 1
                while (Dscal + str(i)) in list(__coef.values()):
                    i = i + 1
                num = str(i)
            else:
                num = str(1)
            scalar_label = Lscal + num
            __coef[scalar_label] = Dscal + num

        # existing scalar

        else:
            if scalar_label not in list(__coef.keys())or \
               (scalar_label in list(__coef.keys()) and __coef[scalar_label] == ''):

                __coef[scalar_label] = Dscal + str(length + 1)

        return scalar_label, __coef[scalar_label]


    def __defaultVarianceName(self, scalar_label=None):
        """
        Private method.
        Return a default name and label for a new variance.
        """
        __coef = {}
        for l in self.getScalarsVarianceList():
            __coef[l] = l
        length = len(__coef)
        Lscal = self.defaultScalarValues()['variance_label']

        # new scalar: default value for both scalar and diffusivity

        if not scalar_label:
            if length != 0:
                i = 1
                while (Lscal + str(i)) in list(__coef.values()):
                    i = i + 1
                num = str(i)
            else:
                num = str(1)
            scalar_label = Lscal + num
        return scalar_label


    def __updateScalarNameAndDiffusivityName(self):
        """
        Private method.
        Update suffixe number for scalar name and diffusivity' name.
        """
        lst = []
        n = 0
        for node in self.scalar_node.xmlGetNodeList('variable'):
            n = n + 1
            if node['type'] == 'user':
                node['name'] = 'user_' + str(n)
            nprop = node.xmlGetChildNode('property')
            if nprop:
                old_name = nprop['name']
                nprop['name'] = 'diffusion_coefficient_' + str(n)
                new_name = nprop['name']
                if old_name:
                    for no in self.case.xmlGetNodeList('formula'):
                        txt = no.xmlGetTextNode()
                        if txt != None:
                            f = txt.replace(old_name, new_name)
                            no.xmlSetTextNode(f)


    def __setScalarDiffusivity(self, scalar_label, coeff_label):
        """
        Private method.

        Input default initial value of property "diffusivity"
        for a new scalar I{scalar_label}
        """
        self.isNotInList(scalar_label, self.getScalarsVarianceList())
        self.isInList(scalar_label, self.getUserScalarLabelsList())

        n = self.scalar_node.xmlGetNode('variable', type='user', label=scalar_label)
        n.xmlInitChildNode('property', label=coeff_label)

        if not self.getScalarDiffusivityChoice(scalar_label):
            self.setScalarDiffusivityChoice(scalar_label, 'constant')

        if not self.getScalarDiffusivityInitialValue(scalar_label):
            ini = self.defaultScalarValues()['diffusion_coefficient']
            self.setScalarDiffusivityInitialValue(scalar_label, ini)


    def __deleteScalar(self, label):
        """
        Private method.

        Delete scalar I{label}.
        """
        node = self.scalar_node.xmlGetNode('variable', label=label)
        node.xmlRemoveNode()
        self.__deleteScalarBoundaryConditions(label)
        self.__updateScalarNameAndDiffusivityName()


    @Variables.noUndo
    def getThermalScalarLabelsList(self):
        """Public method.
        Return the User scalar label list (thermal scalar included)"""
        lst = []
        for node in self.node_therm.xmlGetNodeList('variable'):
            lst.append(node['label'])
        return lst


    @Variables.noUndo
    def getScalarLabelsList(self):
        """Public method.
        Return the User scalar label list (thermal scalar included)"""
        lst = []
        for node in self.scalar_node.xmlGetNodeList('variable'):
            lst.append(node['label'])
        return lst


    @Variables.noUndo
    def getMeteoScalarsList(self):
        node_list = []
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('atmospheric_flows', 'model')
        if node == None:
            return

        model = node['model']
        if model != 'off':
            node_list = node.xmlGetNodeList('variable')
            list_scalar=[]
            for node_scalar in node_list:
                list_scalar.append(node_scalar['label'])
        else:
            return

        return list_scalar


    @Variables.noUndo
    def getElectricalScalarsList(self):
        node_list = []
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('joule_effect', 'model')
        if node == None:
            return

        model = node['model']
        if model != 'off':
            node_list = node.xmlGetNodeList('variable')
            list_scalar=[]
            for node_scalar in node_list:
                list_scalar.append(node_scalar['label'])
        else:
            return

        return list_scalar


    @Variables.noUndo
    def getUserScalarLabelsList(self):
        """Public method.
        Return the user scalar label list (without thermal scalar).
        Method also used by UserScalarPropertiesView
        """
        lst = []
        for node in self.scalar_node.xmlGetNodeList('variable', type='user'):
            lst.append(node['label'])
        return lst


    @Variables.undoGlobal
    def setScalarBoundaries(self):
        """Public method.
        Input boundaries conditions for a scalar node. Method also used by ThermalScalarModel
        """
        from Pages.Boundary import Boundary

        for node in self.node_bc.xmlGetChildNodeList('inlet'):
            model = Boundary('inlet', node['label'], self.case)
            for label in self.getScalarLabelsList():
                model.setScalarValue(label, 'dirichlet', 0.0)

        for node in self.node_bc.xmlGetChildNodeList('outlet'):
            model = Boundary('outlet', node['label'], self.case)
            for label in self.getScalarLabelsList():
                model.setScalarValue(label, 'dirichlet', 0.0)


    @Variables.undoGlobal
    def addUserScalar(self, label=None):
        """Public method.
        Input a new user scalar I{label}"""

        l, c = self.__defaultScalarNameAndDiffusivityLabel(label)

        if l not in self.getScalarLabelsList() and l not in self.getThermalScalarLabelsList():
            self.scalar_node.xmlInitNode('variable', 'name', type="user", label=l)

            self.__setScalarDiffusivity(l, c)
            self.setScalarBoundaries()

        self.__updateScalarNameAndDiffusivityName()

        return l


    @Variables.undoGlobal
    def addVariance(self, label=None):
        """Public method.
        Input a new user scalar I{label}"""

        l= self.__defaultVarianceName(label)
        if l not in self.getScalarsVarianceList():
            self.scalar_node.xmlInitNode('variable', 'name', type="user", label=l)
            if self.getScalarLabelsList() != None:
                self.setScalarVariance(l, self.defaultScalarValues()['variance'])

        self.__updateScalarNameAndDiffusivityName()

        return l


    @Variables.undoLocal
    def renameScalarLabel(self, old_label, new_label):
        """Public method.
        Modify old_label of scalar with new_label and put new label if variancy exists"""
        # fusion de cette methode avec OutputVolumicVariablesModel.setVariablesLabel
        self.isInList(old_label, self.getScalarLabelsList())

        label = new_label[:LABEL_LENGTH_MAX]
        if label not in self.getScalarLabelsList():
            for node in self.scalar_node.xmlGetNodeList('variable'):
                if node['label'] == old_label:
                    node['label'] = label

                if node.xmlGetString('variance') == old_label:
                    node.xmlSetData('variance', label)

        for nature in ('inlet', 'outlet', 'wall'):
            for node in self.node_bc.xmlGetChildNodeList(nature):
                for n in node.xmlGetChildNodeList('variable'):
                    if n['label'] == old_label:
                        n['label'] = new_label

        for node in self.case.xmlGetNodeList('formula'):
            f = node.xmlGetTextNode().replace(old_label, new_label)
            node.xmlSetTextNode(f)


    @Variables.undoGlobal
    def setTurbulentFluxGlobalModel(self, TurbulenceModel):
        """Put turbulent flux model of an additional_scalar with label scalar_label"""
        lst = self.getScalarLabelsList() + self.getThermalScalarLabelsList()

        if TurbulenceModel not in ('Rij-epsilon', 'Rij-SSG', 'Rij-EBRSM'):
            mdl = self.defaultScalarValues()['GGDH']
            for var in lst:
                n = self.case.xmlGetNode('variable', label=var)
                n.xmlSetData('turbulent_flux_model', mdl)


    @Variables.noUndo
    def getTurbulentFluxModel(self, l):
        """
        Get turbulent flux model of an additional_scalar with label I{l}.
        """
        lst = self.getScalarLabelsList() + self.getThermalScalarLabelsList()
        self.isInList(l, lst)
        n = self.case.xmlGetNode('variable', label=l)
        mdl = n.xmlGetString('turbulent_flux_model')
        if not mdl:
            mdl = self.defaultScalarValues()['GGDH']
            self.setTurbulentFluxModel(l, mdl)

        return mdl


    @Variables.undoGlobal
    def setTurbulentFluxModel(self, scalar_label, TurbFlux):
        """Put turbulent flux model of an additional_scalar with label scalar_label"""
        lst = self.getScalarLabelsList() + self.getThermalScalarLabelsList()
        self.isInList(scalar_label, lst)

        n = self.case.xmlGetNode('variable', label=scalar_label)
        n.xmlSetData('turbulent_flux_model', TurbFlux)


    @Variables.noUndo
    def getScalarVariance(self, l):
        """
        Get variance of an additional_scalar with label I{l}.
        Method also used by UserScalarPropertiesView
        """
        self.isInList(l, self.getScalarLabelsList())

        return self.scalar_node.xmlGetNode('variable', label=l).xmlGetString('variance')


    @Variables.undoGlobal
    def setScalarVariance(self, scalar_label, variance_label):
        """Put variance of an additional_scalar with label scalar_label"""
        self.isInList(scalar_label, self.getUserScalarLabelsList())
        lst = self.getScalarLabelsList() + self.getThermalScalarLabelsList()
        self.isInList(variance_label, lst)

        n = self.scalar_node.xmlGetNode('variable', type='user', label=scalar_label)
        n.xmlSetData('variance', variance_label)

        self.__removeScalarChildNode(scalar_label, 'property')


    @Variables.noUndo
    def getScalarsWithVarianceList(self):
        """
        Return list of scalars which have a variance
        """
        lst = []
        for node in self.scalar_node.xmlGetNodeList('variable'):
            sca = node.xmlGetString('variance')
            if sca and sca not in lst:
                lst.append(sca)
        return lst


    @Variables.noUndo
    def getScalarsVarianceList(self):
        """
        Return list of scalars which are also a variance
        """
        lst = []
        for node in self.scalar_node.xmlGetNodeList('variable'):
            if node.xmlGetString('variance') and node['label'] not in lst:
                lst.append(node['label'])
        return lst


    @Variables.noUndo
    def getVarianceLabelFromScalarLabel(self, label):
        """
        Get the label of scalar with variancy's label: label
        """
        self.isInList(label, self.getScalarLabelsList())

        lab = ""
        for node in self.scalar_node.xmlGetNodeList('variable'):
            if node.xmlGetString('variance') == label:
                lab = node['label']
        return lab


    @Variables.noUndo
    def getScalarDiffusivityName(self, scalar_label):
        """
        Get label of diffusivity's property for an additional_scalar
        with label scalar_label
        """
        self.isInList(scalar_label, self.getScalarLabelsList())

        lab_diff = ""
        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n_diff = n.xmlGetChildNode('property')
        if n_diff:
            lab_diff = n_diff['name']

        return lab_diff


    @Variables.undoLocal
    def setScalarDiffusivityLabel(self, scalar_label, diff_label):
        """
        Set label of diffusivity's property for an additional_scalar
        """
        self.isInList(scalar_label, self.getScalarLabelsList())

        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n.xmlGetChildNode('property')['label'] = diff_label


    @Variables.noUndo
    def getScalarDiffusivityLabel(self, scalar_label):
        """
        Get label of diffusivity's property for an additional_scalar
        with label scalar_label
        """
        self.isInList(scalar_label, self.getScalarLabelsList())

        lab_diff = ""
        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n_diff = n.xmlGetChildNode('property')
        if n_diff:
            lab_diff = n_diff['label']

        return lab_diff


    @Variables.undoLocal
    def setScalarDiffusivityInitialValue(self, scalar_label, initial_value):
        """
        Set initial value of diffusivity's property for an additional_scalar
        with label scalar_label. Method also called by UserScalarPropertiesView.
        """
        self.isNotInList(scalar_label, self.getScalarsVarianceList())
        self.isInList(scalar_label, self.getUserScalarLabelsList())
        self.isFloat(initial_value)

        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n_diff = n.xmlInitChildNode('property')
        n_diff.xmlSetData('initial_value', initial_value)


    @Variables.noUndo
    def getScalarDiffusivityInitialValue(self, scalar_label):
        """
        Get initial value of diffusivity's property for an additional_scalar
        with label scalar_label. Method also called by UserScalarPropertiesView.
        """
        self.isNotInList(scalar_label, self.getScalarsVarianceList())
        self.isInList(scalar_label, self.getUserScalarLabelsList())

        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n_diff = n.xmlInitChildNode('property')
        diffu = n_diff.xmlGetDouble('initial_value')
        if diffu == None:
            diffu = self.defaultScalarValues()['diffusion_coefficient']
            self.setScalarDiffusivityInitialValue(scalar_label, diffu)

        return diffu


    @Variables.undoLocal
    def setScalarDiffusivityChoice(self, scalar_label, choice):
        """
        Set choice of diffusivity's property for an additional_scalar
        with label scalar_label
        """
        self.isNotInList(scalar_label, self.getScalarsVarianceList())
        self.isInList(scalar_label, self.getUserScalarLabelsList())
        self.isInList(choice, ('constant', 'variable'))

        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        n_diff = n.xmlInitChildNode('property')
        n_diff['choice'] = choice


    @Variables.noUndo
    def getScalarDiffusivityChoice(self, scalar_label):
        """
        Get choice of diffusivity's property for an additional_scalar
        with label scalar_label
        """
        self.isNotInList(scalar_label, self.getScalarsVarianceList())
        self.isInList(scalar_label, self.getUserScalarLabelsList())

        n = self.scalar_node.xmlGetNode('variable', label=scalar_label)
        choice = n.xmlInitChildNode('property')['choice']
        if not choice:
            choice = self.defaultScalarValues()['diffusion_choice']
            self.setScalarDiffusivityChoice(scalar_label, choice)

        return choice


    @Variables.noUndo
    def getDiffFormula(self, scalar):
        """
        Return a formula for I{tag} 'density', 'molecular_viscosity',
        'specific_heat' or 'thermal_conductivity'
        """
        self.isNotInList(scalar, self.getScalarsVarianceList())
        self.isInList(scalar, self.getUserScalarLabelsList())
        n = self.scalar_node.xmlGetNode('variable',label = scalar)
        node = n.xmlGetNode('property')
        formula = node.xmlGetString('formula')
        if not formula:
            formula = self.getDefaultFormula(scalar)
            self.setDiffFormula(scalar, formula)
        return formula


    @Variables.noUndo
    def getDefaultFormula(self, scalar):
        """
        Return default formula
        """
        self.isNotInList(scalar, self.getScalarsVarianceList())
        self.isInList(scalar, self.getUserScalarLabelsList())

        name = self.getScalarDiffusivityName(scalar)

        formula = str(name) + " ="

        return formula


    @Variables.undoLocal
    def setDiffFormula(self, scalar, str):
        """
        Gives a formula for 'density', 'molecular_viscosity',
        'specific_heat'or 'thermal_conductivity'
        """
        self.isNotInList(scalar, self.getScalarsVarianceList())
        self.isInList(scalar, self.getUserScalarLabelsList())
        n = self.scalar_node.xmlGetNode('variable',label = scalar)
        node = n.xmlGetNode('property')
        node.xmlSetData('formula', str)


    @Variables.undoGlobal
    def setScalarValues(self, label, vari):
        """
        Put values to scalar with labelled I{label} for creating or replacing values.
        """
        l = self.getScalarLabelsList()
        l.append('no')
        self.isInList(vari, l)

        if vari != "no":
            self.setScalarVariance(label, vari)
        else:
            self.__removeScalarChildNode(label, 'variance')
            l, c = self.__defaultScalarNameAndDiffusivityLabel(label)
            self.__setScalarDiffusivity(l, c)

        self.__updateScalarNameAndDiffusivityName()


    @Variables.undoGlobal
    def deleteScalar(self, slabel):
        """
        Public method.
        Delete scalar I{label}
        Warning: deleting a scalar may delete other scalar which are variances
        of previous deleting scalars.
        """
        self.isInList(slabel, self.getScalarLabelsList())

        # First add the main scalar to delete
        lst = []
        lst.append(slabel)

        # Then add variance scalar related to the main scalar
        for node in self.scalar_node.xmlGetNodeList('variable'):
            if node.xmlGetString('variance') == slabel:
                lst.append(node['label'])

        # Delete all scalars
        for scalar in lst:
            self.__deleteScalar(scalar)

        return lst


    @Variables.undoGlobal
    def deleteThermalScalar(self, slabel):
        """
        Public method.
        Delete scalar I{label}. Called by ThermalScalarModel
        Warning: deleting a scalar may delete other scalar which are variances
        of previous deleting scalars.
        """
        self.isInList(slabel, self.getThermalScalarLabelsList())

        # First add the main scalar to delete
        lst = []
        lst.append(slabel)

        # Then add variance scalar related to the main scalar
        for node in self.scalar_node.xmlGetNodeList('variable'):
            if node.xmlGetString('variance') == slabel:
                self.__deleteScalar(node['label'])

        # Delete scalars
        node = self.node_therm.xmlGetNode('variable', label=slabel)
        node.xmlRemoveNode()
        self.__deleteScalarBoundaryConditions(slabel)
        self.__updateScalarNameAndDiffusivityName()

        return lst


    @Variables.noUndo
    def getScalarType(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getScalarLabelsList() + self.getThermalScalarLabelsList())
        if scalar_label not in self.getScalarLabelsList():
            node = self.node_therm.xmlGetNode('variable', 'name', label=scalar_label)
        else:
            node = self.scalar_node.xmlGetNode('variable', 'type', label=scalar_label)
        Model().isInList(node['type'], ('user', 'thermal'))
        return node['type']


    @Variables.noUndo
    def getScalarName(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getScalarLabelsList() + self.getThermalScalarLabelsList())
        if scalar_label not in self.getScalarLabelsList():
            node = self.node_therm.xmlGetNode('variable', 'name', label=scalar_label)
        else:
            node = self.scalar_node.xmlGetNode('variable', 'name', label=scalar_label)
        return node['name']


    @Variables.noUndo
    def getMeteoScalarType(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getMeteoScalarsList())
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('atmospheric_flows', 'model')
        n = node.xmlGetNode('variable', 'type', label=scalar_label)
        Model().isInList(n['type'], ('user', 'thermal', 'model'))
        return n['type']


    @Variables.noUndo
    def getMeteoScalarName(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getMeteoScalarsList())
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('atmospheric_flows', 'model')
        n = node.xmlGetNode('variable', 'name', label=scalar_label)
        return n['name']


    @Variables.noUndo
    def getElectricalScalarType(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getElectricalScalarsList())
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('joule_effect', 'model')
        n = node.xmlGetNode('variable', 'type', label=scalar_label)
        Model().isInList(n['type'], ('user', 'thermal', 'model'))
        return n['type']


    @Variables.noUndo
    def getElectricalScalarName(self, scalar_label):
        """
        Return type of scalar for choice of color (for view)
        """
        self.isInList(scalar_label, self.getElectricalScalarsList())
        models = self.case.xmlGetNode('thermophysical_models')
        node = models.xmlGetNode('joule_effect', 'model')
        n = node.xmlGetNode('variable', 'name', label=scalar_label)
        return n['name']


#-------------------------------------------------------------------------------
# DefineUsersScalars test case
#-------------------------------------------------------------------------------


class UserScalarTestCase(ModelTest):
    """
    Unittest.
    """
    def checkDefineUserScalarsModelInstantiation(self):
        """Check whether the DefineUserScalarsModel class could be instantiated."""
        model = None
        model = DefineUserScalarsModel(self.case)

        assert model != None, 'Could not instantiate DefineUserScalarsModel'


    def checkAddNewUserScalar(self):
        """Check whether the DefineUserScalarsModel class could add a scalar."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')

        doc = '''<additional_scalars>
                    <variable label="toto" name="user_1" type="user">
                            <initial_value zone_id="1">0.0 </initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
           'Could not add a user scalar'

    def checkRenameScalarLabel(self):
        """Check whether the DefineUserScalarsModel class could set a label."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')
        model.addUserScalar(zone,'titi')
        model.renameScalarLabel('titi', 'MACHIN')

        doc = '''<additional_scalars>
                    <variable label="toto" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="MACHIN" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
           'Could not rename a label to one scalar'

    def checkGetThermalScalarLabel(self):
        """Check whether the DefineUserScalarsModel class could be get label of thermal scalar."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'usersca1')
        from Pages.ThermalScalarModel import ThermalScalarModel
        ThermalScalarModel(self.case).setThermalModel('temperature_celsius')
        del ThermalScalarModel

        doc = '''<additional_scalars>
                    <variable label="usersca1" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="TempC" name="temperature_celsius" type="thermal">
                            <initial_value zone_id="1">20.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                    </variable>
                </additional_scalars>'''

        model.renameScalarLabel("TempC", "Matemperature")

        assert model.getThermalScalarLabel() == "Matemperature",\
           'Could not get label of thermal scalar'

    def checkSetAndGetScalarInitialValue(self):
        """Check whether the DefineUserScalarsModel class could be set and get initial value."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')
        model.setScalarInitialValue(zone, 'toto', 0.05)

        doc = '''<additional_scalars>
                    <variable label="toto" name="user_1" type="user">
                            <initial_value zone_id="1">0.05</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not set initial value to user scalar'
        assert model.getScalarInitialValue(zone, 'toto') == 0.05,\
            'Could not get initial value to user scalar'

    def checkSetAndGetScalarMinMaxValue(self):
        """Check whether the DefineUserScalarsModel class could be set and get min and max value."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')
        model.addUserScalar(zone, 'titi')
        model.setScalarInitialValue(zone, 'toto', 0.05)
        model.setScalarMinValue('toto',0.01)
        model.setScalarMaxValue('titi',100.)

        doc = '''<additional_scalars>
                    <variable label="toto" name="user_1" type="user">
                            <initial_value zone_id="1">0.05</initial_value>
                            <min_value>0.01</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="titi" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>100.</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not set minimal or maximal value to user scalar'
        assert model.getScalarMinValue('toto') == 0.01,\
            'Could not get minimal value from user scalar'
        assert model.getScalarMaxValue('titi') == 100.,\
            'Could not get maximal value from user scalar'

    def checkSetAndGetScalarVariance(self):
        """Check whether the DefineUserScalarsModel class could be set and get variance of scalar."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')
        model.addUserScalar(zone, 'titi')
        model.setScalarVariance('toto', 'titi')

        doc = '''<additional_scalars>
                    <variable label="toto" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>0</min_value>
                            <max_value>1e+12</max_value>
                            <variance>titi</variance>
                    </variable>
                    <variable label="titi" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not set variance to user scalar'
        assert model.getScalarVariance('toto') == 'titi',\
            'Could not get variance of user scalar'

    def checkGetVarianceLabelFromScalarLabel(self):
        """
        Check whether the DefineUserScalarsModel class could be get label of
        the scalar which has variancy.
        """
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'toto')
        model.addUserScalar(zone, 'titi')
        model.setScalarVariance('toto', 'titi')

        assert model.getVarianceLabelFromScalarLabel('titi') == 'toto',\
            'Could not get label of scalar whiwh has a variancy'

    def checkGetScalarDiffusivityLabel(self):
        """
        Check whether the DefineUserScalarsModel class could be get label of
        diffusivity of user scalar.
        """
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'premier')
        model.addUserScalar(zone, 'second')

        doc = '''<additional_scalars>
                    <variable label="premier" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>0</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="second" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.getScalarDiffusivityLabel('second') == "Dscal2",\
            'Could not get label of diffusivity of one scalar'

    def checkSetandGetScalarDiffusivityInitialValue(self):
        """
        Check whether the DefineUserScalarsModel class could be set
        and get initial value of diffusivity.
        """
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'premier')
        model.addUserScalar(zone, 'second')
        model.setScalarDiffusivityInitialValue('premier', 0.555)

        doc = '''<additional_scalars>
                    <variable label="premier" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>0.555</initial_value>
                            </property>
                    </variable>
                    <variable label="second" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not set initial value of property of one user scalar'
        assert model.getScalarDiffusivityInitialValue('premier') == 0.555,\
            'Could not get initial value of property of one user scalar '

    def checkSetandGetScalarDiffusivityChoice(self):
        """Check whether the DefineUserScalarsModel class could be set and get diffusivity's choice."""
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'premier')
        model.addUserScalar(zone, 'second')
        model.setScalarDiffusivityChoice('premier', 'variable')
        doc = '''<additional_scalars>
                    <variable label="premier" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="variable" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="second" name="user_2" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal2" name="diffusion_coefficient_2">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not set choice of property of one user scalar'
        assert model.getScalarDiffusivityChoice('premier') == "variable",\
            'Could not get choice of property of one user scalar'

    def checkDeleteScalarandGetScalarType(self):
        """
        Check whether the DefineUserScalarsModel class could be
        delete a user scalar and get type of the scalar.
        """
        model = DefineUserScalarsModel(self.case)
        zone = '1'
        model.addUserScalar(zone, 'premier')

        from Pages.ThermalScalarModel import ThermalScalarModel
        ThermalScalarModel(self.case).setThermalModel('temperature_celsius')
        del ThermalScalarModel

        model.addUserScalar(zone, 'second')
        model.addUserScalar(zone, 'troisieme')
        model.addUserScalar(zone, 'quatrieme')

        assert model.getScalarType('premier') == 'user',\
            'Could not get type of one scalar'

        model.deleteScalar('second')

        doc = '''<additional_scalars>
                    <variable label="premier" name="user_1" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal1" name="diffusion_coefficient_1">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="TempC" name="temperature_celsius" type="thermal">
                            <initial_value zone_id="1">20.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                    </variable>
                    <variable label="troisieme" name="user_3" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal4" name="diffusion_coefficient_3">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                    <variable label="quatrieme" name="user_4" type="user">
                            <initial_value zone_id="1">0.0</initial_value>
                            <min_value>-1e+12</min_value>
                            <max_value>1e+12</max_value>
                            <property choice="constant" label="Dscal5" name="diffusion_coefficient_4">
                                    <initial_value>1.83e-05</initial_value>
                            </property>
                    </variable>
                </additional_scalars>'''

        assert model.scalar_node == self.xmlNodeFromString(doc),\
            'Could not delete one scalar'



def suite():
    """unittest function"""
    testSuite = unittest.makeSuite(UserScalarTestCase, "check")
    return testSuite


def runTest():
    """unittest function"""
    print("UserScalarTestTestCase")
    runner = unittest.TextTestRunner()
    runner.run(suite())


#-------------------------------------------------------------------------------
# End DefineUsersScalars
#-------------------------------------------------------------------------------
