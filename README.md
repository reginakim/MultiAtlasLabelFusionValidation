MultiAtlasLabelFusionValidation
===============================

This is a nipype development page for multi atlas label fusion validation study. This nipype works with [BRAINSTools](https://github.com/BRAINSia/BRAINSTools) build. 

Directories
-----------
### ./src
All the source files
* ./src/nipype
  * *prepareMultiLabel.py*: Command line python module to do preprocessing including Brain Clip and affine registration to a given template atlas.

Nipype scripts
#### ./src/script
Scripts other than nipype
* *generateInputSpecification.sh*: A utility script to generate list of files for prepareMultiLabel.py module. This has to be modified as necessary.  

### ./test
Test files that can be used for the usage reference.

* prepareMultiLabel.sh
* testList.csv
* testListIncompleteSet.csv

Usage with Example
------------------

<pre><code>
  cd ./test
  bash prepareMultiLabel.sh
</pre></code>

