import numpy as np, random as rd
import statistics as stats

def randomBool(qVal):
    # choice = np.random.choice([0, 1], p=[qVal, 1 - qVal])
    choice = np.random.binomial(n=1, p=qVal)
    return choice


class CoveredGraph:
    # We consider complete trees of k layers (k ≥ 2) and degree d (d ≥ 2)
    # The chosen intervention is the values {1,1,...,d} at the parents of the 1st node in the penultimate layer
    # The SCM is that:
    #   1. each of the internal nodes which are not in the penultimate layer are simply sum variables
    #   AUTHOR COMMENT:
    #   Earlier we chose 'OR' for these variables, but in large networks, it almost always gives value 1 at the output.
    #   2. all internal nodes (except the last) in the penultimate layer take value 1 with probability mu
    #   3. the last node in the penultimate layer takes value:
    #       3a. 1 with probability mu + epsilon if all its parents are set to 1.
    #       3b. 1 with probability mu otherwise.
    #
    # The leaf nodes are boolean variables that take value 1 as per the q values
    #
    # We will use the array representation so that we can easily find the parent node of any given node.
    # For example:
    #   1. Reward node is node at index 0
    #   2. The children of the reward node are variables with index 1-d
    #   3. The child of node 1 is at index d + 1
    #
    # In general, the parent of node at index k is the node with index m = ceil(k/d) + 1

    def __new__(cls, *args, **kwargs):
        print("1. Create a new instance of the graph.")
        return super().__new__(cls)

    def __init__(self, degree, numLayers, initialQValues=0.01, mu=0.05, epsilon=0.1):
        print("2. Initialize the new instance of Point.")
        self.degree = degree  # number of edges per node.
        self.numLayers = numLayers  # Root node is considered layer 1. So a 2 layer tree has only leaves and root
        self.numNodes = int((degree ** (numLayers + 1) - 1) / (degree - 1))
        self.numNodes = int((degree ** (numLayers + 1) - 1) / (degree - 1))
        self.numLeaves = int(degree ** (numLayers))
        self.numInternal = self.numNodes - self.numLeaves
        self.numPenultimate = int(degree ** (numLayers - 1))
        self.mu = mu
        self.epsilon = epsilon
        self.leafQvals = np.ones(self.numLeaves) * initialQValues

    def __repr__(self) -> str:
        return f"{type(self).__name__}(degree={self.degree}, numLayers={self.numLayers}, " \
               f"numNodes={self.numNodes}, numLeaves={self.numLeaves}, , numInternal={self.numInternal}" \
               f"\nnumPenultimate={self.numPenultimate}, mu={self.mu}, epsilon={self.epsilon}" \
               f"\nleafQvals={self.leafQvals})"

    def checkLeafIndex(self, k):
        if k < 0 or k >= self.numNodes:
            return "Not a node index"
        if k >= (self.numNodes - self.numLeaves):
            return 1
        return 0

    def checkPenultimateLayer(self, k):
        if k < 0 or k >= self.numNodes:
            return -1
        if (self.numNodes - self.numLeaves - 1) >= k >= (self.numNodes - self.numLeaves - self.numPenultimate):
            return 1
        return 0

    def checkChosenParentPenultimate(self, k):
        if k < 0 or k >= self.numNodes:
            return -1
        if k == (self.numNodes - self.numLeaves - 1):
            return 1
        return 0

    def getParentIndex(self, k):
        if k < 0 or k >= self.numNodes:
            return "Not a node index"
        if k == 0:
            return -1
        parentIndex = np.ceil(k / self.degree) - 1
        return parentIndex

    def getChildIndices(self, k):
        if self.checkLeafIndex(k):
            return -1
        startIndex = self.degree * k + 1
        endIndex = self.degree * (k + 1)
        childrenIndices = list(range(startIndex, endIndex + 1))
        return childrenIndices

    def doNothing(self):
        sampledVals = np.zeros(self.numNodes)
        for currentIndex in reversed(range(self.numNodes)):
            if self.checkLeafIndex(currentIndex):
                leafIndex = currentIndex-self.numInternal
                qVal = self.leafQvals[leafIndex]
                sampledVals[currentIndex] = randomBool(qVal)
            elif self.checkPenultimateLayer(currentIndex):
                if self.checkChosenParentPenultimate(currentIndex):
                    childIndices = self.getChildIndices(currentIndex)
                    if sampledVals[childIndices].sum() == self.degree:
                        qVal = self.mu + self.epsilon
                    else:
                        qVal = self.mu
                    sampledVals[currentIndex] = randomBool(qVal)
                else:
                    qVal = self.mu
                    sampledVals[currentIndex] = randomBool(qVal)
            else:
                childIndices = self.getChildIndices(currentIndex)
                # sum = 0
                # for j in childIndices:
                #     sum += sampledVals[j]
                # sampledVals[i] = sum
                sampledVals[currentIndex] = (sampledVals[childIndices].sum() > 0)*1
        return sampledVals

    def doOperation(self,intervenedIndices,intervenedValues):
        for currentIndex in intervenedIndices:
            if not self.checkLeafIndex(currentIndex):
                raise Exception("Sorry, not a valid do() operation")
        for value in intervenedValues:
            if value not in [0,1]:
                raise Exception("Sorry, not a valid do() operation")

        sampledVals = np.zeros(self.numNodes)
        for currentIndex in reversed(range(self.numNodes)):
            if self.checkLeafIndex(currentIndex):
                if currentIndex in intervenedIndices:
                    currentIndexLocationInInterevenedArray = intervenedIndices.index(currentIndex)
                    intervenedValue = intervenedValues[currentIndexLocationInInterevenedArray]
                    sampledVals[currentIndex] = intervenedValue
                else:
                    leafIndex = currentIndex - self.numInternal
                    qVal = self.leafQvals[leafIndex]
                    sampledBoolean = randomBool(qVal)
                    sampledVals[currentIndex] = sampledBoolean

            elif self.checkPenultimateLayer(currentIndex):
                if self.checkChosenParentPenultimate(currentIndex):
                    childIndices = self.getChildIndices(currentIndex)
                    if sampledVals[childIndices].sum()==self.degree:
                        qVal = self.mu + self.epsilon
                    else:
                        qVal = self.mu
                    sampledVals[currentIndex] = randomBool(qVal)
                else:
                    qVal = self.mu
                    sampledVals[currentIndex] = randomBool(qVal)
            else:
                childIndices = self.getChildIndices(currentIndex)
                # sum = 0
                # for j in childIndices:
                #     sum += sampledVals[j]
                # sampledVals[i] = sum
                sampledVals[currentIndex] = (sampledVals[childIndices].sum() > 0)*1
        return sampledVals

if __name__ == "__main__":
    np.random.seed(8)
    np.set_printoptions(precision=3)
    # np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
    rd.seed(8)
    cgraph = CoveredGraph.__new__(CoveredGraph)
    cgraph.__init__(degree=3, numLayers=4, initialQValues=0.0,mu=0.05,epsilon=0.05)
    print("cgraph=", cgraph)
    print("cgraph.numNodes=", cgraph.numNodes)
    for i in range(cgraph.numNodes):
        print("child Node = %d, parentNode = %d" % (i, cgraph.getParentIndex(i)))

    for i in range(cgraph.numNodes):
        print("parent Node = %d, child Nodes = %s" % (i, cgraph.getChildIndices(i)))

    graphObs = cgraph.doNothing()
    print("graphObs=",graphObs)
    rewards = []
    for i in range(10000):
        graphObs = cgraph.doNothing()
        rewards.append(graphObs[0])
    # print("cgraph Values on do nothing =", rewards)
    print("cgraph Average Rewards on Do nothing =", stats.fmean(rewards))
    rewardsOnDo = []
    for i in range(10000):
        graphObs = cgraph.doOperation([118,119,120],[1,1,1])
        rewardsOnDo.append(graphObs[0])
    # print("cgraph Values on do lastNodes =", rewardsOnDo)
    print("cgraph Average Rewards on Do =", stats.fmean(rewardsOnDo))
