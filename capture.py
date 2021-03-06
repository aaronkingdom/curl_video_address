#encoding: utf8
import pcap
import dpkt
import threading
import os
import time
from time import sleep
import logging
import requests

class TrafficCapture(object):
    def __init__(self, netcardName, title,  loggingName = None):
        self.stopFlag = False
        self.pc = pcap.pcap(netcardName)    #注，参数可为网卡名，如eth0
        self.pc.setfilter('tcp[20:2]=0x4745 or tcp[20:2]=0x4854')  #设置监听过滤器 HTTP请求的TCP头为GET 或者 HTTP
        self.downloadThread = []
        self.downloadedURL = dict()
        self.mergeList = []
        self.title = title.replace("/","_")
        self.floderName = u"download/" + self.title + u"/"
        if not os.path.exists(self.floderName):
            os.makedirs(self.floderName)

        # if loggingName is None:
        #     self.logger = logging.getLogger("curl_video")
        #     self.logger.setLevel(logging.DEBUG)      
        #     formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        #     self.logger.setFormatter(formatter)
            
        # else:
        #     self.logger = getLogger(loggingName)

    

    def wrapDownloadURL(self, requrl):
        # logger.debug("in downloadfile, " + requrl)
        if(requrl.find('?') != -1):
            requrl = requrl.split("?")[0] 
        if(requrl.find("http://") == -1):
            requrl = "http://" + requrl
        return requrl

    def downloadFile(self, fileurl, storename):
        # logger.info("strat download " + fileurl)
        os.system("curl -o " + storename + " " + fileurl)
        # logger.info("finish download " + fileurl)

    def stop(self):
        self.stopFlag = True
        

    def start(self):
        for ptime,pdata in self.pc:    #ptime为收到时间，pdata为收到数据
            if self.stopFlag:
                print "set stop flag true"
                break
            #对抓到的以太网V2数据包(raw packet)进行解包
            p=dpkt.ethernet.Ethernet(pdata)
            if p.data.__class__.__name__=='IP':
                ip='%d.%d.%d.%d'%tuple(map(ord,list(p.data.dst)))
                
                if p.data.data.__class__.__name__=='TCP':
                    if p.data.data.dport == 80:
                       
                        header = p.data.data.data # by gashero
                        headerArr = header.split('\r\n')
                        url = headerArr[0].split(' ')[1]
                        host = headerArr[1].split(' ')[1]
                        requestUrl = host + url

                        if requestUrl.find('.flv') != -1 or requestUrl.find('.mp4') != -1:
                            videoUrl = self.wrapDownloadURL(requestUrl)
                            # logger.info(videoUrl) 
                            if(not self.downloadedURL.has_key(videoUrl)):
                                print videoUrl
                                # logger.debug("never download this url: " + videoUrl)
                                nowTime = time.time()
                                fileName = str(nowTime) + "." + videoUrl.split(".")[-1]
                                fileName =  self.floderName + fileName
                                self.downloadedURL[videoUrl] = (nowTime, fileName)
                                self.mergeList.append(fileName)
                                # t = threading.Thread(target=self.downloadFile,args=(videoUrl , fileName))
                                # self.downloadThread.append(t)
                                # t.start()

                            # f = open(self.floderName + u"list.txt", "w")
                            # toWrite = ["file '" + item + "'\n" for item in self.mergeList]
                            # f.writelines(toWrite)
                            # f.close()

        # for t in self.downloadThread:
        #     t.join()

    def getDownloadFiles(self):
        return self.mergeList

    def getDownloadUrls(self):
        return [url for (url, filename) in self.downloadedURL.iteritems()]


def sleepForWhile(arg):
    sleep(10)
    # arg.stop()
    print "time over"
    # make a http get request, let the capture thread return
    # sleep(2)
    # a = requests.get("http://www.baidu.com")


if __name__ == '__main__':
    tc = TrafficCapture("enp5s0", u"hello", "hello")
    t = threading.Thread(target=sleepForWhile, args= (tc,))
    t.start()
    tc.start()
    print 'finish'

