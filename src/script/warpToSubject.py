###############################################################################
# Author: Eun Young (Regina) Kim


# export PYTHONPATH=/ipldev/scratch/eunyokim/src/BRAINS201308/BRAINSTools/AutoWorkup/:/ipldev/scratch/eunyokim/src/nipype/nipype-0.8:/ipldev/scratch/eunyokim/src/BRAINS201308/build/lib:
# export PATH=/ipldev/scratch/eunyokim/src/BRAINS201308/buildNamic/UKF-build/ukf/bin/:/ipldev/scratch/eunyokim/src/BRAINS201308/build/bin/:$PATH


def WarpToSubject( WFName, 
                   inputSubjectFilename,
                   inputLabelFilename,
                   inputWarpTransformFilename,
                   referenceSubjectFilename,
                   outputDirectory):
    """ 
       Bring all the training set into BRAINSTools Atlas Space
    """
    import os
    import nipype.interfaces.io as nio
    import nipype.pipeline.engine as pe
    
    from SEMTools import BRAINSFit, BRAINSResample 

    WarpToSubjectWF = pe.Workflow( name=WFName )
    WarpToSubjectWF.base_dir = outputDirectory

    '''
    warp corresponding images
    '''
    ResampleND = pe.Node( interface=BRAINSResample(), name="ResampleToSubject" )
    ResampleND.inputs.interpolationMode = "Linear"
    ResampleND.inputs.referenceVolume = referenceSubjectFilename 
    ResampleND.inputs.outputVolume = "toSubjectSpaceBaselineImage.nii.gz"
    ResampleND.inputs.warpTransform = inputWarpTransformFilename
    ResampleND.inputs.inputVolume = inputSubjectFilename

    WarpToSubjectWF.add_nodes( [ResampleND] )

    '''
    warp corresponding label image
    '''
    ResampleLabelND = pe.Node( interface=BRAINSResample(), name="ResampleLabelToSubjectSpace" )
    ResampleLabelND.inputs.interpolationMode = "NearestNeighbor"
    ResampleLabelND.inputs.referenceVolume = referenceSubjectFilename 
    ResampleLabelND.inputs.outputVolume = "subjectSpaceLabelMap.nii.gz"
    ResampleLabelND.inputs.pixelType = 'int'
    ResampleLabelND.inputs.warpTransform = inputWarpTransformFilename
    ResampleLabelND.inputs.inputVolume = inputLabelFilename

    WarpToSubjectWF.add_nodes( [ResampleLabelND] )

    WarpToSubjectWF.write_graph()
    WarpToSubjectWF.run()

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
                           dest='workflowName', required =False, default='MALFPostprocessingWF')
    argParser.add_argument('--inputSubjectFilename', help='A file name for the baseline input subject image',
                           dest='inputSubjectFilename', required = True)
    argParser.add_argument('--inputLabelFilename', help='A file name for the input labelmap',
                           dest='inputLabelFilename', required = True)
    argParser.add_argument('--inputWarpTransformFilename', help='''A file name for warping 
                              transform to be applied on the inputSubject and inputLabel''',
                           dest='inputWarpTransformFilename', required = True)
    argParser.add_argument('--referenceSubjectFilename', help='A file name for the input labelmap',
                           dest='referenceSubjectFilename', required = True)
    argParser.add_argument('--outputDirectory', help='The output directory of this workflow',
                           dest='outputDirectory', required = True)
    
    args = argParser.parse_args() 

    # nipype requires an absolute path in general
    import os

    WarpToSubject( args.workflowName,
                   os.path.abspath( args.inputSubjectFilename ), 
                   os.path.abspath( args.inputLabelFilename ),
                   os.path.abspath( args.inputWarpTransformFilename ), 
                   os.path.abspath( args.referenceSubjectFilename ),
                   os.path.abspath( args.outputDirectory) )


if __name__ == "__main__":
    sys.exit(main())

