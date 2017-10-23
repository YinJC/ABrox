from collections import Counter, OrderedDict
from itertools import combinations
import pandas as pd
import numpy as np

from abrox.core.abc_utils import toArray


class Report:

    def __init__(self, table, modelNames, paramNames, objective):
        self.table = table
        self.modelNames = modelNames
        self.paramNames = paramNames
        self.objective = objective

    def initParamTable(self):
        """ Initialise the parameter table."""
        paramArray = toArray(self.table, 'param')
        return pd.DataFrame(paramArray, columns=self.paramNames)

    def bayesFactor(self):
        """
        Compute Bayes factor matrix.
        :return: Bayes factor matrix
        """
        nModels = len(self.modelNames)
        counterDict = {idx: 0 for idx in range(nModels)}

        counter = Counter(counterDict)

        counter.update(self.table['idx'])

        orderedCounter = OrderedDict(sorted(counter.items()))

        lowerPart = [b / a for a, b in list(combinations(orderedCounter.values(), 2))]
        upperPart = []
        for t in lowerPart:
            try:
                inverse = 1 / t
                upperPart.append(inverse)
            except ZeroDivisionError:
                upperPart.append(np.inf)

        bfMatrix = np.ones((nModels, nModels))

        bfMatrix[np.tril_indices(nModels, -1)] = lowerPart
        bfMatrix[np.triu_indices(nModels, 1)] = upperPart

        return pd.DataFrame(bfMatrix,columns=self.modelNames)

    def report(self):
        """
        Report final results depending on objective.
        :return: Either Bayes factor matrix (comparison) or parameter summaries.
        """
        if self.objective == "comparison":
            return self.bayesFactor()

        if self.objective == "inference":
            self.initParamTable()
            return self.paramTable.describe().transpose()
