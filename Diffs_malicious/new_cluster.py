import os
from urllib.request import urlopen
import re
import shutil
import pickle
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np


location_apis = '(getLatitude|getLongitude|getAddress)'
device_apis = '(getDeviceId|getSubscriberId|getSimSerialNumber|getLine1Number|sendTextMessage|getCurrentUser|getSimOperatorName|getSimCountryIso|getNetworkOperatorName|getNetworkType|getPhoneType)'
suspicious_permissions = '(SEND_SMS|READ_CONTACTS|WRITE_CONTACTS|CALL_PHONE|ADD_VOICEMAIL|READ_CALENDAR|WRITE_CALENDAR|ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|RECORD_AUDIO)'
touchEvent_apis = '(addFlags|getDisplayMetrics|getDefaultDisplay|heightPixels|widthPixels|dispatchTouchEvent|onClick)'
reflective_calls = '(class\.getMethod|class\.getDeclaredMethod|invoke|java\.lang\.reflect|getClass|getMethods|getDeclaredField)'
new_receiver = '(new( ){1,}BroadcastReceiver|extends( ){1,}BroadcastReceiver)'
new_service = '(new( ){1,}Service|extends( ){1,}Service)'
onCreate_apis = '(onCreate|run|exec|start)'
#getSystemService

# weight_dic = {}
# weight_dic["location"] = 20
# weight_dic["device_info"] = 20
# weight_dic["permission"] = 20
# weight_dic["receiver"] = 5
# weight_dic["service"] = 5
# weight_dic["long_file"] = 100
# weight_dic["touchEvent"] = 5
# weight_dic["onCreate"] = 2
# weight_dic["reflection"] = 5
weight_dic = {}
weight_dic["location"] = 1
weight_dic["device_info"] = 1
weight_dic["permission"] = 1
weight_dic["receiver"] = 1
weight_dic["service"] = 1
weight_dic["long_file"] = 1
weight_dic["touchEvent"] = 1
weight_dic["onCreate"] = 1
weight_dic["reflection"] = 1


def cluster():
	data_set = []
	commit_set = []
	for repo_name in next(os.walk('.'))[1]:
		if "." in repo_name:
			continue
		for file_name in os.listdir("./"+repo_name):
			file = open("./"+repo_name+"/"+file_name, "r")
			# owner = file_name.split(':')[0]
			# fork_name = file_name.split(':')[1]
			# hash_val = file_name.split(':')[2]
			file_content = file.read()
			file.close()
			content_list = file_content.split('\n')
			vector = [0,0,0,0,0,0,0,0,0]

			changed_lines = 0
			too_long = False
			contain_location_api = False
			contain_device_api = False
			contain_permission = False
			contain_receiver = False
			contain_service = False
			contain_touchEvent = False
			contain_onCreate = False
			contain_reflection = False

			for content_line in content_list:
				if content_line == '':
					continue
				# (notice) add + for non-commit code
				content_line = "+ " + content_line
				match = re.match('\+( )*//.*', content_line)
				if match:
					continue
				if content_line[0] == '+' or content_line[0] == '-':
					changed_lines += 1
				matchObj = re.match('\+.*( +|\.)'+location_apis+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[0] += weight_dic["location"]
				matchObj = re.match('\+.*( +|\.)'+device_apis+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[1] += weight_dic["device_info"]
				matchObj = re.match('\+.*( +|\.)'+reflective_calls+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[8] += weight_dic["reflection"]
				matchObj = re.match('\+.*( +|\.)'+touchEvent_apis+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[6] += weight_dic["touchEvent"]
				matchObj = re.match('\+.*android\.permission\.'+suspicious_permissions+'.*', content_line)
				if matchObj:
					vector[2] += weight_dic["permission"]
				matchObj = re.match('\+.*( +|\.)'+new_receiver+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[3] += weight_dic["receiver"]
				matchObj = re.match('\+.*( +|\.)'+new_service+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[4] += weight_dic["service"]
				matchObj = re.match('\+.*( +|\.)'+onCreate_apis+'( )*(\(|\{).*', content_line)
				if matchObj:
					vector[7] += weight_dic["onCreate"]

			if changed_lines > 5000:
				vector[5] = weight_dic["long_file"]
			# print(vector, "https://github.com/"+owner+"/"+fork_name+"/commit/"+hash_val)
			print(vector, file_name)
			data_set.append(vector)
			# commit_set.append("https://github.com/"+owner+"/"+fork_name+"/commit/"+hash_val)
			commit_set.append(file_name)

	data_set = np.array(data_set)
	np.save("./mvectors2.npy",data_set)
	with open("./mcommits2.pkl","wb") as f:
		pickle.dump(commit_set,f)

	kmeans = KMeans(n_clusters=15).fit(data_set)
	y_kmeans = kmeans.predict(data_set)
	res = {}
	for i in range(len(commit_set)):
		if y_kmeans[i] in res:
			res[y_kmeans[i]].append((commit_set[i], data_set[i]))
		else:
			res[y_kmeans[i]] = []
			res[y_kmeans[i]].append((commit_set[i], data_set[i]))

	for key in res:
		print(key)
		for commit_vec in res[key]:
			print(commit_vec[0], commit_vec[1])

def main():
	cluster()

main()
	