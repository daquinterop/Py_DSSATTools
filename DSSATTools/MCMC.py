'''
Module for Bayesian Calibration using MCMC with a Metropolis-Hasting step
'''

from copy import copy, deepcopy
import numpy as np
import multiprocessing as mp
from scipy.stats import (
    gamma, uniform, norm, invgamma, expon, beta, 
    multivariate_normal, invwishart, lognorm
)
from typing import Callable
import tqdm
import os
import shutil
from .run import CSM_EXE
import warnings
import pickle
import time

def unwrap_self(arg, **kwarg):
    out = MCMC._MCMC__sample_chain(*arg, **kwarg)
    return out


def setup_paralell_env(cores, DSSATFolder, crop):
    '''
    This function creates the folders to handle different simulations.
    Creates the "wdir" in the cwd, and returns a list with the CSM_EXE instances
    to run the model.
    Parameters
            ----------
            cores : int
                number of cores

            DSSATFolder: str
                path to DSSAT

            crop: str
                str len two indicating the crop Code
    
    Returns
            ----------
            DSSATEnvList: list
                list with CSM_EXE instances to be pased to MCMC.sample.
    '''
    DSSATEnvList = []
    DSSATFolder = '/mnt/c/DSSAT47'
    FILES_TO_COPY = [f for f in os.listdir(DSSATFolder) if not os.path.isdir(os.path.join(DSSATFolder, f))]
    FILES_TO_COPY = [f for f in FILES_TO_COPY if f[-4:] not in ['.exe']]
    if not os.path.exists(os.path.join(os.getcwd(), 'wdir')):
        os.mkdir(os.path.join(os.getcwd(), 'wdir'))
    print('Intializing working directories')
    for i in range(cores):
        print(f'Initializing working directory for cpu {i}')
        folder = os.path.join(os.getcwd(), 'wdir', f'{i:02d}')
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)
        folder = os.path.join(folder, 'DSSAT47')
        os.mkdir(folder)
        for f in FILES_TO_COPY:
            shutil.copy(os.path.join(DSSATFolder, f), folder)
        for f in ['Soil', 'Genotype', 'Weather']:
            os.mkdir(os.path.join(folder, f))
        for f in [x for x in os.listdir(os.path.join(DSSATFolder, 'Genotype')) if x[:2] == crop]:
            shutil.copy(os.path.join(DSSATFolder, 'Genotype', f), os.path.join(folder, 'Genotype', f))
        DSSATEnv = CSM_EXE(
            DSSATExe=os.path.join(folder, 'DSCSM047.EXE'),
            verbose=False
        )
        DSSATEnvList.append(DSSATEnv)
    return DSSATEnvList    


class MCMC():
    def __init__(self, priors:dict, responses:Callable,
                 responses_mean:dict=None):
        '''
        Parameters
            ----------
            priors : dict
                A dict containing the prior distributions of the parameters to be
                calibrated. The dict must follow this structure:
                    {"PAR1": {"dist": scipy.stats, "params": tuple, "file": str}, ...}
                where "PAR1" is the name of the parameter, scipy.stats is a scipy.stats
                instance representing a distribution, and tuple contains the parameters
                of the distribution in the order taken by the distribution instance. "file"
                contains the type of file for the parameter to be found e.g., ECO, CUL or SPE. That
                dict has lenght p, where p is the number of responses.

                The last element of the dict is for the Covariance matrix "SIGMA". If that element
                is not provided, then a custom prior will be used. That prior follows an
                inverse Wishart distribution, with p + 1 degrees of freedom, and scale=I, where
                I is the identity matrix of size pxp.
            
            responses: function
                It is a function that takes a dssattools.CSM_EXE instance and returns the response,
                variables a dict with this structure:
                    {"RESP1": [value1, value2, ...], "RESP2": [value1, value2, ...], ...}
            
            responses_mean: dict
                A dict containing the means and sd to standarize every response variable.
                It must follow the next structure:
                    {"RESP1": (mean, sd), "RESP2": (mean, sd), ...}
                Those values could be obtained from the observations. if None, then it's
                calculated when sampling from the observations.
        '''
        self._PRIORS = priors
        self._RESPONSES = responses
        if responses_mean != None:
            self._RESPONSES_MEAN = responses_mean
            self._N_RESPONSES = len(self._RESPONSES_MEAN)
            self._RESPONSE_NAMES = list(self._RESPONSES_MEAN.keys())
        else:
            self._RESPONSES_MEAN = None
        # self._RUN = run_function
        self._N_PARS = len(self._PRIORS)
        self._PARAM_NAMES = list(self._PRIORS.keys())


    def __moment_match(self, par, mu, sigma):
        '''
        Calculate distribution parameters using moment matching
        '''
        if par != 'SIGMA':
            if mu == 0: mu = 1e-6
            if sigma == 0: sigma = 1e-6
        else:
            SIGMA_pars = self._PRIORS[par]['pars']
        dist = self._PRIORS[par]['dist']
        if type(dist) == type(gamma):
            a = mu**2/sigma**2
            scale = sigma**2/mu
            if a == 0:
                a = .01
            return (a, 0, scale)
        elif type(dist) == type(invgamma):
            a = mu**2/sigma**2 + 2
            scale = mu*(mu**2/sigma**2 + 1)
            return (a, 0, scale)
        elif type(dist) == type(expon):
            l = 1/mu
            return (l)
        elif type(dist) == type(beta):
            # TODO: Some test have to be conducted for this distribution
            a = (mu**2 - mu**3 - mu*sigma**2)/sigma**2
            scale = (mu - 2*mu**2 + mu**3 - sigma**2 + mu*sigma**2)/sigma**2
            return (a, scale)
        elif type(dist) == type(norm):
            return (mu, sigma)
        elif type(dist) == type(lognorm):
            s = np.sqrt(np.log((sigma**2+mu**2)/mu**2))
            sigma = np.log(mu) - .5*np.log((sigma**2+mu**2)/mu**2)
            scale = np.exp(sigma)
            return (s, 0, scale)
        elif type(dist) == type(uniform):
            return self._PRIORS[par]['pars']
        elif type(dist) == type(invwishart):
            return (SIGMA_pars[0], sigma*SIGMA_pars[1])
        else:
            raise TypeError("Distribution doesn't match any of the available: gamma, invgamma, expon, beta, norm, uniform, lognorm")
        
        
    def sample(self, chains:int=4, cores:int=None, burnin:int=1000,
               n_iter:int=2000, tuning_interval:int=100, observations:dict=None,
               support: dict=None, previous_trace: dict=None):
        '''
        Parameters
            ----------
            chains : int
                number of chains to be sampled
                
            cores: int
                number of cores to be used. If None, the number of cores are the number 
                of chains.
                
            burin: int
                number of initial iterations for model adaptation.
            
            n_iter: int
                number of iterations to sample
                
            tuning_interval: int
                how often (iterations) to update the tuning parameters. The tuning parameter
                is tuned to achieve an acceptance rate between .3 and .5
            
            observations: dict
                a dict containg the observed data with the next structure:
                    {"PAR1": [value1, value2, ...], "PAR2": [value1, value2, ...], ...}

            support: dict
                a dict containing the support of the parameters, i.e. the minimum and maximum 
                value to accept as a sample.
                    {"PAR1": [min, max], "PAR2": [min, max], ...}

            previous_trace: dict
                a dict containg previous samples, acceptance and tuning_pars. The sampling
                will start from this point. You can use the method save_trace to save the trace.
        '''
        self._CHAINS = chains
        self._SUPPORT = support
        if not isinstance(observations, dict):
            raise TypeError('observations object must be a dict')
        self._OBSERVATIONS = observations
        if cores == None:
            self._CORES = min(self._CHAINS, np.floor(mp.cpu_count()*.6))
        else:
            self._CORES = min(self._CHAINS, cores)
        self._BURNIN = burnin
        self._N_ITER = n_iter + 1
        self._TUNING_INTERVAL = tuning_interval
        self._PREVIOUS_TRACE = previous_trace

        self.__setup()

        # TODO: Implement parallel for real simulations
        if self._CORES == 1:
            for iter in tqdm.tqdm(range(1, self._N_ITER + self._BURNIN)):
                if ((((iter - 1) % self._TUNING_INTERVAL) == 0) \
                    and iter < self._BURNIN):
                    for chain in range(self._CHAINS):
                        self.__tune(chain)

                for chain in range(self._CHAINS):
                    self.__sample_chain(chain)
                # if iter == self._BURNIN:
                #     print()
        else:
            jobs = []
            core = 0
            manager = mp.Manager()
            for iter in tqdm.tqdm(range(1, self._N_ITER + self._BURNIN)):
                # Create object to get output
                mp_chains = manager.list()
                for chain in range(self._CHAINS): 
                    mp_chains.append(manager.list())
                    mp_chains[chain].append(manager.list()) # samples
                    mp_chains[chain].append(manager.list()) # acceptance

                # Adapt tuning parameters 
                if ((((iter - 1) % self._TUNING_INTERVAL) == 0) \
                    and iter < self._BURNIN):
                    for chain in range(self._CHAINS):
                        self.__tune(chain)

                for chain in range(self._CHAINS):
                    p = mp.Process(target=unwrap_self, args=((self, chain, True, mp_chains, core),))
                    jobs.append(p)
                    p.start()
                    core +=1 
                    if core == self._CORES:
                        for proc in jobs: 
                            proc.join()
                        core = 0
                        jobs = []
                        for ch in range((chain + 1) - self._CORES, chain + 1):
                            if len(mp_chains[ch][0]) == 0:
                                self.__sample_chain(ch, core=ch)
                                return
                            # If sampling failed at some poing then complete it with prev samples
                            if len(mp_chains[chain][0]) < self._N_PARS:
                                prev_samples = self.samples[ch, self._CURR_ITER[ch] - 1, :]
                                for n in range(len(mp_chains[chain][0]), self._N_PARS):
                                    mp_chains[chain][0].append(prev_samples[n])
                                    mp_chains[chain][1].append(0)
                            self.samples[ch, self._CURR_ITER[ch], :] = np.array(mp_chains[ch][0], dtype=object)
                            self.acceptance[ch, self._CURR_ITER[ch], :] = np.array(mp_chains[ch][1])
                            self._CURR_ITER[ch] += 1
                if self._CURR_ITER[0] % 20 == 0:
                    print()
        return

    
    def __tune(self, chain):
        curr_iter = self._CURR_ITER[chain]
        if curr_iter == 1:
            return
        acc_rate_pars = self.acceptance[chain, curr_iter - self._TUNING_INTERVAL:curr_iter, :].mean(axis=0)
        for n_par, acc_rate in enumerate(acc_rate_pars):
            scale = self.tuning_pars[chain, n_par]
            if acc_rate < 0.001:
                # reduce by 90 percent
                self.tuning_pars[chain, n_par] = scale * .1
            elif acc_rate < 0.05:
                # reduce by 50 percent
                self.tuning_pars[chain, n_par] = scale * .5
            elif acc_rate < 0.3:
                # reduce by ten percent
                self.tuning_pars[chain, n_par] = scale * .9
            elif acc_rate > 0.95:
                # increase by factor of ten
                self.tuning_pars[chain, n_par] = scale * 10.
            elif acc_rate > 0.75:
                # increase by double
                self.tuning_pars[chain, n_par] = scale * 2.
            elif acc_rate > 0.5:
                # increase by ten percent
                self.tuning_pars[chain, n_par] = scale * 1.1
        return

    
    def __standarized_response(self, samples, **kwargs):
        samples[:-1] = np.where(samples[:-1] == 0., .001, samples[:-1])
        # try:
        mu = self._RESPONSES(samples, **kwargs)
        # If the simulation fails is probably because the parameters are not correctly defined
        # then all outputs are set to 0 to decrease the likelihood.
        # except OSError:
        #     mu = {key: 0 for key, _ in self._RESPONSES_MEAN.items()}
        #     warnings.warn(f'DSSAT Simulation failed for next samples: {samples}')
        mu_sd = {
            key: (values - self._RESPONSES_MEAN[key][0]) / self._RESPONSES_MEAN[key][1] 
            for key, values in mu.items()
        }
        return mu_sd


    def __sample_chain(self, chain, parallel=False, mp_chains=None, core=None):
        '''
        Samples a single chain
        '''
        prev_samples = self.samples[chain, self._CURR_ITER[chain]-1, :]
        accept = 1
        # Sample one parameter at once
        for n, (par, prev_sample, tuning_par) in enumerate(
                zip(self._PRIORS.keys(), prev_samples, self.tuning_pars[chain])):
             
            prev_sample = prev_samples[n]
            tuning_par = self.tuning_pars[chain][n]
            
            new_samples = deepcopy(prev_samples)
            new_sample = self.__sample_par(par, prev_sample, tuning_par) 
            new_samples[n] = new_sample
            
            # Calculate likelihood of prev samples only if the sample has changed
            if par != 'SIGMA':
                if accept:
                    self._likelihood_prev[chain] = self.__likelihood(
                        self.__standarized_response(prev_samples, core=core), prev_samples[-1]
                    )
                # Calculate likelihood for new sample
                try:
                    self._likelihood_new[chain] = self.__likelihood(
                        self.__standarized_response(new_samples, core=core), new_samples[-1]
                    )
                # If simulation fails, then continue with the previous samples
                except OSError:
                    warnings.warn(f'DSSAT Simulation failed for the next sample: {par}={new_sample}')
                    self._likelihood_new[chain] = self._likelihood_prev[chain]
                    new_samples = prev_samples

            
            if not parallel:
            # Then choose samples
                z, accept = self.__choose(prev_sample, new_sample, par, tuning_par, n, chain)
                prev_samples[n] = z
                self.samples[chain, self._CURR_ITER[chain], n] = z
                self.acceptance[chain, self._CURR_ITER[chain], n] = accept
                self._CURR_ITER[chain] += 1
            else: # In case it is on parallel
                z, accept = self.__choose(prev_sample, new_sample, par, tuning_par, n, chain)
                prev_samples[n] = z
                mp_chains[chain][0].append(z)
                mp_chains[chain][1].append(accept)
        if parallel:
            return mp_chains
    


    def __sample_par(self, par, curr_sample, tuning_par):
        pars = self.__moment_match(par, curr_sample, tuning_par)
        sample = self._PRIORS[par]['dist'].rvs(*pars, random_state=int(str(time.time()).split('.')[-1]))
        # Check if sample is within the support
        if (self._SUPPORT is not None) and (par != 'SIGMA'):
            par_support = self._SUPPORT[par]
            if (sample < par_support[0]):
                return curr_sample
            elif (sample > par_support[1]):
                return curr_sample
            else:
                return sample
        return sample


    def __choose(self, x, x_new, par, tuning_par, n_par, chain):
        '''
        Whether to keep or discard the new sample
        '''
        # Inverse-Wishart is the conjugate, then no selection is needed
        if par == 'SIGMA': 
            return x_new, True
        prior = self._PRIORS[par]['dist']
        prior_pars = self._PRIORS[par]['pars']
        denominator = self._likelihood_prev[chain] + \
            prior.logpdf(x, *prior_pars)
        numerator = self._likelihood_new[chain] + \
            prior.logpdf(x_new, *prior_pars)
        q_ratio = prior.pdf(x, *self.__moment_match(par, x_new, tuning_par)) / \
            prior.pdf(x_new, *self.__moment_match(par, x, tuning_par))
        R = min(1, np.exp(numerator - denominator) * q_ratio)
        if R > np.random.uniform():
            if x_new == x:
                return x, False
            else:
                return x_new , True
        else:
            return x, False


    def __likelihood(self, mu, SIGMA):
        mu_mv = np.array(list(mu.values()))
        n_responses = mu_mv.shape[0]
        logL = multivariate_normal.logpdf(
            mu_mv.T, 
            mean=np.zeros(shape=n_responses), 
            cov=SIGMA,
            # cov = np.ones(shape=(n_responses, n_responses)),
            allow_singular=True
        ).sum()
        return logL
    

    def __setup(self):
        '''
        Initialize the objects to store the samples, acceptance rate,
        tuning parameters, etc.
        '''
        if self._RESPONSES_MEAN == None:
            self._RESPONSES_MEAN = {
                key: (np.mean(values), np.std(values))
                for key, values in self._OBSERVATIONS.items()
                }
            self._N_RESPONSES = len(self._RESPONSES_MEAN)
            self._RESPONSE_NAMES = list(self._RESPONSES_MEAN.keys())

        # Add Sigma prior
        if 'SIGMA' not in self._PRIORS.keys():
            self._STD_OBSERVATIONS = {
                key: (np.array(values) - np.array(values).mean())/np.array(values).std()
                for key, values in self._OBSERVATIONS.items()
            }
            self._PRIORS['SIGMA'] = {
                'dist': invwishart,
                'pars': (
                    self._N_RESPONSES + 2, 
                    np.identity(self._N_RESPONSES)
                )
            }
            self._N_PARS += 1
            
        self.samples = np.zeros(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_PARS),
                                dtype=object)

        
        # Tuning parameters initialized as one
        self.tuning_pars = np.ones(shape=(self._CHAINS, self._N_PARS))
        # Initialize arrays for responses and acceptance
        # self.response_out = np.zeros(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_RESPONSES))
        self.acceptance = np.ones(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_PARS))

        if isinstance(self._PREVIOUS_TRACE, dict):
            prev_samples = self._PREVIOUS_TRACE['samples']
            indexes = list(map(lambda x: hasattr(x, 'shape'), prev_samples[:, :, -1].mean(axis=0)))
            self._CURR_ITER = np.array([sum(indexes) - 1] * self._CHAINS)
            
            prev_samples = prev_samples[:, indexes, :]
            self.samples = np.concatenate([prev_samples, self.samples], axis=1)

            self.tuning_pars = self._PREVIOUS_TRACE['tuning_pars']
            
            prev_acceptance = self._PREVIOUS_TRACE['acceptance']
            if prev_acceptance.shape[1] > self._PREVIOUS_TRACE['samples'].shape[1]:
                prev_acceptance = prev_acceptance[:, :self._PREVIOUS_TRACE['samples'].shape[1], :]
            prev_acceptance[:, indexes, :]
            self.acceptance = np.concatenate([prev_acceptance, self.acceptance], axis=1)
        else:
            # Define init values from priors
            for n, (_, value) in enumerate(self._PRIORS.items()):
                for chain in range(self._CHAINS):
                    self.samples[chain, 0, n] = value['dist'].rvs(*value['pars'])
            self._CURR_ITER = np.array([1] * self._CHAINS)

        self._likelihood_new = np.zeros(shape=(self._CHAINS))
        self._likelihood_prev = np.zeros(shape=(self._CHAINS))
        return

    
    def save_trace(self, filename='mcmc_trace'):
        '''
        Save the trace to be pased to next sampling iterations.
        '''
        with open(f'{filename}.pkl', 'wb') as f:
            previous_trace = {
                'samples': self.samples,
                'acceptance': self.acceptance,
                'tuning_pars': self.tuning_pars
                }
            pickle.dump(previous_trace, f)
    
    