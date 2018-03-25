from ActorMngr import ActorMngr;
import time;

if __name__ == '__main__':
#     fileIn = open("./iRobot_0-2195.txt", "r");
#     fileIn = open("./pol_0-8991.txt", "r");
#     fileIn = open("./pol_0-500.txt", "r");
    fileIn = open("./pol_4803-5400.txt", "r");
#     fileIn = open("./chase_JailEscape.txt", "r");
    fileOut = open("./output_Chase.txt", "w");
#     fileOut = open("./output_Dists_NoLosts.txt", "w");
    actorsMngr = ActorMngr(fileOut);
    nInitT = time.time();
    while 1:
        #Read Line of Input File
        sLine = fileIn.readline();
        sLine = sLine.replace("\n","").replace("\"","");
        if not sLine: break;
        aLine = sLine.split(" ");
        if int(aLine[6])==1: continue; #Ignore Lost Frames (Column 6)
        for i,sVal in enumerate(aLine):
            if sVal.replace(".","").replace("-","").isdigit():
                aLine[i] = int(float(sVal));
        #Update All Actors with this Line & Write Results in fileOut
        actorsMngr.updateActors(aLine);
        nFrame = aLine[5];
    #Update & Write Actors's Data of Last Frame
    actorsMngr.update_PastFrame(nFrame+1);
    actorsMngr.plotActors();
    fileIn.close();
    fileOut.close();
    print "Finished. Time:", time.time()-nInitT, "seconds.";
