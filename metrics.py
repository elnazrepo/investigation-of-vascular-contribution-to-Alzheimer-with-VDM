# This module is used for calculating the vascular metrics
import os
import glob
from Filtering import load_as_np_array
import numpy as np
import pandas as pd
import nibabel as nib
def finding_paths(all_folders_path,segmented_vessels_path,flag=1): # This function is useful when regional brain volume
    #obtained from freesurfer and masked values are mapped on the list of segmented data. Flag=1 derives the corresponding
    # brain masks and flag=2 derives the corresponding roi based on freesurfer lookup table
    """

    :param all_folders_path: the path in which all the dataset including T1 weighted, TOF, freesurfer results are located
    :param segmented_vessels_path: path of the segmented vessels
    :param flag:
    :return: depending on the flag either the list of the corresponding brain masks for the segmented vessels or the aparc+aseg
    files which are used to look at the regional brain volume based on the freesurfer lookup table
    """
    data=[i for i in os.listdir(segmented_vessels_path) if i.endswith('.nii')]
    data_splitted=[i.replace('sub-','').replace('_ses','').replace('_acq-TOF_angio_segmentation.nii','') for i in data]
    data_name=[i.split('-')[0]+'_MR_'+i.split('-')[1] for i in data_splitted]
    if flag==1:
        files=[all_folders_path+'/'+i+'/brainmask_Warped_spm.nii' for i in data_name]
    elif flag==2:
        files=[all_folders_path+'/'+i+'/aparc+aseg_Warped_spm.nii' for i in data_name]
    return files

def get_pixel_resolution(array): #computing the resolution of 3d image in all 3 (x,y,z)directions

    loaded_file,affine,header=nib.load(array)
    res_x,res_y,res_z=header.get_zooms()
    return res_x,res_y,res_z


class calculate_metrics(): #this class calculates the metrics

    def __init__(self,all_folders_path,data_array_path,dic_array,csv_name,flag=1,metric_flag=1):
        self.all_folders_path=all_folders_path
        self.data_array_list=glob.glob(data_array_path+'/*.nii')
        self.roi_array_list=finding_paths(all_folders_path=all_folders_path,segmented_vessels_path=data_array_path)
        self.dic_array=dic_array  #the regions that we investigate have a value located in freesurfer lookup table. We insert
        #these regions as dictionaries for instance roi={left hippocampus:53}
        self.csv_name=csv_name
        self.flag=flag
        self.metric_flag=metric_flag

    def metrics(self): # returns the metrics of the desired ROI in a csv file
            all_results = []
            ids = [i.replace('.nii', '') for i in self.data_array_list]
            for dat, roi in zip(self.data_array_list, self.roi_array_list):
                print('processing {}'.format(dat))
                print('processing {}'.format(roi))
                data = load_as_np_array(dat)
                rois = load_as_np_array(roi)
                result_per_data = []
                columns = []
                for key, values in self.dic_array.items():
                    mask = rois == values
                    voxels_ROI = (data[mask > 0])
                    num_regional_voxels=len(voxels_ROI)
                    x, y, z = get_pixel_resolution(data)
                    vol_voxel = x * y * z
                    if self.metric_flag==1:  ##then calculate regional vascular density
                      voxesl_ROI_non_zero = np.nonzero(np.array(voxels_ROI))
                      num_voxels_one = len((voxesl_ROI_non_zero)[0])
                      metric= num_voxels_one / num_regional_voxels
                      metric = float("{:.5f}".format(metric))
                    elif self.metric_flag==2: #then calculate vessel volume
                        voxesl_ROI_non_zero = np.nonzero(np.array(voxels_ROI))
                        num_voxels_one = len((voxesl_ROI_non_zero)[0])
                        metric = num_voxels_one * vol_voxel
                    elif self.metric_flag==3:## then calculate regional volume
                        metric=num_regional_voxels*vol_voxel
                    result_per_data.append(metric)
                    columns.append(key + '_mean')
                    all_results.append(result_per_data)
                df = pd.DataFrame(index=ids, columns=columns, data=all_results)
                df.to_csv(self.csv_name)


