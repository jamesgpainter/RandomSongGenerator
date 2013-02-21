#!/usr/bin/env python

print 'Content-Type: text/plain'
print

import os
import base64
import httplib
import cgi
from xml.dom.minidom import parseString
import urllib
import random
import sys
import string

# debug mode assigns default parameters
debugmode = 0

if __name__ == '__main__':
	# create unique identifier using a random sequence of letters and digits
	sessionid = ''.join(random.choice(string.ascii_uppercase+string.digits) for x in range(10))
	params = {}
	if (debugmode == 0):
		fieldStorage = cgi.FieldStorage()
		paramnum = 0
		for key in fieldStorage.keys():
			params[paramnum] = fieldStorage[key].value
			paramnum += 1

	else:
		params[0] = "chicken"
		params[1] = "sandwich"

	inputwords = len(params)
	conn = httplib.HTTPConnection("api.wordnik.com")
	headers = {"api_key":"726bdc18913a01ef41002052f4a04e781ebd3f4f737557e47"}
	word = []
	hifreq = 1000
	lofreq = -200

	# get audio recording of each input word
	for curword in params:
		# get the link to the word's MP3
		url = "/v4/word.xml/" + params[curword] + "/audio"
		conn.request("GET", url, "", headers)
		output = conn.getresponse()
		domxml = parseString(output.read())
		mp3url = domxml.getElementsByTagName("fileUrl")[0].childNodes[0].nodeValue
		cmd = "wget '" + mp3url + "' -O " + params[curword] + ".mp3"
		os.system(cmd)
		cmd = "chmod a+rwx " + params[curword] + ".mp3"
		os.system(cmd)

		# decode mp3 to wav format
		cmd = "./mpg123 -w " + params[curword] + ".wav " + params[curword] + ".mp3"
		os.system(cmd)

		# choose a random pitch and apply it using SoX
		pitch = random.randint(lofreq,hifreq)
		cmd = "./sox " + params[curword] + ".wav " + str(sessionid) + "_out1_" + str(curword) + ".wav pitch " + str(pitch)
		os.system(cmd)

		# choose a random tempo and apply it using SoX
		tempo = random.uniform(0.5,1.1)
		infile = str(sessionid) + "_out1_" + str(curword) + ".wav"
		outfile = str(sessionid) + "_out2_" + str(curword) + ".wav"
		cmd = "./sox " + infile + " " + outfile + " tempo " + str(tempo)
		os.system(cmd)

		# choose whether to create an echo
		echo_on = random.randint(1,4)
		if echo_on == 1:
			infile = str(sessionid) + "_out2_" + str(curword) + ".wav"
			outfile = str(sessionid) + "_out3_" + str(curword) + ".wav"
			# apply echo using SoX
			cmd = "./sox " + infile + " " + outfile + " echo .7 .8 100 .4"
			os.system(cmd)
		else:
			infile = str(sessionid) + "_out2_" + str(curword) + ".wav"
			outfile = str(sessionid) + "_out3_" + str(curword) + ".wav"
			os.rename(infile,outfile)

	# concatenate all words
	cmd = "./sox "
	for curword in params:
		cmd2 = "chmod a+rwx " + str(sessionid) + "_out3_" + str(curword) + ".wav"
		os.system(cmd2)
		cmd += str(sessionid) + "_out3_" + str(curword) + ".wav "
	cmd += str(sessionid) + ".wav"
	os.system(cmd)
	cmd = "chmod a+rwx " + str(sessionid) + ".wav"
	os.system(cmd)

	# mpg123 sucks so don't encode the wav file
	#cmd = "./mpg123 -w " + str(sessionid) + ".mp3 " + str(sessionid) + "_full.wav"
	#os.system(cmd)
	#cmd = "chmod a+rwx " + str(sessionid) + ".mp3"
	#os.system(cmd)

	# move the final output file to original client directory
	cmd = "mv " + str(sessionid) + ".wav ../../sing/out"
	os.system(cmd)

	# cleanup
	cmd = "rm *.mp3 *.wav"
	os.system(cmd)

	# send the filename back to the client
	print(str(sessionid) + ".wav")
