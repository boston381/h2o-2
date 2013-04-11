import os, json, unittest, time, shutil, sys
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd,h2o_hosts, h2o_browse as h2b, h2o_import as h2i, h2o_hosts
import h2o_exec as h2e
import time, random

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global localhost
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(3,java_heap_GB=10)
        else:
            h2o_hosts.build_cloud_with_hosts(3)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_from_import(self):
        # just do the import folder once
        # importFolderPath = "/home/hduser/hdfs_datasets"
        importFolderPath = '/home/0xdiag/datasets'

        h2i.setupImportFolder(None, importFolderPath)
        timeoutSecs = 500

        #    "covtype169x.data",
        #    "covtype.13x.shuffle.data",
        #    "3G_poker_shuffle"
        #    "covtype20x.data", 
        #    "billion_rows.csv.gz",
        csvFilenameAll = [
            ("manyfiles-nflx-gz/file_1.dat.gz", "file_1.dat.gz"),
            # do it twice
            ("manyfiles-nflx-gz/file_1.dat.gz", "file_1.dat.gz"),
            # ("covtype.data", "covtype.data"),
            # ("covtype20x.data", "covtype20x.data"),
            # "covtype200x.data",
            # "100million_rows.csv",
            # "200million_rows.csv",
            # "a5m.csv",
            # "a10m.csv",
            # "a100m.csv",
            # "a200m.csv",
            # "a400m.csv",
            # "a600m.csv",
            # "billion_rows.csv.gz",
            # "new-poker-hand.full.311M.txt.gz",
            ]
        # csvFilenameList = random.sample(csvFilenameAll,1)
        csvFilenameList = csvFilenameAll

        # pop open a browser on the cloud
        h2b.browseTheCloud()

        # split out the pattern match and the filename used for the hex
        for csvFilepattern, csvFilename in csvFilenameList:
            # creates csvFilename.hex from file in importFolder dir 

            start = time.time()
            parseKey = h2i.parseImportFolderFile(None, csvFilepattern, importFolderPath, 
                key2=csvFilename + ".hex", timeoutSecs=500)
            elapsed = time.time() - start
            print "parse end on ", csvFilepattern, 'took', elapsed, 'seconds.',\
                "%d pct. of timeout" % ((elapsed/timeoutSecs) * 100)

            print csvFilepattern, 'parse time:', parseKey['response']['time']
            print "Parse result['destination_key']:", parseKey['destination_key']

            # We should be able to see the parse result?
            inspect = h2o_cmd.runInspect(key=parseKey['destination_key'])

            # the nflx data doesn't have a small enough # of classes in any col
            # use exec to randomFilter out 200 rows for a quick RF. that should work for everyone?
            origKey = parseKey['destination_key']
            # execExpr = 'a = randomFilter('+origKey+',200,12345678)' 
            execExpr = 'a = slice('+origKey+',1,200)' 
            h2e.exec_expr(h2o.nodes[0], execExpr, "a", timeoutSecs=30)
            # runRFOnly takes the parseKey directly
            newParseKey = {'destination_key': 'a'}


            print "\n" + csvFilepattern
            start = time.time()
            # poker and the water.UDP.set3(UDP.java) fail issue..
            # constrain depth to 25
            print "Temporarily hacking to do nothing instead of RF on the parsed file"
            ### RFview = h2o_cmd.runRFOnly(trees=1,depth=25,parseKey=newParseKey, timeoutSecs=timeoutSecs)
            ### h2b.browseJsonHistoryAsUrlLastMatch("RFView")

            sys.stdout.write('.')
            sys.stdout.flush() 

if __name__ == '__main__':
    h2o.unit_main()
