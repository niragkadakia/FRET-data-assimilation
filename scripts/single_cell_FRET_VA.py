"""
Variational annealing of single cell FRET data. 

Created by Nirag Kadakia at 08:00 10-16-2017
This work is licensed under the 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 
International License. 
To view a copy of this license, visit 
http://creativecommons.org/licenses/by-nc-sa/4.0/.
"""

import sys, time
sys.path.append('../src')
sys.path.append('../../../../varanneal_NK/varanneal/varanneal')
sys.path.append('/home/fas/emonet/nk479/varanneal_NK/varanneal/varanneal')
import va_ode
import scipy as sp
#from varanneal import va_ode
from utils import get_flags
from single_cell_FRET import single_cell_FRET
from params_bounds import bounds_Tar_1, bounds_Tar_2
from load_data import load_VA_data
from save_data import save_estimates

data_flags = get_flags()

n_ID = data_flags[0]
data_dt = float(data_flags[1])
data_sigma = float(data_flags[2])
init_seed = int(data_flags[3])

# Initialize FRET class 
scF = single_cell_FRET()
scF.set_param_bounds()
scF.set_state_bounds()
scF.set_bounds()
scF.init_seed = init_seed
scF.initial_estimate()
scF.Rm = 1.0/data_sigma**2.0

# Load twin data from file
data_dict = load_VA_data(data_flags=data_flags)
measurements = data_dict['measurements'][:, 1:]
stimuli = data_dict['stimuli'][:]
scF.Tt = data_dict['measurements'][:, 0]
scF.nT = len(scF.Tt)
scF.dt = scF.Tt[1]-scF.Tt[0]

# Initalize annealer class
annealer = va_ode.Annealer()
annealer.set_model(scF.df_estimation, scF.nD)
annealer.set_data(measurements, stim=stimuli,  t=scF.Tt)

# Estimate
BFGS_options = {'gtol':1.0e-8, 'ftol':1.0e-8, 'maxfun':1000000, 'maxiter':1000000}
tstart = time.time()
annealer.anneal(scF.x_init, scF.p_init, scF.alpha, scF.beta_array, scF.Rm, scF.Rf0, 
					scF.Lidx, scF.Pidx, dt_model=None, init_to_data=True, 
					bounds=scF.bounds, disc='trapezoid', method='L-BFGS-B', 
					opt_args=BFGS_options, adolcID=0)
print("\nADOL-C annealing completed in %f s."%(time.time() - tstart))

save_estimates(annealer, data_flags)
