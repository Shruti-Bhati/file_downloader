import sys
import os
import urllib2
import requests
import time
import math
import multiprocessing.dummy as mp

def combine_file_parts(parts):
	final = ''
	for p in parts:
		final += p
	return final

def download(s,e,url):
	req = urllib2.Request(url)
	req.headers['Range'] = 'bytes=%s-%s' % (s, e)
	f = urllib2.urlopen(req)
	data = f.read()
	return data

def parallel_downloads(start,end,url):
	process_chunk = 1000.0
	arguments = list()
	pointer = start

	#Dynamically finding how many parallel processes need to be createds
	processes = int(math.ceil((end-start)/process_chunk))
	for i in range(processes):
		s = pointer
		e = pointer + int(process_chunk)
		if e > end:
			e = end
		arguments.append([s,e,url])
		pointer = pointer + int(process_chunk) + 1

	#Create a pool of processes that download file in parallel
	pool = mp.Pool(processes)
	
	results = pool.map_async(lambda x:download(*x),arguments)
	#Map async ensure the results are returned and in order

	file_parts = results.get()
	#we then combine the results from the downloads
	return combine_file_parts(file_parts)

def download_with_resume(url,destination):
	if not url or len(url) == 0:
		print 'No download URL given.Exiting'
		sys.exit()

	#Temp directory to store part of file
	temp_dir = "./downloader_temp"
	if not os.path.exists(temp_dir):
		os.mkdir(temp_dir)
	filename = url.split("/")[-1]
	tmp_file = temp_dir + "/" + filename + ".part"
	
	#Check destination
	if destination:
		if not os.path.exists(destination):
		    print "Destination folder doesnt exist.Please check.Exiting program"
		    sys.exit()
	else:
		destination = "."
	final_file = destination + "/" + filename

	if os.path.exists(final_file):
		print "File already exists at ",final_file
		sys.exit()

	#Divide file into chunks and download each chunk in parallel
	chunk_size = 1000 * 1000 * 10


	#Assuming the server on which the file is hosted allows fetching header details
	try:
		file_size = int(requests.head(url,headers={'Accept-Encoding': 'identity'}).headers['content-length'])
	except Exception:
		print "Error while getting infomation from the server.Exiting program"
		sys.exit()

	print "Now downloading file",filename,"\nTotal filesize",file_size
	
	#Check if part of file was already downloaded, if yes read size and continue from there
	if os.path.exists(tmp_file):
		chunk_start = os.path.getsize(tmp_file) 
		print "Found part of file,Resuming download."
	else:
		chunk_start = 0
	
	try:
		while chunk_start < file_size:
			print "........."
			time.sleep(1)
			chunk_end = min(chunk_start + chunk_size,file_size)
			chunk_data = parallel_downloads(chunk_start,chunk_end,url)
			with open(tmp_file,'ab') as tf:
				tf.write(chunk_data)
			chunk_start = chunk_end + 1
	except Exception as error:
		print "Error while downloading file",error


	#Move file to destination once finished downloading and remove temp directory	
	os.rename(tmp_file,final_file)
	print "Download finished\nFile is at",final_file	
	os.rmdir(temp_dir)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Too few arguments.Exiting"
		sys.exit()
	file_url = sys.argv[1]
	if len(sys.argv) > 2:
		destination = sys.argv[2]
	else:
		destination = None
	download_with_resume(file_url,destination)
