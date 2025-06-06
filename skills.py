import numpy as np
import math


class Skill:
    def __init__(self):
        pass


    def check(self, level, learn=True):
        """
        Input: 
        - level (int): The level the skill is checked at
        - learn (bool): Decides if this use of skill check should lead to improvement
        or not. Defaults to True

        Output:
        - Generalized mean of the performance of every ancestor skill.

        Side effect:
        - For every dependency, the skill check is done up until it reaches an attribute,
        at which point the mean of that attribute is updated based on the surprisal of
        the outcome.
        """
        pass 

class Attribute(Skill):
    def __init__(self, learning_rate):
        """
        Paramters:

        - learning_rate (float): A float denoting how fast a skill is learned.
        """
        self._mean = 0
        self.learning_rate = learning_rate

    def normal_cdf(self, level):
        """
        Returns the probability that a random sample of a normal distribution is below
        the input "level".
        """
        z = (level - self._mean) / np.sqrt(2)
        return 0.5 * (1 + math.erf(z))
    
    def get_mean(self):
        return self._mean

    def check(self, level, learn=True):
        p_failure = self.normal_cdf(level)
        performance = self._mean + np.random.normal()
        if performance < level:
            surprisal = -np.log(p_failure)
        else:
            surprisal = -np.log(1-p_failure)
        if learn:
            self._mean += self.learning_rate * surprisal # learn!
        return performance


class Composite(Skill):
    def __init__(self, ancestors, exp):
        """
        Parameters:

        - ancestors (dict): A dictionary with all the ancestor skills for this skill in the
            form of {skill : alpha_j} where alpha_j is the requirement of the j-th ancestor.
        - exp (float): The exponent used to calculate the generalized mean.
        """
        self.ancestors = ancestors
        self.exp = exp

    def generalized_mean(self, anc_results):
        """
        Input:
        - anc_results (list): list of the results of ancestor skill checks

        Output:
        - Single value denoting the generalized mean of every value in anc_results
        """
        n = len(anc_results)
        sum = 0
        for (result, alpha) in anc_results:
            sum += (result/alpha) ** self.exp
        return (sum/n) ** (1/self.exp)

    def check(self, level, learn=True):
        anc_results = []
        for ancestor, alpha in self.ancestors.items():
            anc_results.append(((ancestor.check(level * alpha, learn) / alpha), alpha))
        return self.generalized_mean(anc_results)


