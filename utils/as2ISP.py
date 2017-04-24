import pickle as pkl
import time
from datetime import datetime
import os

class AS2ISP:
    def __init__(self, data_path):
        self.raw_path = os.path.join(data_path, "raw")
        self.export_path = os.path.join(data_path, "as2isp.pkl")
        self.date = []
        self.as2isp = None

        #self.saveDB()
        self.loadDate()
        self.loadDB()

    def loadDate(self):
        for fname in os.listdir(self.raw_path):
          if "as-org2info" in fname:
            date = fname.split(".")[0]
            self.date.append(date)

    def loadDB(self):
        t = time.time()
        self.as2isp = pkl.load(open(self.export_path))
        print 'peering DB loaded done: it took %s secs' % (time.time() - t)

    def getISP(self, date, asnum ):
        dbdate = self.date[min(range(len(self.date)),
            key=lambda v: abs((datetime.strptime(self.date[v], "%Y%m%d") - datetime.strptime(date, "%Y%m%d")).days))]
        #print dbdate
        if asnum not in self.as2isp[dbdate]:
            return None, None

        return self.as2isp[dbdate][asnum]

    def saveDB(self):
        ORG_NAME = "format:org_id|changed|org_name|country|source"
        AS_ORG = "format:aut|changed|aut_name|org_id|source"
        asnumDB = {}

        for fname in os.listdir(self.raw_path):
            date = fname.split(".")[0]
            asnumDB[date] = {}
            org_id2name = {}
            as_asnum2name = {}

            line_type = 0
            for line in open(os.path.join(self.raw_path, fname)):
                if(ORG_NAME in line):
                    line_type = 1
                    continue
                elif(AS_ORG in line):
                    line_type = 2
                    continue

                if(line_type == 0):
                    continue

                if(line_type == 1): ## ORG_NAME
                    org_id, changed, org_name, country, source = line.split("|")
                    org_id2name[org_id] = (org_name, country)

                elif(line_type == 2): ## AS_ORG
                    asnum, changed, aut_name, org_id, source = line.split("|")
                    asnumDB[date][asnum] = org_id2name[org_id]

        pkl.dump(asnumDB, open(self.export_path, "wb"))
