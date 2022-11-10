import pandas as pd
import numpy as np
## the functions in this module are written for excluding the subjects which had motion artifacts in the TOF data and
# the vessels were not visible or the visible slices were not enough to derive conclusive conclusion and also to find
#  the age-matched controls


AD_motion_and_slice_scale=pd.read_excel('AD_motion_scale.xlsx',index_col=False,sheet_name='Sheet1') #we made excels file which
# include the scale range for both motion artifact and slices. The motion scales were 1 for no motion, 1.5 for tiny motion
# in some slices, 2 average motion or tiny motions in most of the slices and 3 for severe motions. For slices we had 1
# for the dataset which almost cover all the regions we need, 1.5 for datasets which have some slices missing but still
#managable and 2 for the datasets which dont cover many important regions.
healthy_motion_and_slice_scale=pd.read_excel('healthy_motion_scale.xlsx',index_col=False,sheet_name='Sheet1')
csv_AD=AD_motion_and_slice_scale.to_csv('AD_motion_scale.csv',index=False) # we convert them to csv to facilitate the workflow
csv_healthy=healthy_motion_and_slice_scale.to_csv('healthy_motion_scale.csv',index=False)
read_AD_scale=pd.read_csv('AD_motion_scale.csv')
read_healthy_scale=pd.read_csv('healthy_motion_scale.csv')
AD_motion_values=read_AD_scale['motion'].values   #we read the motion and slices values for both healthy and AD
# to be used as a ground truth for exclusion criteria.
healthy_motion_values=read_healthy_scale['motion'].values
AD_slice_values=read_AD_scale['slices'].values
healthy_slice_values=(read_healthy_scale['slices'].values)

def exclusion_creiteria(array_with_artifacts,scale_motion=None,scale_slice=None,type='both'):
    # The data underwent the exclusion criteria based on the scale values. In this function i tested the different
    # combinations of different values to check the results. I finally excluded the motion scale 2 and 3 and the slice
    #scale 2
    """
    :param array_with_artifacts: insert the array which has artifacts
    :param scale_motion: we insert our motion scale values which we want to be excluded as a list e.g., [1,2]
    :param scale_slice: we insert our slice scale values which we want to be excluded as a list
    :param type: the type of exclusin: motion, slice or both
    :return: the values of the array after removing the artifacts
    """

    if type=='motion': #if we only want to exclude motion artifacts
        scale_motion_idx = [i for i, j in enumerate(healthy_slice_values) if j not in scale_motion]
        array_after_exclusion_motion = [array_with_artifacts[i] for i in scale_motion_idx]
        return np.array(array_after_exclusion_motion)
    elif type=='slice':  #if we only want to exclude data with non-sufficient slices
        scale_slice_idx = [i for i, j in enumerate(healthy_slice_values) if j not in scale_slice]
        array_after_exclusion_slice = [array_with_artifacts[i] for i in scale_slice_idx]
        return np.array(array_after_exclusion_slice)
    elif type=='both': # if we want to exclude both factors
        scale_slice_motion_idx = [i for i, j in enumerate(healthy_slice_values) if
                                  j not in (scale_slice and scale_motion)]
        array_after_exclusion_motion_slice = [array_with_artifacts[i] for i in scale_slice_motion_idx]
        return np.array(array_after_exclusion_motion_slice)



# The table we had for patients only included their age at their entry so we calculated their age based on the
#time at which MR experiments were conducted.
healthy_data_age=pd.read_csv('healthy_patients_MR.csv')['Age'].values  # we read the age values of the healthy and AD subjects
AD_data_age=pd.read_csv('AD_patients_MR.csv')['Age'].values
healthy_data_MR=pd.read_csv('healthy_patients_MR.csv')['MR sessions'].values
AD_data_MR=pd.read_csv('AD_patients_MR.csv')['Age'].values   # we read the clinical MR sessions
def age_matched_closest_point(scale_motion,scale_slice,type): #finds the age-matched controls. the healthy subjects who had the closest
    # age to people with AD. Here we consider the exclusion criteria based on slice and motion
    """

    :param scale_motion: we insert our motion scale values which we want to be excluded as a list
    :param scale_slice: we insert our slice scale values which we want to be excluded as a list
    :param type: motion, slice or both
    :return:
    """
    closest_healthy=[]
    age_AD_after_exclusion=exclusion_creiteria(array_with_artifacts=AD_data_age,scale_motion=scale_motion,scale_slice=scale_slice,type=type)
    age_healthy_after_exclusion=exclusion_creiteria(array_with_artifacts=healthy_data_age,scale_motion=scale_motion,scale_slice=scale_slice,type=type)
    for i in age_AD_after_exclusion:
         sub_age=list(abs(age_healthy_after_exclusion-i))
         min_age=min(sub_age)
         min_age_idx=sub_age.index(min_age)
         second_min_age=sorted(sub_age)[1]
         second_min_age_idx=sub_age.index(second_min_age)
         if min_age_idx not in closest_healthy:
          closest_healthy.append(min_age_idx)
         elif min_age_idx in closest_healthy:
           closest_healthy.append(second_min_age_idx)
    return np.array(sorted(closest_healthy))