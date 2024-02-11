class Node:
    """
    Represents a preference graph node
    """

    def __init__(self, id):
        """
        Initialises the node
        :param id: the node's id
        """
        self.id = id
        #We initialise the list of parent nodes (those which generalise this node)
        self.parents = []
        # We initialise the list of sibling nodes (those which are generalised by this node)
        self.siblings = []
        # We initialise the list of users that think this node is appropriate/inappropriate
        self.app = []
        self.inapp = []

    def addparent(self, p):
        """
        Adds a parent to the node's list of parents while also adding all parents of the new parent and updating the
        parent's list of siblings to add the node
        :param p: The new parent node
        :return: The total number of added parents
        """

        #We get all the parents to add
        toadd = [p]+p.getparents()
        count = 0

        #We add each of them and update the total count
        for par in toadd:
            if par not in self.parents:
                self.parents.append(par)
                count += 1

        #We add the node to the list of siblings of the parent nodes
        for s in self.siblings:
            for par in toadd:
                if par not in s.getparents():
                    s.addsingleparent(par)
                    count += 1

        return count

    def addsingleparent(self, p):
        """
        Adds p to the list of parents
        :param p: The parent node to add
        """
        self.parents.append(p)

    def addsibling(self, s):
        """
        Adds a sibling to the node's list of siblings while also adding all siblings of the new sibling and updating the
        siblings's list of parents to add the node
        :param s: The new sibling
        :return: The total number of siblings added
        """

        #We get all the siblings to add
        toadd = [s]+s.getsiblings()
        count = 0

        #We add each of them and update the total count
        for sib in toadd:
            if sib not in self.siblings:
                self.siblings.append(sib)
                count += 1

        #We add the node to the list of parents of the new siblings
        for p in self.parents:
            for sib in toadd:
                if sib not in p.getsiblings():
                    p.addsinglesibling(sib)
                    count += 1

        return count

    def addsinglesibling(self, s):
        """
        Adds s to the list of siblings
        :param s: The sibling node to add
        """
        self.siblings.append(s)

    def setpref(self, user, sign):
        """
        Adds a new preference to the node
        :param user: The user that specified the preference
        :param sign: The "sign" of the preference (1 for appropriateness, -1 for inappropriateness)
        """
        if not user in self.app and not user in self.inapp:
            if sign == 1:
                self.app.append(user)
            else:
                self.inapp.append(user)

    def removepref(self, user, sign):
        """
        Removes a preference of the node's list of preferences
        :param user: The user of the preference
        :param sign: The "sign" of the preference (1 for appropriateness, -1 for inappropriateness)
        """
        if sign and user in self.app:
                self.app.remove(user)
        elif user in self.inapp:
                self.inapp.remove(user)

    def generalises(self, n):
        """
        Checks if this node generalises n
        :param n: The node to check
        :return: True if this node generalises n, False otherwise
        """
        return n in self.siblings

    def isgeneralised(self, n):
        """
        Checks if this node is generalised by n
        :param n: The node to check
        :return: True if this node is generalised by n, False otherwise
        """
        return n in self.parents

    def getparents(self):
        """
        Returns the list of parent nodes
        """
        return self.parents

    def getsiblings(self):
        """
        Returns the list of sibling nodes
        """
        return self.siblings

    def getapp(self):
        """
        Returns the list of users that approve the node
        """
        return self.app

    def getinapp(self):
        """
        Returns the list of users that disapprove the node
        """
        return self.inapp

    def getid(self):
        """
        Returns the id of the node
        """
        return self.id