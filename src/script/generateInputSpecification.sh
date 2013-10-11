inputFile=$1

if [[ -z $inputFile ]]; then
    inputFile=/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/scans.list
fi

while read site subject session
do
  t1="/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/$session/TissueClassify/BABC/t1_average_BRAINSABC.nii.gz"
  t2="/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/$session/TissueClassify/BABC/t2_average_BRAINSABC.nii.gz"
  labelMap="/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/Manuals/BasalGangliaLabelMaps/${session}_basalGanglia_EDIT.nii.gz"
  brainMask="/Shared/johnsonhj/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/AW_20120801.SubjectOrganized_Results/BAW_20120801.SubjectOrganized_Results/${session}/TissueClassify/BABC/brain_label_seg.nii.gz"

  echo "{'baselineImage':['$t1'], \
         'additionalImages':['$t2'],\
         'labelMap':'$labelMap',\
         'brainMask':'$brainMask'}"
done < $inputFile
