'''
Module for Bayesian Calibration using MCMC with a Metropolis-Hasting step
'''

import numpy as np
import multiprocessing as mp
from pathos.multiprocessing import ProcessingPool as Pool
from scipy.stats import (
    gamma, uniform, norm, invgamma, expon, beta
)
from typing import Callable
import tqdm
import copy

def unwrap_self(arg, **kwarg):
    out = MCMC._MCMC__sample_chain(*arg, **kwarg)
    return out

class MCMC():
    def __init__(self, priors:dict, responses:Callable,
                 responses_mean:dict, run_function:Callable):
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
                contains the type of file for the parameter to be found e.g., ECO, CUL or SPE.
            
            responses: function
                It is a function that takes a dssattools.CSM_EXE instance and returns the response,
                variables a dict with this structure:
                    {"RESP1": [value1, value2, ...], "RESP2": [value1, value2, ...], ...}
            
            responses_mean: dict
                A dict containing the means and sd to standarize every response variable.
                It must follow the next structure:
                    {"RESP1": (mean, sd), "RESP2": (mean, sd), ...}
                Those values could be obtained from the observations.
            
            run_function: function
                The function that takes a dssattools.MCMC instance and run DSSAT through a 
                dssattools.CSM_EXE instance.
        '''
        self._PRIORS = priors
        self._RESPONSES = responses
        self._RESPONSES_MEAN = responses_mean
        self._RUN = run_function
        self._N_PARS = len(self._PRIORS)
        self._N_RESPONSES = len(self._RESPONSES_MEAN)
        self._PARAM_NAMES = list(self._PRIORS.keys())
        self._RESPONSE_NAMES = list(self._RESPONSES_MEAN.keys())


    def __moment_match(self, par, mu, sigma):
        '''
        Calculate distribution parameters using moment matching
        '''
        #TODO: fix the parameter orders for every distribution.
        dist = self._PRIORS[par]['dist']
        if type(dist) == type(gamma):
            a = mu**2/sigma**2
            scale = sigma**2/mu
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
        elif type(dist) == type(uniform):
            return self._PRIORS[par]['pars']
        else:
            raise TypeError("Distribution doesn't match any of the available: gamma, invgamma, expon, beta, norm, uniform")
        
        
    def sample(self, chains:int=4, cores:int=None, burnin:int=1000,
               n_iter:int=2000, tuning_interval:int=100, observations:dict=None):
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
        '''
        self._CHAINS = 4
        if not isinstance(observations, dict):
            raise TypeError('observations object must be a dict')
        self._OBSERVATIONS = observations
        if cores == None:
            self._CORES = min(self._CHAINS, np.floor(mp.cpu_count()*.6))
        else:
            self._CORES = min(self._CHAINS, cores)
        self._BURNIN = burnin
        self._N_ITER = n_iter
        self._TUNING_INTERVAL = tuning_interval
        self._CURR_ITER = np.array([1] * self._CHAINS)
        
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
                    p = mp.Process(target=unwrap_self, args=((self, chain, True, mp_chains),))
                    jobs.append(p)
                    p.start()
                    core +=1 
                    if core == self._CORES:
                        for proc in jobs: 
                            proc.join()
                        core = 0
                        jobs = []
                        for ch in range((chain + 1) - self._CORES, chain + 1):
                            self.samples[ch, self._CURR_ITER[ch], :] = np.array(mp_chains[ch][0])
                            self.acceptance[ch, self._CURR_ITER[ch], :] = np.array(mp_chains[ch][1])
                            self._CURR_ITER[ch] += 1

                # pool.close()
                # pool.join()               
            
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

    
    def __sample_chain(self, chain, parallel=False, mp_chains=None):
        '''
        Samples a single chain
        '''
        prev_samples = self.samples[chain, self._CURR_ITER[chain]-1, :]
        new_samples = np.zeros_like(prev_samples)
        # curr_iter = self._CURR_ITER[chain]

        # First generate all the new samples for all of the parameters
        for n, (par, prev_sample, tuning_par) in enumerate(
                zip(self._PRIORS.keys(), prev_samples, self.tuning_pars[chain])):
            new_samples[n] = self.__sample_par(par, prev_sample, tuning_par)
        
        #TODO: Remember to have this working for more variables
        # Calculate likelihoods since the same will be used for all the variables
        self._likelihood_new[chain] = self.__likelihood(
            self._RESPONSES(
                new_samples, self._RESPONSES_MEAN
            )[self._RESPONSE_NAMES[0]]
        )
        self._likelihood_prev[chain] = self.__likelihood(
            self._RESPONSES(
                prev_samples, self._RESPONSES_MEAN
            )[self._RESPONSE_NAMES[0]]
        )
        if not parallel:
        # Then choose samples
            for n, (par, prev_sample, new_sample, tuning_par) in enumerate(
                    zip(self._PRIORS.keys(), prev_samples, new_samples, self.tuning_pars[chain])):
                z, accept = self.__choose(prev_sample, new_sample, par, tuning_par, n, chain)
                self.samples[chain, self._CURR_ITER[chain], n] = z
                self.acceptance[chain, self._CURR_ITER[chain], n] = accept
            self._CURR_ITER[chain] += 1
        else: # In case it is on parallel
            for n, (par, prev_sample, new_sample, tuning_par) in enumerate(
                    zip(self._PRIORS.keys(), prev_samples, new_samples, self.tuning_pars[chain])):
                z, accept = self.__choose(prev_sample, new_sample, par, tuning_par, n, chain)
                mp_chains[chain][0].append(z)
                mp_chains[chain][1].append(accept)
            return mp_chains
            # self._CURR_ITER[chain] += 1
    


    def __choose(self, x, x_new, par, tuning_par, n_par, chain):
        '''
        Whether to keep or discard the new sample
        '''
        prior = self._PRIORS[par]['dist']
        prior_pars = self._PRIORS[par]['pars']
        denominator = self._likelihood_prev[chain] + \
            prior.logpdf(x, *prior_pars)
        numerator = self._likelihood_new[chain] + \
            prior.logpdf(x_new, *prior_pars)
        q_ratio = prior.pdf(x, *self.__moment_match(par, x_new, tuning_par)) / \
            prior.pdf(x_new, *self.__moment_match(par, x, tuning_par))
        R = np.exp(numerator - denominator) * q_ratio
        if R > np.random.uniform():
            return x_new , True
        else:
            return x, False


    def __likelihood(self, mu):
        #TODO: I need to implement this for a multivariate
        logL = norm.logpdf(mu).sum()
        return logL
    

    def __sample_par(self, par, curr_sample, tuning_par):
        if curr_sample == 0: curr_sample = .001
        if tuning_par == 0: tuning_par = .0001
        pars = self.__moment_match(par, curr_sample, tuning_par)
        return self._PRIORS[par]['dist'].rvs(*pars)
    

    def __setup(self):
        '''
        Initialize the objects to store the samples, acceptance rate,
        tuning parameters, etc.
        '''
        self.samples = np.zeros(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_PARS))
        # Define init values from priors
        for n, (_, value) in enumerate(self._PRIORS.items()):
            for chain in range(self._CHAINS):
                self.samples[chain, 0, n] = value['dist'].rvs(*value['pars'])
        # Tuning parameters initialized as one
        self.tuning_pars = np.ones(shape=(self._CHAINS, self._N_PARS))
        # Initialize arrays for responses and acceptance
        self.response_out = np.zeros(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_RESPONSES))
        self.acceptance = np.ones(shape=(self._CHAINS, self._BURNIN + self._N_ITER, self._N_PARS))
        self._likelihood_new = np.zeros(shape=(self._CHAINS))
        self._likelihood_prev = np.zeros(shape=(self._CHAINS))
        # '''
        # Things to keep track of when multiprocessing:
        # Prety much everything modified in sample method
        #     self.samples
        #     self.acceptance
        #     self._CURR_ITER
        # '''
        # if self._CORES > 1:
        #     self._manager = mp.Manager()
        #     self._mp_chains = self._manager.list()
        #     for chain in range(self._CHAINS): 
        #         self._mp_chains.append(
        #             self._manager.list()
        #             )
        #         self._mp_chains[chain].append(self._manager.list()) # samples
        #         self._mp_chains[chain].append(self._manager.list()) # acceptance
            # curr_iter=self._manager.list()
        return
    
    