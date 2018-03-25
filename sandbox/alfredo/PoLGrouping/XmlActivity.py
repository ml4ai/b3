import xml.etree.ElementTree as elemTree;

class XmlActivity(object):
    nGlobal_ID = 0;
    nAct = dict();
    def __init__(self, sName):
        self.sPath = "./XmlActs/";
        self.sName = sName;
        self.nId = 0;
        if not(XmlActivity.nAct.has_key(sName)): 
            XmlActivity.nAct[sName] = 0;
    
    def setNewID(self):
        XmlActivity.nGlobal_ID += 1;
        self.nId = XmlActivity.nGlobal_ID;
        
    def writeXmlAct(self, aTimes, nScore, aActors, aActorTimes, bOngoing): #Write the Xml File
        return;
        sFile = self.sName+"_{:03d}".format(XmlActivity.nAct[self.sName])+".xml";
        XmlActivity.nAct[self.sName] += 1;
        outf = open(self.sPath + sFile, "w");
        xmlData = self.getXmlData(aTimes, nScore, aActors, aActorTimes, bOngoing);
        tree = elemTree.ElementTree(xmlData);
        root = tree.getroot();
        self.indent(root);
        tree.write(outf);
        
    def getXmlData(self, aTimes, nScore, aActors, aActorTimes, bOngoing):
        #Create Activity Element
        mActElem = dict()
        mActElem["id"] = str(self.nId);
        mActElem["name"] = self.sName;
        timestring = ",".join([str(aTimes[0]), str(aTimes[1])]);
        if bOngoing: timestring += "+";
        mActElem["time"] = timestring;
        xml = elemTree.Element("activity", mActElem);
        #Create Score Sub-Element
        mActElem = dict();
        mActElem["type"] = "observed";
        mActElem["value"] = str(nScore);
        elt = elemTree.Element("score", mActElem);
        xml.append(elt);
        #Create Actors Sub-Elements
        for i,actor in enumerate(aActors):
            xml.append(self.getActorElemT(actor, aActorTimes[i]));
        #Add the "Activities" Wrapper
        xmlData = elemTree.Element("activities", dict());
        xmlData.append(xml);
        return xmlData;
    
    def getActorElemT(self, sName, aTimes):
        mActorElem = dict();
        mActorElem["name"] = sName;
        mActorElem["observed"] = "True" if sName!="null" else "False";
        mActorElem["type"] = "Person" if sName!="null" else "null";
        mActorElem["role"] = "subject";
        timestring = str(aTimes[0])+","+str(aTimes[1]);
    #     if act.ongoing and node.atEnd:
    #         timestring += "+";
        mActorElem["time"] = timestring;
        elt = elemTree.Element("actor", mActorElem);
        return elt;
    
    def indent(self, elem, level=0):
        i = "\n" + level*"  ";
        if len(elem):
            if not elem.text or not elem.text.strip(): elem.text = i + "  ";
            if not elem.tail or not elem.tail.strip(): elem.tail = i;
            for elem in elem: self.indent(elem, level+1);
            if not elem.tail or not elem.tail.strip(): elem.tail = i;
        else:
            if level and (not elem.tail or not elem.tail.strip()): elem.tail = i;
