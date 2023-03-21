
"""
!!! abstract "Short Description"
    The function `gatorPredict` is employed to make predictions about the 
    expression of a specified marker on cells in new images using the models 
    generated by `gatorTrain`. This calculation is done at the pixel level, 
    resulting in an output image where the number of channels corresponds to 
    the number of models applied to the input image. The parameter `markerChannelMapPath` 
    is used to associate the image channel number with the relevant model to be applied.


## Function
"""


# Libs
import os, argparse
import pandas as pd
import pathlib

# tools libs
from skimage import io as skio
import tensorflow.compat.v1 as tf
import tifffile
import numpy as np
from skimage.transform import resize


# from other .py scripts
if __name__ == '__main__':
    from toolbox.imtools import im2double
    from UNet import UNet2D
elif __name__ == 'gatorPredict':
    from toolbox.imtools import im2double
    from UNet import UNet2D
else:
    from .toolbox.imtools import im2double
    from .UNet import UNet2D



# Function
def gatorPredict (imagePath,
                 gatorModelPath,
                 projectDir, 
                 markerChannelMapPath, 
                 markerColumnName='marker', 
                 channelColumnName='channel', 
                 modelColumnName='gatormodel', 
                 verbose=True,
                 GPU=-1,
                 dsFactor=1):
    
    """
Parameters:
    imagePath (str):  
        The path to the .tif file that needs to be processed. 
     
    gatorModelPath (str):  
        The path to the `gatorModel` folder. 
    
    projectDir (str):  
        The path to the output directory where the processed images (`probabilityMasks`) will be saved.
     
    markerChannelMapPath (str, optional):  
        The path to the marker panel list, which contains information about the markers used in the image. This argument is required.
     
    markerColumnName (str, optional):  
        The name of the column in the marker panel list that contains the marker names. The default value is 'marker'.
     
    channelColumnName (str, optional):  
        The name of the column in the marker panel list that contains the channel names. The default value is 'channel'.
     
    modelColumnName (str, optional):  
        The name of the column in the marker panel list that contains the model names. The default value is 'gatormodel'.

    verbose (bool, optional):
        If True, print detailed information about the process to the console.  

    GPU (int, optional):  
        An optional argument to explicitly select the GPU to use. The default value is -1, meaning that the GPU will be selected automatically.

    dsFactor (float, optional):
        An optional argument to downsample image before inference. The default value is 1, meaning that the image is not downsampled. Use it to modify image pixel size to match training data in the model.

Returns:
    Predicted Probability Masks (images):  
        The result will be located at `projectDir/GATOR/gatorPredict/`.

Example:

    	```python    
        # set the working directory & set paths to the example data
        cwd = '/Users/aj/Desktop/gatorExampleData'
        imagePath = cwd + '/image/exampleImage.tif'
        gatorModelPath = cwd + '/GATOR/gatorModel/'
        projectDir = cwd
        markerChannelMapPath = cwd + '/markers.csv'
        
        # Run the function
        ga.gatorPredict( imagePath=imagePath,
                         gatorModelPath=gatorModelPath,
                         projectDir=projectDir, 
                         markerChannelMapPath=markerChannelMapPath, 
                         markerColumnName='marker', 
                         channelColumnName='channel', 
                         modelColumnName='gatormodel', 
                         verbose=True,
                         GPU=-1)
        
        # Same function if the user wants to run it via Command Line Interface
        python gatorPredict.py --imagePath /Users/aj/Desktop/gatorExampleData/image/exampleImage.tif --gatorModelPath /Users/aj/Desktop/gatorExampleData/GATOR/gatorModel/ --projectDir /Users/aj/Desktop/gatorExampleData --markerChannelMapPath /Users/aj/Desktop/gatorExampleData/markers.csv
    	
    	```
     
     """
    
    fileName = pathlib.Path(imagePath).stem

    # read the markers.csv
    maper = pd.read_csv(pathlib.Path(markerChannelMapPath))
    columnnames =  [word.lower() for word in maper.columns]
    maper.columns = columnnames
    
    # making it compatable with mcmicro when no channel info is provided
    if not set(['channel', 'channels', channelColumnName]).intersection(set(columnnames)):
        # add a column called 'channel'
        maper['channel'] = [i + 1 for i in range(len(maper))]
        columnnames = list(maper.columns)
        
        
    # identify the marker column name (doing this to make it easier for people who confuse between marker and markers)
    if markerColumnName not in columnnames:
        # ckeck if 'markers' or 'marker_name' or 'marker_names' is in columnnames
        # if so assign that match to markerCol
        for colname in columnnames:
            if 'marker' in colname or 'markers' in colname or 'marker_name' in colname or 'marker_names' in colname:
                markerCol = colname
                break
        else:
            raise ValueError('markerColumnName not found in markerChannelMap, please check')
    else:
        markerCol = markerColumnName


   # identify the channel column name (doing this to make it easier for people who confuse between channel and channels)
    if channelColumnName not in columnnames:
        if channelColumnName != 'channel':
            raise ValueError('channelColumnName not found in markerChannelMap, please check')
        if 'channels' in columnnames:
            channelCol = 'channels'
        else:
            raise ValueError('channelColumnName not found in markerChannelMap, please check')
    else:
        channelCol = channelColumnName


    # identify the gator model column name (doing this to make it easier for people who confuse between gatormodel and gatormodels)
    if modelColumnName not in columnnames:
        if modelColumnName != 'gatormodel':
            raise ValueError('modelColumnName not found in markerChannelMap, please check')
        if 'gatormodels' in columnnames:
            modelCol = 'gatormodels'
        else:
            raise ValueError('modelColumnName not found in markerChannelMap, please check')
    else:
        modelCol = modelColumnName

    # remove rowa that have nans in modelCol
    runMenu = maper.dropna(subset=[modelCol], inplace=False)[[channelCol,markerCol,modelCol]]

    # shortcuts
    numMarkers = len(runMenu)

    I = skio.imread(imagePath, img_num=0, plugin='tifffile')


    probPath = pathlib.Path(projectDir + '/GATOR/gatorPredict/')
    modelPath = pathlib.Path(gatorModelPath)

    if not os.path.exists(probPath):
        os.makedirs(probPath,exist_ok=True)


    def data(runMenu, 
             imagePath, 
             modelPath, 
             projectDir, 
             dsFactor=dsFactor, 
             GPU=GPU):
        
        # Loop through the rows of the DataFrame
        for index, row in runMenu.iterrows():
            channel = row[channelCol]
            markerName = row[markerCol]
            gatormodel = row[modelCol]
            if verbose is True:
                print('Running gator model ' + str(gatormodel) + ' on channel ' + str(channel) + ' corresponding to marker ' + str(markerName) )


            tf.reset_default_graph()
            UNet2D.singleImageInferenceSetup(pathlib.Path(modelPath / gatormodel), GPU, -1, -1)

            fileName = os.path.basename(imagePath)
            fileNamePrefix = fileName.split(os.extsep, 1)
            fileType = fileNamePrefix[1]
            if fileType == 'ome.tif' or fileType == 'ome.tiff' or fileType == 'btf':
                I = skio.imread(imagePath, img_num=int(channel-1), plugin='tifffile')
            elif fileType == 'tif':
                I = tifffile.imread(imagePath, key=int(channel-1))

            if I.dtype == 'float32':
                I = im2double(I) * 255
            elif I.dtype == 'uint16':
                I = im2double(I) * 255

            rawVert = I.shape[0]
            rawHorz = I.shape[1]
            hsize = int(float(rawVert * float(dsFactor)))
            vsize = int(float(rawHorz * float(dsFactor)))
            I = resize(I, (hsize, vsize),preserve_range=True)

            append_kwargs = {
                'bigtiff': True,
                'metadata': None,
                'append': True,
            }
            save_kwargs = {
                'bigtiff': True,
                'metadata': None,
                'append': False,
            }

            PM = np.uint8(255 * UNet2D.singleImageInference(I, 'accumulate',1))
            PM = resize(PM, (rawVert, rawHorz))
            yield np.uint8(255 * PM)

    with tifffile.TiffWriter(probPath / (fileName + '_gatorPredict.ome.tif'), bigtiff=True) as tiff:
        tiff.write(data(runMenu, imagePath, modelPath, probPath, dsFactor=dsFactor, GPU=GPU), shape=(numMarkers,I.shape[0],I.shape[1]), dtype='uint8', metadata={'Channel': {'Name': runMenu[markerCol].tolist()}, 'axes': 'CYX'})
        UNet2D.singleImageInferenceCleanup()


# =============================================================================
#     logPath = ''
#     scriptPath = os.path.dirname(os.path.realpath(__file__))
# 
#     pmPath = ''
# 
#     if os.system('nvidia-smi') == 0:
#         if args.GPU == -1:
#             print("automatically choosing GPU")
#             GPU = GPUselect.pick_gpu_lowest_memory()
#         else:
#             GPU = args.GPU
#         print('Using GPU ' + str(GPU))
# 
#     else:
#         if sys.platform == 'win32':  # only 1 gpu on windows
#             if args.GPU == -1:
#                 GPU = 0
#                 print('using default GPU')
#             else:
#                 GPU = args.GPU
#             print('Using GPU ' + str(GPU))
#         else:
#             GPU = 0
#             print('Using CPU')
#     os.environ['CUDA_VISIBLE_DEVICES'] = '%d' % GPU
# =============================================================================


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gator Predict function')
    parser.add_argument('--imagePath', type=str, required=True, help='The path to the .tif file that needs to be processed.')
    parser.add_argument('--gatorModelPath', type=str, required=True, help='The path to the `gatorModel` folder.')
    parser.add_argument('--projectDir', type=str, help='The path to the output directory where the processed images will be saved.')
    parser.add_argument('--markerChannelMapPath', type=str, required=True, help='The path to the marker panel list, which contains information about the markers used in the image.')
    parser.add_argument('--markerColumnName', type=str, default='marker', help='The name of the column in the marker panel list that contains the marker names. The default value is `marker`.')
    parser.add_argument('--channelColumnName', type=str, default='channel', help='The name of the column in the marker panel list that contains the channel names. The default value is `channel`.')
    parser.add_argument('--modelColumnName', type=str, default='gatormodel', help='The name of the column in the marker panel list that contains the model names. The default value is `gatormodel`.')
    parser.add_argument("--verbose", type=bool, default=True, help="If True, print detailed information about the process to the console.")      
    parser.add_argument('--GPU', type=int, default=-1, help='An optional argument to explicitly select the GPU to use. The default value is 0, meaning that the GPU will be selected automatically.')
    parser.add_argument('--dsFactor', type=float, default=1,help='Scaling Factor.')

    args = parser.parse_args()
    gatorPredict(imagePath=args.imagePath, 
                 gatorModelPath=args.gatorModelPath, 
                 projectDir=args.projectDir, 
                 markerChannelMapPath=args.markerChannelMapPath, 
                 markerColumnName=args.markerColumnName, 
                 channelColumnName=args.channelColumnName, 
                 modelColumnName=args.modelColumnName, 
                 verbose=args.verbose,
                 GPU=args.GPU,
                 dsFactor=args.dsFactor)






