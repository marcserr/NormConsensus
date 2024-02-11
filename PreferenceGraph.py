import math
from Node import *
import random

class PreferenceGraph:
    """
    Represents a preference graph
    """

    def __init__(self):
        #The list of nodes of the graph
        self.nodes = []
        #The list of nodes in No+
        self.noplus = []
        #The list of nodes in No-
        self.nominus = []
        #The list of nodes in No+*
        self.noplusstar = []
        # The list of nodes in No-*
        self.nominusstar = []
        #The list of users represented in the graph's preferences
        self.users = []
        #The list of nodes whose appropriateness has been propagated
        self.apppropnodes = []

    def nonsiblings(self, n1):
        """
        Returns the nodes in the graph that are not siblings of n1
        :param n1: A Node
        :return: A list of Nodes
        """
        nonsib = []
        for n2 in self.nodes:
            if n2 != n1 and n2 not in n1.getsiblings():
                nonsib.append(n2)
        return nonsib

    def generate(self, numNodes, RelPer, numUsers, PrefProb, appProb):
        """
        Generates a random preference graph
        :param numNodes: The number of nodes to generate
        :param RelPer: A number in [0,1] representing the percentage of generalisation relations out of all possible
        :param numUsers: The number of users to generate
        :param PrefProb: The probability in [0,1] of a user defining a preference for each generated node
        :param appProb: The probability in [0,1] of a preference being an approval preference
        """

        #Generation of users
        for u in range(numUsers):
            self.users.append("u"+str(u))

        #Generation of context nodes
        num = 0
        for n in range(numNodes):
            newnode = Node(num)
            self.nodes.append(newnode)
            num += 1

        #Generation of generalisation relations
        numRels = math.floor(((numNodes*(numNodes-1))/2.0)*RelPer)
        currentRels = 0
        while currentRels < numRels:
            n1 = random.choice(self.nodes)
            while len(n1.getsiblings()) == len(self.nodes)-1:
                n1 = random.choice(self.nodes)
            n2 = random.choice(self.nonsiblings(n1))
            parrels = n2.addparent(n1)
            sibrels = n1.addsibling(n2)
            currentRels += parrels+sibrels-1

        #Generation of preferences
        for u in self.users:
            for n in self.nodes:
                rannumber = random.random()
                if rannumber <= PrefProb:
                    rannumber = random.random()
                    if rannumber <= appProb:
                        n.setpref(u, 1)
                    else:
                        n.setpref(u, 0)

    def propagate(self):
        """
        Propagates the preferences in the graph and finds the No+, No-, and No+* sets
        """
        #We build No+
        self.getnoplus()
        #We build No-
        self.getnominus()
        #We Propagate appropriateness as described in the paper
        self.apppropagation()
        #We propagate inappropriateness as described in the paper
        self.inapppropagation()
        #Finally, we perform preference cancellation as described in the paper
        self.cancellation()

    def getnoplus(self):
        """
        Builds No+, that is the list of nodes that are approved by some user and disapproved by none
        """
        for n in self.nodes:
            if n.getapp() and not n.getinapp():
                self.noplus.append(n)

    def getnominus(self):
        """
        Builds No-, that is the list of nodes that are disapproved by some user and approved by none
        """
        for n in self.nodes:
            if n.getinapp() and not n.getapp():
                self.nominus.append(n)

    def getnode(self, id):
        """
        Finds the node of the id in the graph
        :param id: The id of the node to find
        :return: The found node
        """
        return self.nodes[id]

    def apppropagation(self):
        """
        Propagates apropriateness as described in the paper
        """
        for n in self.nodes:
            for u in n.getapp():
                toprop = n.getsiblings()
                for sib in n.getsiblings():
                    if u in sib.getinapp():
                        toprop.remove(sib)
                readd = []
                for sib in toprop:
                    for s in sib.getsiblings():
                        if s not in toprop:
                            readd.append(s)
                toprop = toprop + readd
                for s in toprop:
                    s.setpref(u, 1)
                    self.apppropnodes.append(s)

    def inapppropagation(self):
        """
        Propagates inapropriateness as described in the paper
        """
        for n in self.nodes:
            for u in n.getinapp():
                toprop = n.getsiblings()
                for sib in n.getsiblings():
                    #Extra step: if the node is appropriate because of propagation, we leave the pref. unspecified
                    if u in sib.getapp() and sib not in self.apppropnodes:
                        toprop.remove(sib)
                    elif u in sib.getapp() and sib not in self.apppropnodes:
                        sib.removepref(u, 1)
                readd = []
                for sib in toprop:
                    for s in sib.getsiblings():
                        if s not in toprop:
                            readd.append(s)
                toprop = toprop + readd
                for s in toprop:
                    s.setpref(u, -1)

    def cancellation(self):
        """
        Cancels appropriateness of any parent of an inappropriate node and inappropriatenesss of any parent of an
        appropriate node
        """
        for n in self.nodes:
            for u in n.getinapp():
                for p in n.getparents():
                    p.removepref(u, 1)

        for n in self.nodes:
            for u in n.getapp():
                for p in n.getparents():
                    p.removepref(u, -1)

    def buildnoplusstar(self):
        """
        Builds the list of nodes in No+* that is those approved by
        """
        for n in self.nodes:
            if n.getapp() and not n.getinapp():
                self.noplusstar.append(n)

    def buildnominusstar(self):
        """
        Builds the list of nodes in No+* that is those approved by
        """
        for n in self.nodes:
            if n.getinapp() and not n.getapp():
                self.nominusstar.append(n)

    def positivesearchspace(self):
        """
        Finds the nodes in the positive search space Con+ (see the formal definition in the paper)
        :return: the list of nodes in Con+
        """

        #We find No+*
        if not self.noplusstar:
            self.buildnoplusstar()

        #We initialise Exc and Con+
        exc = []
        conplus = []

        #We calclate Exc. For each node in No+* we do
        for n in self.noplusstar:
            if n.getparents():
                #Get the parents of the node that are also in No+*
                nopluspropparents = []
                for p in n.getparents():
                    if p in self.noplusstar:
                        nopluspropparents.append(p)
                #Get the parents of the node that have some sibling in No+* that generalises the node
                mid = []
                for p in n.getparents():
                    for s in p.getsiblings():
                        if s in nopluspropparents:
                            mid.append(p)
                #We will exclude the node if all its parents are either on nopluuspropparents or mid
                exclude = True
                for p in n.getparents():
                    if p not in nopluspropparents or p not in mid:
                        exclude = False
                if exclude:
                    exc.append(n)

        #The nodes in Con+ are those that are in No+* and not in Exc
        #We check we are not excluding nodes in No+ as required by the formal definition
        for n in self.noplusstar:
            if n in self.noplus and n in self.noplusstar:
                conplus.append(n)
            elif n not in exc:
                conplus.append(n)

        return conplus

    def negativesearchspace(self):
        """
        Finds the nodes in the positive search space Con- (analogous definition to Con-)
        :return: The list of nodes in No-
        """
        # We find No-*
        if not self.nominusstar:
            self.buildnominusstar()

        # We initialise Exc and Con-
        exc = []
        conminus = []

        # We calclate Exc. For each node in No-* we do
        for n in self.nominusstar:
            if n.getparents():
                # Get the parents of the node that are also in No-*
                nominusminusparents = []
                for p in n.getparents():
                    if p in self.nominusstar:
                        nominusminusparents.append(p)
                # Get the parents of the node that have some sibling in No-* that generalises the node
                mid = []
                for p in n.getparents():
                    for s in p.getsiblings():
                        if s in nominusminusparents:
                            mid.append(p)
                # We will exclude the node if all its parents are either on nominusminusparents or mid
                exclude = True
                for p in n.getparents():
                    if p not in nominusminusparents or p not in mid:
                        exclude = False
                if exclude:
                    exc.append(n)

        # The nodes in Con- are those that are in No-* and not in Exc
        # We check we are not excluding nodes in No- as required by the formal definition
        for n in self.nominusstar:
            if n in self.nominus and n in self.nominusstar:
                conminus.append(n)
            elif n not in exc:
                conminus.append(n)

        return conminus

    def nodesUser(self, sign, searchspace):
        """
        Finds the nodes that have been appropved/disapproved by each user in the searchspace
        :param sign: 1 if we want to find the approved nodes, -1 for the disapproved oness
        :param searchspace: The list of nodes in the searchspace
        :return: A dictionary were users are the keys and the values are the nodes approved/disapproved by the user
        """

        #We initialise the dictionary awith the user keys
        retdict = {}
        for u in self.users:
            retdict[u] = []

        #For each node in the searchspace
        for n in searchspace:

            #If we are checking appropriate nodes, we add the node to the users that have approved it
            if sign == 1:
                for uapp in n.getapp():
                    retdict[uapp].append(n.getid())

            # If we are checking inappropriate nodes, we add the node to the users that have disapproved it
            else:
                for uinapp in n.getinapp():
                    retdict[uinapp].append(n.getid())

        return retdict