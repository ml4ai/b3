from libpgm.nodedata import NodeData;
from libpgm.graphskeleton import GraphSkeleton;
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork;
from libpgm.tablecpdfactorization import TableCPDFactorization;
from subprocess import call;

class Node:
    def __init__(self, name="", values=range(2), parents=[], cpt={}):
        self.name = name;
        self.values = map(str, values);
        self.parents = parents;
        self.cpt = cpt;
        self.sId = "";
    
class Graph:
    def __init__(self):
        self.node = dict();
        self.obs = dict();
           
    def addnode(self,node):
        self.node[node.name] = node;
           
    def removeNode(self, name):
        if self.node.has_key(name):
            del self.node[name];
 
    def addobs(self, node, value):
        self.obs[node.name] = [node, value];
   
    def removeObs(self, name):
        if self.obs.has_key(name):
            del self.obs[name];
    
    def setup(self):
        self.nd = NodeData();
        self.skel = GraphSkeleton();
        self.skel.V, self.skel.E = [], [];
        self.nd.Vdata = {};
        for i,node in enumerate(self.node.values()):
            dNode = {};
            node.sId = str(i);
            dNode["numoutcomes"] = len(node.values);
            dNode["vals"] = node.values;
            dNode["cprob"] = node.cpt;
#             dNode["parents"] = map(lambda x: if x=x.name, node.parents);            
            self.skel.V.append(node.name);
            aParents = [];
            for parent in node.parents:
                if parent==None: continue;
                aParents.append(parent.name);
                self.skel.E.append([parent.name, node.name]); 
            dNode["parents"] = aParents if len(aParents)>0 else None;
            self.nd.Vdata[node.name] = dNode;
        self.skel.toporder();
        self.bn = DiscreteBayesianNetwork(self.skel, self.nd);
        self.fn = TableCPDFactorization(self.bn);
    
#     def setup(self):
#         self.nd = NodeData();
#         self.skel = GraphSkeleton();
#         self.skel.V, self.skel.E = [], [];
#         self.nd.Vdata = {};
#         for i,node in enumerate(self.node.values()):
#             dNode = {};
#             node.sId = str(i);
#             dNode["numoutcomes"] = len(node.values);
#             dNode["vals"] = node.values;
#             dNode["cprob"] = node.cpt;
# #             dNode["parents"] = map(lambda x: if x=x.name, node.parents);            
#             self.skel.V.append(node.name);
#             aParents = [];
#             for parent in node.parents:
#                 if parent==None: continue;
#                 aParents.append(parent.name);
#                 self.skel.E.append([parent.name, node.name]); 
#             dNode["parents"] = aParents if len(aParents)>0 else None;
#             self.nd.Vdata[node.name] = dNode;
#         self.skel.toporder();
#         self.bn = DiscreteBayesianNetwork(self.skel, self.nd);
#         self.fn = TableCPDFactorization(self.bn);
        
    def getPost(self, query, evidence):
        result = self.fn.specificquery(query, evidence);
        return result;       
            
    def write2dot(self, fname = "graph.dot"):
        f = open(fname, "w");
        f.write("digraph G {\n");
        f.write("node[shape=circle, width=0.4];\n");
        for node in self.node.values():
            l = "\""+ node.name +"\"";
            f.write(node.sId);
            if node in map(lambda x : x[0], self.obs):
                f.write("[label="+l+",style=filled,color=blue]");
            else:
                f.write("[label="+l+"]");
            f.write(";\n");
            for parent in node.parents:
                if parent==None: continue;
                f.write(parent.sId+" -> "+ node.sId+";\n");
        f.write("}");
        f.close();
        
    def write2pdf(self, fname = "graph.pdf"):
        if ".pdf" in fname:
            fname = fname[:-4];
        pdfFile = fname+".pdf";
        dotFile = fname+".dot";
        self.write2dot(dotFile);
        call(['dot', '-Tpdf', dotFile, '-o', pdfFile]);
#         call(['C:/Program Files (x86)/Graphviz2.30/bin/dot.exe', '-Tpdf', 
#           './'+dotFile, '-o', './'+pdfFile]);


        