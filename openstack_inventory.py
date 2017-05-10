#!/usr/bin/env python


from __future__ import print_function
from novaclient import client
import os, sys, json


def main(args):
	
	nt = client.Client("2", "t.han6@student.unimelb.edu.au", "ZDI5NzgzYjZiZTVlOTlk", "b44f80a0b9574456b457fe97f029b1c9", "https://keystone.rc.nectar.org.au:5000/v2.0/")

	serverlist = nt.servers.list();
	print(serverlist)

	f=open('hosts', 'w')

        f.write('[dbServers]\n')
	for server in nt.servers.list():
		ip =server.networks.get('pawsey-01')
                ip_addr = str(ip)
                ip_addr = ip_addr[3:-2]
		f.write(str(ip_addr)+'\n')
		print(ip_addr)

        f.write('[slaveServers]\n')
	for server in nt.servers.list():
		ip =server.networks.get('pawsey-01')
                ip_addr = str(ip)
                ip_addr = ip_addr[3:-2]
		f.write(str(ip_addr)+'\n')
		

        f.write('[masterServer]\n')

        
        
		




if __name__ == "__main__":
	main(sys.argv)

