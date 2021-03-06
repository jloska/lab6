import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# lab6
#

class lab6(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "lab6" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# lab6Widget
#

class lab6Widget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...
#
    # Rozwijana lista Area
    #
    listCollapsibleButton = ctk.ctkCollapsibleButton()
    listCollapsibleButton.text = "Rozwijana lista"
    self.layout.addWidget(listCollapsibleButton)

    # Layout within the dummy collapsible button
    listFormLayout = qt.QFormLayout(listCollapsibleButton)

    #
    # input hide selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Wybieranie modelu do wczytania." )
    listFormLayout.addRow("Wybierz model: ", self.inputSelector)

    #
    # opacity value
    #
    self.imageOpacitySliderWidget = ctk.ctkSliderWidget()
    self.imageOpacitySliderWidget.singleStep = 1
    self.imageOpacitySliderWidget.minimum = 0
    self.imageOpacitySliderWidget.maximum = 100
    self.imageOpacitySliderWidget.value = 0
    self.imageOpacitySliderWidget.setToolTip("Ustaw przezroczystosc modelu 3D.")
    listFormLayout.addRow("Przezroczystosc (widocznosc)", self.imageOpacitySliderWidget)

    #
    # Show/hide Button
    #
    self.showHideButton = qt.QPushButton("Pokaz/Ukryj")
    self.showHideButton.toolTip = "Ukryj lub pokaz model"
    self.showHideButton.enabled = True
    listFormLayout.addRow(self.showHideButton)
    
    # connections
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.showHideButton.connect('clicked(bool)', self.onShowHideButton)
    self.imageOpacitySliderWidget.connect('valueChanged(double)', self.onOpacityChange)
  
  def onSelect(self):
    self.showHideButton.enabled = self.inputSelector.currentNode()

  def onShowHideButton(self):
    logic = lab6Logic()
    logic.showHideButtonClicked(self.inputSelector.currentNode())

  def onOpacityChange(self):
    logic = lab6Logic()
    opacityValue = self.imageOpacitySliderWidget.value
    logic.opacityChange(self.inputSelector.currentNode(), opacityValue)


#
# lab6Logic
#

class lab6Logic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def showHideButtonClicked(self, inputSelector):
    display = inputSelector.GetDisplayNode()
    display.SetVisibility(not display.GetVisibility())

  def opacityChange(self, inputSelector, opacityValue):
    display = inputSelector.GetDisplayNode()
    display.SetOpacity(opacityValue/100)
  
  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0,):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('lab6Test-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class lab6Test(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_lab61()

  def test_lab61(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = lab6Logic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
