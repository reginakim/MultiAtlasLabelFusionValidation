###############################################################################
# Author: Eun Young (Regina) Kim


# export PYTHONPATH=/ipldev/scratch/eunyokim/src/BRAINS201308/BRAINSTools/AutoWorkup/:/ipldev/scratch/eunyokim/src/nipype/nipype-0.8:/ipldev/scratch/eunyokim/src/BRAINS201308/build/lib:
# export PATH=/ipldev/scratch/eunyokim/src/BRAINS201308/buildNamic/UKF-build/ukf/bin/:/ipldev/scratch/eunyokim/src/BRAINS201308/build/bin/:$PATH

## TODO Change "OutputDir" --> . so that duplicate directories of Workflow and OutputDir created.

def ReconstructDictionary( inputKeys,
                           inputElements ):
    import sys
    if len( inputKeys ) != len( inputElements ) :
        print """ERROR! length of inputKeys ({0}) has to equal 
            to one of inputElements ({1}).""".format( len( inputKeys ), len( inputElements ) )
        sys.exit(0)
    outputDictionary = dict( )
    outputAdditionalImages = []
    for key, element in zip( inputKeys, inputElements ):
        if( key == 'additionalImages' ):
            outputAdditionalImages.append( element )
        else:
            outputDictionary[ key ] = element
    outputDictionary[ 'additionalImages' ] = outputAdditionalImages

    print "Return reconstructed dictionary..."
    print outputDictionary 
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    return outputDictionary


def WarpSubjectToAtlas( WFName, 
                        inputDictionaries,
                        inputAtlasFilename,
                        outputDirectory):
    """ 
       Bring all the training set into BRAINSTools Atlas Space
    """
    import os
    import nipype.interfaces.io as nio
    import nipype.pipeline.engine as pe
    
    from SEMTools import BRAINSFit, BRAINSResample 

    WarpToAtlasWF = pe.Workflow( name=WFName )
    WarpToAtlasWF.base_dir = outputDirectory

    BFitSubjectToAtlasND = pe.Node( interface=BRAINSFit(), name="BFitSubjectToAtlas")
    BFitSubjectToAtlasND.inputs.costMetric = "MMI"

    BFitSubjectToAtlasND.inputs.maskProcessingMode = "ROIAUTO" 
    BFitSubjectToAtlasND.inputs.numberOfSamples = 500000 
    BFitSubjectToAtlasND.inputs.numberOfIterations = 10000 
    BFitSubjectToAtlasND.inputs.numberOfHistogramBins = 100 
    BFitSubjectToAtlasND.inputs.maximumStepLength = 0.2 
    BFitSubjectToAtlasND.inputs.minimumStepLength = [ 0.0025,0.0025,0.0025,0.0025 ]

    BFitSubjectToAtlasND.inputs.useRigid = True
    BFitSubjectToAtlasND.inputs.useScaleVersor3D = True
    BFitSubjectToAtlasND.inputs.useScaleSkewVersor3D = True
    BFitSubjectToAtlasND.inputs.useAffine = True

    BFitSubjectToAtlasND.inputs.relaxationFactor = 0.5 
    BFitSubjectToAtlasND.inputs.translationScale = 1000 
    BFitSubjectToAtlasND.inputs.reproportionScale = 1 
    BFitSubjectToAtlasND.inputs.skewScale = 1 
    BFitSubjectToAtlasND.inputs.useExplicitPDFDerivativesMode = "AUTO" 
    BFitSubjectToAtlasND.inputs.projectedGradientTolerance = 1e-05 
    BFitSubjectToAtlasND.inputs.costFunctionConvergenceFactor = 1e+09 
    BFitSubjectToAtlasND.inputs.backgroundFillValue = 0 
    BFitSubjectToAtlasND.inputs.maskInferiorCutOffFromCenter = 1000 

    BFitSubjectToAtlasND.inputs.outputTransform = "subjectToAtlas.h5" 
    BFitSubjectToAtlasND.inputs.outputVolume = "subjectToAtlasBaselineVolume.nii.gz" 

    ''' 
      I/O
    '''
    BFitSubjectToAtlasND.inputs.fixedVolume = inputAtlasFilename
    BFitSubjectToAtlasND.inputs.movingVolume = inputDictionaries[ 'baselineImage' ]

    WarpToAtlasWF.add_nodes( [BFitSubjectToAtlasND] )

    ResampleND = pe.Node( interface=BRAINSResample(), name="ResampleToAtlas" )
    ResampleND.inputs.interpolationMode = "Linear"
    ResampleND.inputs.referenceVolume = inputAtlasFilename
    ResampleND.inputs.outputVolume = "subjectToAtlasAdditionalImage.nii.gz"

    if len( inputDictionaries[ 'additionalImages' ]) >0 :
        WarpToAtlasWF.connect( BFitSubjectToAtlasND, 'outputTransform', 
                               ResampleND, 'warpTransform')

    ResampleND.iterables = ( 'inputVolume', list( inputDictionaries[ 'additionalImages' ] ) )

    WarpToAtlasWF.write_graph()
    WarpToAtlasWF.run()

def ClipVolumeWithMask( inputVolumeFilename,
                inputMaskFilename,
                inputType,
                outputVolumeFilename ):
    import sys
    import os
    import SimpleITK as sitk
    
    try:
        maskVolume  = sitk.ReadImage( inputMaskFilename )
        binaryMaskVolume = sitk.BinaryThreshold( maskVolume, 1, 255 )

        inputVolume = sitk.ReadImage( inputVolumeFilename )

        binaryMaskVolume = sitk.Cast( binaryMaskVolume, inputVolume.GetPixelIDValue() )
        outputVolume = binaryMaskVolume * inputVolume

        sitk.WriteImage( outputVolume, outputVolumeFilename)
        outputVolumePath = os.path.abspath( outputVolumeFilename )
    except IOError as e:
        print "I/O error({0}: {1}".format(e.errno, e.strerror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    print "return value is [ {0}: {1} ]".format(inputType, outputVolumePath)
    return [inputType, outputVolumePath] 

def ExtractImageList ( inputDictionaries, 
                       desiredKeys ):
    outputImageList = []
    outputTypeList = []
    for key in desiredKeys:
        if key in inputDictionaries.keys():
            print "- Extract " + str( key ) + ", " + str( inputDictionaries[key] ) 
            if type( inputDictionaries[ key ] ) is list:
                for element in inputDictionaries[ key ]:
                    print "-- add element of " + str( element )
                    outputImageList.append( element )
                    outputTypeList.append( key )
            else:
                print "-- add element of " + str( inputDictionaries[ key ] )
                outputImageList.append( inputDictionaries[ key ] )
                outputTypeList.append( key )
                
        else:
            print str(key) + " does not exist in dictionary."

    return outputImageList, outputTypeList

def PreprocessingMALF( WFName,
                      inputDictionaries,
                      inputAtlasFilename,
                      outputDir
                    ):

    from nipype import config
    config.enable_debug_mode()
    print """ Run WarpSubjectsIntoAtlasWF"""
    import os
    import nipype.interfaces.io as nio
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function, IdentityInterface
    from PipeLineFunctionHelpers import  POSTERIORS
    from WorkupT1T2TissueClassify import MakePosteriorDictionaryFunc

    PreprocessingWF= pe.Workflow( name=WFName)
    PreprocessingWF.base_dir = outputDir

    #inputAtlasFilename = inputAtlasDir+ "template_t1_clipped.nii.gz"

    """
      Clip Brain 
    """

    """
      - extract image list from dictionaries 
    """
    InputImageListND =pe.Node( interface = Function( function = ExtractImageList,
                                                     input_names = ['inputDictionaries', 
                                                                    'desiredKeys'],
                                                     output_names = ['outputImageList',
                                                                     'outputTypeList']),
                               name='InputImageList')
    InputImageListND.inputs.inputDictionaries = inputDictionaries
    InputImageListND.inputs.desiredKeys = ['baselineImage', 'additionalImages', 'labelMap']

    BrainClipND = pe.MapNode( interface = Function( function = ClipVolumeWithMask,
                                                    input_names = ['inputVolumeFilename',
                                                                   'inputMaskFilename',
                                                                   'inputType',
                                                                   'outputVolumeFilename'] ,
                                                    output_names = ['outputType',
                                                                    'outputVolume']),
                              iterfield=['inputVolumeFilename', 'inputType'],
                              name="BrainClip")

    BrainClipND.inputs.inputMaskFilename = inputDictionaries[ 'brainMask' ] 
    PreprocessingWF.connect( [ (InputImageListND, BrainClipND, [ ('outputImageList', 'inputVolumeFilename') ] ),
                               (InputImageListND, BrainClipND, [ ('outputTypeList', 'inputType') ] ) 
                           ] )
    BrainClipND.inputs.outputVolumeFilename = "SubjectBrainClipped.nii.gz"

    """
      Reconstruct input Dictionaries
    """
    ReconstructDictND = pe.Node( interface = Function( function = ReconstructDictionary,
                                                       input_names = [ 'inputKeys','inputElements'],
                                                       output_names = [ 'outputDictionary'] ),
                                 name = 'ReconstructDict' )

    PreprocessingWF.connect( BrainClipND, 'outputType',
                             ReconstructDictND, 'inputKeys')
    PreprocessingWF.connect( BrainClipND, 'outputVolume',
                             ReconstructDictND, 'inputElements')

    """
      Warp all the subject image into atlas space
    """
    WarpSubjectToAtlasND = pe.Node( interface = Function( function = WarpSubjectToAtlas,
                                                          input_names = [ 'WFName', 
                                                                          'inputDictionaries',
                                                                          'inputAtlasFilename',
                                                                          'outputDirectory' ],
                                                          output_names = [] ),
                                    name = 'WarpSubjectToAtlas' )

    WarpSubjectToAtlasND.inputs.WFName = 'WarpSubjectToAtlasWF'

    PreprocessingWF.connect( ReconstructDictND, 'outputDictionary',
                             WarpSubjectToAtlasND, 'inputDictionaries') 

    WarpSubjectToAtlasND.inputs.inputAtlasFilename = inputAtlasFilename
    WarpSubjectToAtlasND.inputs.outputDirectory = '.'

    PreprocessingWF.write_graph()
    PreprocessingWF.run()

def BatchPreprocessing( WFName,
                        listOfDictionariesFilename,
                        atlasFilename,
                        outputDirectory ):
    
    """ 
      NOTE: This could not be implemented in NIPYPE
        due to the length of character restriction
        in the shell
    """

    listOfDictionaries = []


    import ast
    with open( listOfDictionariesFilename ) as f:
        for line in f:
            listOfDictionaries.append( ast.literal_eval( line ) )

    '''
    print and check read-in dictionaries
    '''
    for line in listOfDictionaries:
        for key in line.iterkeys():
            print "( {0}, {1} )".format( key, line[key] )
    from sets import Set
    import sys
    requiredInput = Set( [ 'baselineImage', 'labelMap', 'brainMask' ] )

    if not Set( line.iterkeys() ).issuperset( requiredInput ):
        print "Input specification requires (" + str( requiredInput ) + ")."
        print "Following element(s) seem(s) missing:"
        print requiredInput.difference( Set( line.iterkeys() ) )
        sys.exit(0)
    
    count = 1
    for singleSubject in listOfDictionaries:
        print "*** Process " 
        print singleSubject
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        PreprocessingMALF( WFName + "_" + str(count),
                           singleSubject, 
                           atlasFilename, 
                           outputDirectory + "_" + str(count) ) 


def UnitTest()    :
    my_WFName="PreprocessingMALF_UnitTest"
    my_oneSubject = {'baselineImage': '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/10335/TissueClassify/BABC/t1_average_BRAINSABC.nii.gz',
                     'additionalImages': ['/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/10335/TissueClassify/BABC/t2_average_BRAINSABC.nii.gz'],
                     'labelMap': '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/Manuals/BasalGangliaLabelMaps/10335_basalGanglia_EDIT.nii.gz',
                     'brainMask' : '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/10335/TissueClassify/BABC/brain_label_seg.nii.gz'}
    my_inputList=[ {'baselineImage': ['/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/10335/TissueClassify/BABC/t1_average_BRAINSABC.nii.gz'],
                    'labelMap': '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/Manuals/BasalGangliaLabelMaps/10335_basalGanglia_EDIT.nii.gz',
                    'brainMask' : '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/10335/TissueClassify/BABC/brain_label_seg.nii.gz'},
                   {'baselineImage': ['/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/11506/TissueClassify/BABC/t1_average_BRAINSABC.nii.gz'],
                    'labelMap': '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/Manuals/BasalGangliaLabelMaps/11506_basalGanglia_EDIT.nii.gz',
                    'brainMask' : '/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/11506/TissueClassify/BABC/brain_label_seg.nii.gz'}
                 ]
    my_atlas='/Shared/sinapse/scratch/eunyokim/src/BRAINS201308/build/ReferenceAtlas-build/Atlas/Atlas_20130711/template_t1_clipped.nii.gz'
    my_outputDir='/Shared/johnsonhj/HDNI/20130911_MultiLabel_Validation/WFTest'

    PreprocessingMALF( my_WFName + "_Single",
                      my_oneSubject,
                      my_atlas,
                      my_outputDir + "_Single")

    BatchPreprocessing( my_WFName+"_Batch",
                        my_inputList, 
                        my_atlas,
                        my_outputDir + "_Batch")

""" 
  call the workflow function
"""
import sys

def main(argv=None):
    ## todo: make this argument optional.
    ## UnitTest()

    #-------------------------------- argument parser  
    import argparse
    argParser = argparse.ArgumentParser( description="Parse argument for preprocessing")
    
    argParser.add_argument('--workflowName', help='A workflow name',
                           dest='workflowName', required =False, default='MALFPreprocessingWF')
    argParser.add_argument('--inputListFilename', help='A file name contains input list',
                           dest='inputListFilename', required = True)
    argParser.add_argument('--inputAtlas', help='A input template atlas with brain clipped',
                           dest='inputAtlas', required = True)
    argParser.add_argument('--outputDirectory', help='A directory that will contain output',
                           dest='outputDirectory', required = False, default=".")
    
    args = argParser.parse_args() 

    # nipype requires an absolute path in general
    import os
    absoluteOutputDirectory = os.path.abspath( args.outputDirectory )

    BatchPreprocessing( args.workflowName,
                        args.inputListFilename, 
                        args.inputAtlas, 
                        absoluteOutputDirectory )


if __name__ == "__main__":
    sys.exit(main())

