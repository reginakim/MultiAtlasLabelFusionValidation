export PYTHONPATH=/ipldev/scratch/eunyokim/src/BRAINS201308/BRAINSTools/AutoWorkup/:/ipldev/scratch/eunyokim/src/nipype/nipype-0.8:/ipldev/scratch/eunyokim/src/BRAINS201308/build/lib:
export PATH=/ipldev/scratch/eunyokim/src/BRAINS201308/buildNamic/UKF-build/ukf/bin/:/ipldev/scratch/eunyokim/src/BRAINS201308/build/bin/:$PATH

python ../src/nipype/prepareMultiLabel.py --workflowName "TEST" \
  --inputAtlas /Shared/sinapse/scratch/eunyokim/src/BRAINS201308/build/ReferenceAtlas-build/Atlas/Atlas_20130711/template_t1_clipped.nii.gz \
  --outputDirectory ./TestOutput/
  --inputListFilename testList.csv \
