
"""
This example shows how to decompose EEG signals into source activations with MVARICA, and subsequently extract single-trial connectivity as features for LDA.
"""
import numpy as np

import scot
import scot.backend.sklearn     # use scikit-learn backend
import scot.xvschema

from sklearn.lda import LDA

import matplotlib.pyplot as plt

"""
The example data set contains a continuous 45 channel EEG recording of a motor
imagery experiment. The data was preprocessed to reduce eye movement artifacts
and resampled to a sampling rate of 100 Hz.
With a visual cue the subject was instructed to perform either hand of foot
motor imagery. The the trigger time points of the cues are stored in 'tr', and
'cl' contains the class labels (hand: 1, foot: -1). Duration of the motor 
imagery period was approximately 6 seconds.
"""

from motorimagery import data as midata

raweeg = midata.eeg
triggers = midata.triggers
classes = midata.classes
fs = midata.samplerate
locs = midata.locations

"""
Set up the analysis object

We simply choose a VAR model order of 30, and reduction to 4 components.
Setting the regularization parameter to 0.2 gives good results in this example.
"""
ws = scot.Workspace(30, reducedim=4, fs=fs, var_delta=0.2)


"""
Prepare the data

Here we cut segments from 3s to 4s following each trigger out of the EEG. This
is right in the middle of the motor imagery period.
"""
data = scot.datatools.cut_segments(raweeg, triggers, 3*fs, 4*fs)

"""
Perform MVARICA
"""
ws.setData(data, classes)
print('Running CSPVARICA...')
ws.doCSPVARICA()

"""
Find optimal regularization parameter for single-trial fitting
"""
#ws.optimizeRegularization(scot.xvschema.singletrial, 60)

freq = np.linspace(0,fs,ws.nfft_)

"""
Single-Trial Fitting and feature extraction
"""
print('Extracting Features...')
features = np.zeros((len(triggers), 32))
for t in range(len(triggers)):
    print('Trial: %d   '%t, end='\r')
    ws.setData(data[:,:,t])
    ws.fitVAR()

    con = ws.getConnectivity('ffPDC')
    
    alpha = np.mean(con[:,:,np.logical_and(7<freq, freq<13)], axis=2)
    beta = np.mean(con[:,:,np.logical_and(15<freq, freq<25)], axis=2)
    
    features[t,:] = np.array([alpha, beta]).flatten()
print('')
    
lda = LDA( )
lda.fit(features, classes)

llh = lda.transform(features)
    
plt.hist([llh[classes==-1,:], llh[classes==1,:]])
plt.show()