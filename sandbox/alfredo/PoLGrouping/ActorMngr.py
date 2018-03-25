from Actor import Actor;
from ClusteringMngr import ClusteringMngr;
import Image, ImageDraw, ImageFont;

class ActorMngr(object):
    def __init__(self, fileOut):
        self.fileOut = fileOut;
        self.nOldFrame = -1;
        self.aActors = dict();
        self.aActive_Actors = dict();
        self.clusteringMngr = ClusteringMngr(self);
    
    def updateActors(self, aData): #Create & Update Actor's Data
        #Get Actor's Data from File
        nTrackId = aData[0];
        nMinX, nMinY = aData[1], aData[2];
        nMaxX, nMaxY, nFrame = aData[3], aData[4], aData[5]+1;
        sAction = aData[6] if len(aData)==11 else None;
        #If it's New Actor, then Create it
        if not self.aActors.has_key(nTrackId):
            self.aActors[nTrackId] = Actor(nTrackId, self);
        #Update Actor's Data
        self.update_PastFrame(nFrame); #Update only when Next Frames appears
        self.aActors[nTrackId].updateActorData(nFrame, nMinX, nMinY, nMaxX, nMaxY, sAction);
        if not self.aActive_Actors.has_key(nTrackId):
            self.aActive_Actors[nTrackId] = self.aActors[nTrackId];
    
    def update_PastFrame(self, nFrame):
        #Update Actor's Activities & Write Current Frame (Only when Next Frame appears)
        self.nOldFrame = nFrame if self.nOldFrame==-1 else self.nOldFrame;
        if self.nOldFrame!=nFrame:
            if (nFrame) % 1000==0: print "Frame:", nFrame;
#             for actor in self.aActive_Actors.values():
#                 actor.bMissing = actor.nFrame < self.nOldFrame;
            aDelActors = self.updateActivities(nFrame);
#             self.writeXML_PastFrame(); #Write Current Frame
#             self.write_PastFrame(); #Write Current Frame
            self.clusteringMngr.processActors();
#             self.draw_Results(nFrame);
            self.nOldFrame = nFrame;
            for nDelTrackId in aDelActors:
                del self.aActive_Actors[nDelTrackId];
#             self.printCurrentActors(nFrame-1);

    def updateActivities(self, nFrame):
        aDelActors = [];
        nBlankFrames = (nFrame - self.nOldFrame) if self.nOldFrame!=-1 else 1;
        nInitFrame = self.nOldFrame if self.nOldFrame!=-1 else nFrame;
        for i in range(nBlankFrames):
            nFrame = nInitFrame + i;
            for actor in self.aActive_Actors.values():
                actor.bMissing = actor.nFrame < nFrame;
                bNotAdded = not(actor.nTrackId in aDelActors);
                if actor.bMissing and bNotAdded and not(actor.check_Active()):
                    aDelActors.append(actor.nTrackId);
                actor.updateActivities(nFrame); #Update Actor's Activities
#                 if actor.bMissing: continue;
#                 print nFrame, str(actor.getActorData()).translate(None,"[],'");
        return aDelActors;
    
    def plotActors(self):
        self.clusteringMngr.plotActors();
            
    def printCurrentActors(self, nFrame):
        aActorTracksId = [];
        for actor in self.aActive_Actors.values():
            aActorTracksId.append(actor.nTrackId);
        aActorTracksId.sort();
        print nFrame, aActorTracksId;
        
#     def writeXML_PastFrame(self): #Write Full Data to File
# #         print "Writting nFrame:", self.nOldFrame;
#         for actor in self.aActive_Actors.values():
#             if actor.bMissing: continue;
#             actData = str(actor.getActorData()).translate(None,"[],'") + "\n";
#             print self.nOldFrame, str(actor.getActorData()).translate(None,"[],'");
#             self.fileOut.write(actData);
        
    def write_PastFrame(self): #Write Full Data to File
#         print "Writting nFrame:", self.nOldFrame;
        for actor in self.aActive_Actors.values():
            if actor.bMissing: continue;
            actData = str(actor.getActorData()).translate(None,"[],'") + "\n";
            print self.nOldFrame, str(actor.getActorData()).translate(None,"[],'");
            self.fileOut.write(actData);
        
    def draw_Results(self, nFrame):
        print "Writing file ", nFrame;
        sInputPath = "D:/PoL/Frames/";
        sOutPath = "D:/PoL/Frames_Labeled/";
        sImgFile = "visualization " + str(nFrame).zfill(4) + ".jpg";        
        im = Image.open(sInputPath + sImgFile);
        draw = ImageDraw.Draw(im);
        font = ImageFont.truetype("timesbd.ttf", 14);
        for actor in self.aActive_Actors.values():
            if actor.bMissing: continue;
            nX = actor.minPosBB[0];
            nY = actor.maxPosBB[1];
            sTrackId = str(actor.nTrackId);            
            self.draw_Shadow_Text(nX, nY, sTrackId, draw, font);
        del draw;
        im.save(sOutPath + sImgFile, "JPEG");
        
    def draw_Shadow_Text(self, x, y, text, draw, font):
        fillcolor = "white";
        shadowcolor = "black";
        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor);
        draw.text((x+1, y), text, font=font, fill=shadowcolor);
        draw.text((x, y-1), text, font=font, fill=shadowcolor);
        draw.text((x, y+1), text, font=font, fill=shadowcolor);        
        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor);
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor);
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor);
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor);
        # now draw the text over it
        draw.text((x, y), text, font=font, fill=fillcolor);
