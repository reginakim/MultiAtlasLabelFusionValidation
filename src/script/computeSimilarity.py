# export PYTHONPATH=/ipldev/scratch/eunyokim/src/BRAINS201308/BRAINSTools/AutoWorkup/:/ipldev/scratch/eunyokim/src/nipype/nipype-0.8:/ipldev/scratch/eunyokim/src/BRAINS201308/build/lib:
# export PATH=/ipldev/scratch/eunyokim/src/BRAINS201308/buildNamic/UKF-build/ukf/bin/:/ipldev/scratch/eunyokim/src/BRAINS201308/build/bin/:$PATH

labelDictionary={24:'l_accumben',
                 21:'l_caudate',
                 22:'l_putamen',
                 23:'l_globus',
                 25:'l_hippocampus',
                 26:'l_thalamus',
                 34:'r_accumben',
                 31:'r_caudate',
                 32:'r_putamen',
                 33:'r_globus',
                 35:'r_hippocampus',
                 36:'r_thalamus'
                 }


#########################################################################################

def printImageInfo(img):
    import SimpleITK as sitk
    print("""Image info:::
          spacing: {sp}
          pixelID: {pid}
          dimension: {d}
          """.format( sp=img.GetSpacing(),
                      pid=img.GetPixelIDValue(),
                      d=img.GetDimension()))

#########################################################################################

def getLabelVolume(img, label=1):
    import SimpleITK as sitk
    binary = sitk.BinaryThreshold(img, label, label)
    stat = sitk.LabelStatisticsImageFilter()
    stat.Execute(binary, binary)
    try:
        count = stat.GetCount(1)
    except:
        count = 0
        pass
    volume = count * (img.GetSpacing()[0] * img.GetSpacing()[1] * img.GetSpacing()[2])
    print( """Computed volume is
            {vl} mm^3""".format( vl=volume ))
    return volume

#########################################################################################

def computeSimilarity(autoFilename, refFilename, outputCSVFilename):
    import SimpleITK as sitk
    import os
    import computeSimilarity as this                                                                                                      
    print( """ compute similarity between :
           {0} and {1}""".format( autoFilename, refFilename))

    autoImg = sitk.Cast( sitk.ReadImage(autoFilename), sitk.sitkUInt8 )
    refImg =  sitk.Cast( sitk.ReadImage(refFilename), sitk.sitkUInt8 )
    
    this.printImageInfo(autoImg)
    this.printImageInfo(refImg)

    stat = sitk.LabelStatisticsImageFilter()
    stat.Execute(autoImg, autoImg)

    print "*** compute similarity of valid labels in: *** "
    print stat.GetValidLabels()
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    listOUT=[]
    for labelNo in stat.GetValidLabels():
        print"***  compute label of {0} ***".format(labelNo)
        labelImg1 = sitk.BinaryThreshold( autoImg, labelNo, labelNo )
        #sitk.WriteImage( labelImg1, "DebugLabel_Img1_" + str( labelNo ) + ".nii.gz")
        labelImg2 = sitk.BinaryThreshold( refImg, labelNo, labelNo )
        #sitk.WriteImage( labelImg2, "DebugLabel_Img2_" + str( labelNo ) + ".nii.gz")

        OUT = {}
        if labelNo in labelDictionary:
            OUT['roi'] = labelDictionary[ labelNo ]
        else:
            OUT['roi'] = 'unknown label (' + str(labelNo) + ' )'

        OUT['autoVol'] = this.getLabelVolume(labelImg1)
        OUT['refVol'] = this.getLabelVolume(labelImg2)

        OUT['union'] = this.getLabelVolume(labelImg1 | labelImg2)
        OUT['intersection'] = this.getLabelVolume(labelImg1 & labelImg2)
        OUT['TP'] = OUT['union']
        OUT['FP'] = this.getLabelVolume(labelImg1 - labelImg2, 1)

        OUT['Precision'] = OUT['TP'] / (OUT['TP'] + OUT['FP'])
        OUT['RelativeOverlap'] = OUT['intersection'] / OUT['union']
        OUT['SimilarityIndex'] = 2 * OUT['intersection'] / (OUT['autoVol'] + OUT['refVol'])

        if OUT['autoVol'] != 0:
            hausdorffFilter = sitk.HausdorffDistanceImageFilter()
            hausdorffFilter.Execute(labelImg1, labelImg2)
            OUT['Hausdorff'] = hausdorffFilter.GetHausdorffDistance()
            OUT['HausdorffAvg'] = hausdorffFilter.GetAverageHausdorffDistance()
        else:
            OUT['Hausdorff'] = -1
            OUT['HausdorffAvg'] = -1

        for ele in OUT.iterkeys():
            print("{e} = {v}".format(e=ele, v=OUT[ele]))

        listOUT.append( OUT )

    import csv
    f = open(outputCSVFilename, 'wb')
    dict_writer = csv.DictWriter(f, OUT.keys() )
    dict_writer.writer.writerow( OUT.keys() )
    dict_writer.writerows( listOUT )

    return OUT

def unitTest():
    print "*** start unit testing *** "
    return True
def main(argv=None):
    import os
    import sys

    from nipype import config
    config.enable_debug_mode()
    #-------------------------------- argument parser
    import argparse
    argParser = argparse.ArgumentParser( description="""****************************
        similarity computation between two labels 
        """)
    # workup arguments
    argParser.add_argument('--labelMapFilename1',
                          help="""a filename that will be compared to. """,
                          dest='labelMapFilename1', required=False)

    argParser.add_argument('--labelMapFilename2',
                          help="""a filename that will be compared to. """,
                          dest='labelMapFilename2', required=False)

    argParser.add_argument('--outputCSVFilename',
                          help="""a filename that will store comparative results to. """,
                          dest='outputCSVFilename', required=False)

    argParser.add_argument('--doUnitTest', action='store_true',
                          help="""Do unit test if given""",
                          dest='doUnitTest', required=False)
    args = argParser.parse_args()

    action=False
    if args.doUnitTest :
        unitTest()
        action=True
    if args.labelMapFilename1 or args.labelMapFilename2:
        print os.path.abspath( args.labelMapFilename1 )
        print os.path.abspath( args.labelMapFilename2 )
        print os.path.abspath( args.outputCSVFilename )
        computeSimilarity( os.path.abspath( args.labelMapFilename1 ), 
                           os.path.abspath( args.labelMapFilename2 ),
                           os.path.abspath( args.outputCSVFilename ) )
        action=True
    if not action:
        print """        ***
        No action was required. Please either set 'doUnitTest' for 
          the series of unit tests or set labelMapFilename 1 and 2
          for similarity computation between two label maps
        ***"""
      
import sys

if __name__ == "__main__":
    sys.exit(main())

