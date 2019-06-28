# coding = utf-8
# author = huy4ng
# power by python 3.7
import threading
import queue
import requests
import xml.dom.minidom
import argparse
import sys
import subprocess
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

taskqueue = queue.Queue()
class RequestThread(threading.Thread):
    def __init__(self, name):
        super(RequestThread, self).__init__()
        self.name = name
        print("Thread {} is started".format(self.name))
    def run(self):
        while not taskqueue.empty():
            host = taskqueue.get()
            url1 = "https://" + host
            url2 = "http://" + host
            ip = host.split(':')[0]
            port = host.split(':')[1]
            try:
                self.doRequest(url1)
                self.doRequest(url2)
            except:
                print("Error IP and port: {}\t{}".format(ip, port))

    def doRequest(self, url):
        if "https" in url:
            resp = requests.get(url, verify=False, timeout=3)
        else:
            resp = requests.get(url, timeout=3)
        status = resp.status_code
        self.doDeliver(status, url)

    def doDeliver(self, status, url):
        tempurl = "/p1e4s3/"
        filename = ''
        if status == 200:
            url = url + tempurl
            if requests.get(url, timeout=3).status_code == 404:
                filename = '200.txt'
        elif status == 400:
            filename = '400.txt'
        elif status == 403:
            filename = '403.txt'
        elif status == 404:
            filename = '404.txt'
        elif status == 302:
            filename = '302.txt'
        elif status == 500:
            filename = '500.txt'
        else:
            filename = 'other.txt'

        with open(filename, "w+") as file:
            file.write(url + '\n')


def dealXMl(filename):
    file = filename
    dom = xml.dom.minidom.parse(file)
    root = dom.documentElement
    hosts = root.getElementsByTagName('host')
    print(len(hosts))
    with open("url.txt", "w+") as file:
        for host in hosts:
            # print(host.getAttribute("starttime"))
            addresses = host.getElementsByTagName('address')
            for ip in addresses:
                # print(ip.getAttribute('addr'))
                ports = host.getElementsByTagName('port')
                for port in ports:
                    # print(port.getAttribute('portid'))
                    state = port.getElementsByTagName('state')
                    if state[0].getAttribute('state') == 'open':
                        url = "{}:{}".format(ip.getAttribute('addr'), port.getAttribute('portid'))
                        # print(url)
                        creatTaskQueue(url)
                        file.write("http://"+ url +"\n")
                        file.write("https://"+ url +"\n")

def creatTaskQueue(url):
    taskqueue.put(url)

def usage():
    parser = argparse.ArgumentParser(usage="python {} -i <ip.txt> -t <threads>".format(sys.argv[0]),
                                  description="Fastly to deal ports")
    parser.add_argument('--input', '-i', help="the file of ip list")
    parser.add_argument('--threads', '-t', default=5, help="the number of threads")
    parser.add_argument('--output', '-o', default='nmap.xml', help="the file of result in xml type")
    parser.add_argument('--ips', '-p', help="Example: 192.168.1.1/16")
    return parser.parse_args()

if __name__ == '__main__':
    args = usage()
    inputfile = args.input
    threadsnumber = args.threads
    outputfile = args.output
    if inputfile is None:
        ips = args.ips
        masscan_cmd = "masscan -p 1-65535 {} -oX {} --rate=2000".format(ips, outputfile)
    else:
        masscan_cmd = "masscan -p 1-65535 -iL {} -oX {} --rate=2000".format(inputfile, outputfile)
    subprocess.Popen(masscan_cmd, shell=True).wait()
    dealXMl(outputfile)
    threads = []
    for i in range(threadsnumber):
        threads.append(RequestThread(i))
    for thread in threads:
        thread.start()
