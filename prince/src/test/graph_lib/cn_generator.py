import scipy.stats
import networkx
import math
import numpy as np


class CNGenerator():
    """ this class implements a random graph generator with the properties
    described in the paper "On the topology characterization of Guifi.net" by L.
    Cerda-Alabern, Wimob 2012. It resambles the topology of large mesh
    networks. Manadatory input to the generator is the number of nodes in the
    core network, optional ones are the number of leaf nodes and the number of
    links in the graph and the variance of the distribution. If not given, the ratio derived from guifi network
    are used."""

    def __init__(self, N, T=0, E=0, S=0, seed=False):
        # number of core nodes
        self.N = N
        if seed:
            np.random.seed(seed)

        # number of leaf nodes
        if not T:
            self.T = int(N*96/4)
        else:
            self.T = T
        if not S:
            S = (2*self.T/self.N)**2
        else:
            self.S = S
        if not E:
            self.E = int(N*1.4962)
        else:
            self.E = E
        # the paramters for the gamma distribution to generate the core network
        # in the original paper this was 0.25 and 0.0115. If I use these
        # values with small networks but they don't fit small networks. alpha is
        # the shape (the larger, the more skewed), beta is the scale (the
        # larger, the smaller is the average)

        #check the input to avoid infinite loops
        if (self.E > self.N*(self.N-1)/2):
            print("Cannot generate the graph. Too many edges")
            exit(1)

        if (self.E < self.N-1):
            print("Cannot generate the graph. The graph will be disconnected")
            exit(1)
        if(self.T<self.N):
            print("Cannot generate the network, T must be greater than N")
            exit(1)

        mu = float(self.T/self.N)
        sigma_2 = float(S)
        sigma = np.sqrt(S)
        """
        Calculate parameters for the Negative Binomial distribution in function of N, T and S
        """
        self.p = float(mu/sigma_2)
        self.n = float(self.p*mu/(1-self.p))
        if (sigma/mu > 4 or sigma/mu <1):
            print("Cannot generate a network with {:f} standard_deviation/average ratio".format(sigma/mu))
            exit(1)
        #self.alpha = 0.25
        #self.beta = 0.0115
        # average degree of core nodes
        # guifi has 2.99
        self.avg_k = 5
        self.a = self.T/(self.N*self.avg_k)

        # number of links in the core graph, if not specified
        # we keep the same ratio of nodes/liks as in guifi

        self.graph = networkx.Graph()

        """
        The method performs a Chi Square statistical test on the random values
        generated by the algorithm
        """
    def stat_check(self,r):

        negBin = scipy.stats.nbinom(n=self.n, p=self.p, loc=1)
        theoreticalFreq = []
        bins = []
        initial = 1
        final = initial+1
        theoreticalFreq.append(negBin.cdf(initial))
        probability = negBin.cdf(final)-negBin.cdf(initial)
        bins.append(initial)
        converged = False
        while(not converged):
            theoreticalFreq.append(probability)
            bins.append(final)
            initial = final
            final = final + 1
            probability = negBin.cdf(final)-negBin.cdf(initial)
            if(probability < float(5.0/self.N)):
                converged = True
        rem = 1-sum(theoreticalFreq)
        theoreticalFreq[len(theoreticalFreq)-1]+=rem
        bins.append(np.inf)
        observedFrequency,edges = np.histogram(r,bins=bins)
        theoreticalFreq = np.multiply(theoreticalFreq,self.N)
        theoreticalFreq =  np.round(theoreticalFreq)
        value,p = scipy.stats.chisquare(f_obs=observedFrequency, f_exp=theoreticalFreq)
        if p > 0.05:
            return True
        else:
            return False




    def gen_core_network(self):

        # step 1 , generate gamma values and assign to core nodes
        negBin = scipy.stats.nbinom(n=self.n, p=self.p)
        max_iteration = 100000
        generated = False

        while not generated:
            #r = np.array([math.floor(x) for x in gamma.rvs(self.N)])
            rem_T = self.T - self.N
            r = np.ones((self.N,))

            i=0
            while(i < len(r) and rem_T):
                v = negBin.rvs(1)
                if(v > rem_T): #too many nodes, assign the remaining and stop
                    r[i] += rem_T
                    rem_T = 0

                else:
                    v=np.floor(v)
                    r[i]+=v
                    rem_T -= v
                    i += 1
            if rem_T: # need more nodes, assign the remaining to the last non-terminal node
                r[self.N-1] += rem_T
            stat_test = self.stat_check(r)

            # impose sum == T and no core node has no leaf

            if sum(r) == self.T and all(r) and stat_test:
                generated = True
            max_iteration -=1
            if not max_iteration:
                print ("I couldn't find a nice random sequence for your parameters!")
                print ("in 100.000 runs!")
                exit(1)


        for idx, g_value in enumerate(r):
            self.graph.add_node(idx, {"prob":g_value})

        remaining_edges = self.E
        # Step 2 add initial edges to guarantee connectivity
        edges_weight = scipy.stats.rv_discrete(name='gamma_d',
                values=(range(len(r)), r/sum(r)))

        for node in self.graph.nodes():
            if remaining_edges <=0: #avoid infinite loop in the case E = N-1
                break
            new_neigh = edges_weight.rvs()
            while (self.graph.has_edge(node, new_neigh) or node == new_neigh):
                new_neigh = edges_weight.rvs()
            self.graph.add_edge(node, new_neigh)
            remaining_edges -=1

        # Step 3 add the remaining links
        # handle with care, this might be large
        #fit_array_values = []
        #fit_array_probs = []
        normalization_factor = 0
        for i in range(self.N):
            for j in range(i+1, self.N):
                normalization_factor+=r[i]*r[j]
                #fit_array_probs.append(max(r[i]*r[j],1))
                #fit_array_values.append((i,j))
                #numpy_arr = np.array(fit_array_probs)
                #numpy_arr = numpy_arr/sum(fit_array_probs)
                #fit_dist = scipy.stats.rv_discrete(name='fit_dist',
                 #   values=(range(len(numpy_arr)), numpy_arr))

        #for i in range(self.E - self.N):

        while (remaining_edges>0):
            #couple = fit_dist.rvs()
            i = np.random.randint(self.N)
            j = np.random.randint(self.N)
            #if (not self.graph.has_edge(fit_array_values[couple][0] ,fit_array_values[couple][1]) and fit_array_values[couple][0] != fit_array_values[couple][1] ):
            if(i!=j and not self.graph.has_edge(i,j)):
                edge_probability = r[i]*r[j]/normalization_factor
                threshold = np.random.uniform()
                if(edge_probability>=threshold):
                #self.graph.add_edge(fit_array_values[couple][0], fit_array_values[couple][1])
                    self.graph.add_edge(i,j)
                    remaining_edges -=1

        return r

    def attach_leave_nodes(self):
        nodes = self.graph.nodes(data=True)
        leaf_node = self.N
        for node in nodes:
            for i in range(int(node[1]['prob'])):
                self.graph.add_edge(leaf_node, node[0])
                leaf_node += 1


    def test_gamma_function(self):
        """ just testing what gamma function looks like """

        import matplotlib.pyplot as plt
        from numpy import histogram
        fig, ax = plt.subplots(1, 1)
        gamma = scipy.stats.gamma(self.alpha, scale=1/self.beta)
        r = gamma.rvs(100000)
        y = histogram(r, bins=100)
        plt.plot(y[1][:-1],y[0])
        ax.set_yscale('log')
        plt.show()

    def fit_func(self, x,y):
        return max(x*y,1)
