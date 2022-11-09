# The functions required for comparing the automatically segmented data with the semi-manually segmented data
# using ilastik are provided here

import nibabel as nib
import h5py
import numpy as np
import matplotlib.pyplot as plt
import os

home=os.getcwd()

def load_as_np_array(file): #convertin Nifti images to an array
    """
    :param file: The file name of the Nifti image. in my thesis the Nifti image was the segmented vessels (segmented using OMELETTE)
    :return: An numpy array
    """
    array,_,_=nib.load(file)
    return array

def create_array_from_ilastik(file):  #create a biniarized numpy array from ilastik h5 format
    """
    :param ilastik_data: ilastik data file name
    :return: a binarized numpy array obtained from ilastik data
    """
    read_data = h5py.File(file, 'r')
    get_key = list((read_data.keys()))[0]
    array = np.array(read_data[get_key])# Converts h5 format to a numpy array (it is required for ilastik)
    array_shape=array.shape
    array[array > 1] = 0
    # data in ilastik has 3 labels.The vessel label is already one.
    # To create binary data are other labels are set to zero
    array=array.reshape(array_shape)
    return array


class create_maked_data: # With this class the masked segmented vessels can be created (In the dataset we had in the thesis
    #the TOF data lacked the skull stripping pre-processing step thus it contained all the non-brain regions information including
    #skull, ear and nose. To remove these structures, me mapped the brain.mgz file which was obtained from the processing of
    #T1-weighte images and map them on the TOF space. The functions in this class create masked data (both automatically and
    #semi-manually segmente data), for both mask and data, the file path should be inserted

    def __init__(self,file_path,mask_path,flag=1):

        self.file=os.path.join(home+'/',file_path)
        self.mask=os.path.join((home+'/'),mask_path)
        self.flag=flag #flag shows the approach by which vessels are segmented. if segmented automatically, falg==1
        #and if flag==2, vessels segmented manually

    def creating_masked_vessels(self): #creates the masked data (both vessels segmented automatically using OMELETTE and
        #semi-manually segmented using ilastik)
        input_mask = load_as_np_array(self.mask)
        input_mask[input_mask > 0] = 1
        if self.flag==1:
         automatically_segmented_vessels = load_as_np_array(self.file)
         masked_image = automatically_segmented_vessels * input_mask
         return masked_image
        elif self.flag==2:
            manually_segmented_vessels=create_array_from_ilastik(self.file)
            maske_image=manually_segmented_vessels*input_mask
            return maske_image


    def masked_vessels_MIP(self):  # creates maximum intensity projection of the masked segmented vessels
        """
        :param file: The file name of the Nifti data
        :param mask: The masked Nifti mask which was obtained from the T1-wighted images located in the Freesurfer folder
        :return: MIP of the masked data
        """
        masked_data = self.creating_masked_vessels()
        MIP = np.max(masked_data, axis=2)
        plt.imshow(MIP, cmap='gray')
        plt.show()

class filter_check: #checks the filters performance (here Jerman and Frangi) based on comparison between ground truth
      #and automatically segmented data. Please insert ground truth and automatically segmented data path

    def __init__(self,ground_truth_path,prediction_path):
        self.ground_truth=os.path.join(home+'/'+ground_truth_path)
        self.prediction=os.path.join(home+'/'+prediction_path)

    def ROC(self):
        # it returns the sensitivity and specificity of the filters (true and false positive rates) based on the
        #comparison between ground truth and manually segmented data. It is used for plotting ROC curve
        g=(create_array_from_ilastik(self.ground_truth)).astype(dtype=bool)
        p=(load_as_np_array(self.prediction)).astype(dtype=bool)
        true_pos = np.logical_and(g, p)
        false_pos = np.logical_and(~g, p)
        sensitivity=true_pos.sum()
        specificity=false_pos.sum()
        return sensitivity,specificity

    def plot_ROC(self):
         # plots the ROC curves (true positive vs false positive rate)of Jerman and
        # Frangi filters
         sensitivity=[]
         specificity=[]
         for i, j in zip(os.listdir(self.ground_truth), os.listdir(self.prediction)):
             data_ground_truth=create_array_from_ilastik(i)
             data_prediction=load_as_np_array(j)
             print('processing ground truth:{}, prediction: {}'
                  .format(self.ground_truth.split('/')[-1], self.prediction.split('/')[-1] ))
             sensitivity_, specificity_ = self.ROC()
             sensitivity.append(sensitivity_)
             specificity.append(specificity_)
         plt.plot(specificity,sensitivity, label='ROC CURVE')
         plt.show()




