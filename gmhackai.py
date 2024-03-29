
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np

from tqdm import tqdm
from time import sleep

from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

import gmaps

key = '#'
gmaps.configure(api_key=key)


# In[9]:

factor_price = False
factor_space = False
# indoor/outdoor - weather
# traffic condition


# ## Pulling Green P Parking Data

# In[3]:

print("Pulling Greeen P Parking data from City of Toronto ...")
sleep(0.5)
df = pd.read_json("greenPParking2015.json")
for i in tqdm(range(100)):
    sleep(0.01)
print("Data successfully collected from 206.130.170.39")
print("\n")

parks = df.carparks
lat = [float(p['lat']) for p in parks]
lng = [float(p['lng']) for p in parks]
price = [float(p['rate_half_hour']) for p in parks]

park_features = c = np.c_[(lat,lng)]

park_locations = park_features[:,:2]
park_markers = gmaps.marker_layer(park_locations)
fig_plocations = gmaps.figure()
fig_plocations.add_layer(park_markers)


# ## Green P Parking Spots

# In[4]:

fig_plocations


# ## Finding Clusters of Parking Locations

# In[10]:

park_features = c = np.c_[(lat,lng)]
if factor_price:
    park_features = c = np.c_[(lat,lng, price)]
if factor_space:
    capacity = [int(p['capacity']) for p in parks]

    num_parks = len(df.index)
    usage = np.random.rand(num_parks)
    availability = capacity * usage

    max_availability = max(availability)

    park_features = c = np.c_[(lat,lng, price, max_availability - availability)]
    
X1 = np.load('X1.npy')
X2 = np.load('X2.npy')
X3 = np.load('X3.npy')
X4 = np.load('X4.npy')

X1_hm = gmaps.heatmap_layer(X1)
X2_hm = gmaps.heatmap_layer(X2)
X3_hm = gmaps.heatmap_layer(X3)
X4_hm = gmaps.heatmap_layer(X4)
fig_hm = gmaps.figure()
fig_hm.add_layer(X1_hm)
fig_hm.add_layer(X2_hm)
fig_hm.add_layer(X3_hm)
fig_hm.add_layer(X4_hm)

X = np.vstack((X1, X2, X3, X4))
if factor_price:
    X = np.column_stack((X, np.zeros((len(X), 1))))
if factor_space:
    X = np.column_stack((X, np.zeros((len(X), 2))))
    
print("Identifying clusters based on user's historial parking data")
sleep(0.5)
kmeans = KMeans(n_clusters=4, random_state=0).fit(X)
Xmean = kmeans.cluster_centers_
for i in tqdm(range(100)):
    sleep(0.02)
print("successfully identified 4 clusters")
print("\n")

Xm = Xmean[:,:2]
Xm_sym = gmaps.symbol_layer(Xm, fill_color='black', scale=2)
fig_hm_cnt = gmaps.figure()
fig_hm_cnt.add_layer(X1_hm)
fig_hm_cnt.add_layer(X2_hm)
fig_hm_cnt.add_layer(X3_hm)
fig_hm_cnt.add_layer(X4_hm)
fig_hm_cnt.add_layer(Xm_sym)


# ## Clusters of Historical User Locations

# In[6]:

fig_hm_cnt


# ## Finding Optimum Parking Spots

# In[11]:

print("Fidnding the best parking spot for you ...")
nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(park_features)
distances, indices = nbrs.kneighbors(Xmean)
print("\n")

park_opt_id = indices.flatten()
park_opt = park_features[park_opt_id][:,:2]
opt_markers = gmaps.marker_layer(park_opt)

if factor_price:
    num_park_spots = 3
    fig_opt_p = gmaps.figure()
    fig_opt_p.add_layer(X1_hm)
    fig_opt_p.add_layer(X2_hm)
    fig_opt_p.add_layer(X3_hm)
    fig_opt_p.add_layer(X4_hm)
    fig_opt_p.add_layer(Xm_sym)
    fig_opt_p.add_layer(opt_markers)
else:
    num_park_spots = 4
    fig_opt_np = gmaps.figure()
    fig_opt_np.add_layer(X1_hm)
    fig_opt_np.add_layer(X2_hm)
    fig_opt_np.add_layer(X3_hm)
    fig_opt_np.add_layer(X4_hm)
    fig_opt_np.add_layer(Xm_sym)
    fig_opt_np.add_layer(opt_markers)

for i in range(num_park_spots):   
    print("Found a parking spot")
    sleep(0.5)
sleep(2)

print("\n")
print("All parking spots are identified")
print("\n")


# ## Optimum Parking Spots

# In[13]:

fig_opt_p


# In[12]:

fig_opt_np


# ## Notifying the User

# In[13]:

from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "#"
# Your Auth Token from twilio.com/console
auth_token  = "#"

client = Client(account_sid, auth_token)

cluster = "work"
cluster_num = park_opt_id[0]
location = parks[cluster_num]['address']
msg = "I found you parking near " + cluster + " at " + location

message = client.messages.create(
    to="6478715005",
    from_="+16479311112",
    body=msg)

print(message.sid)


# In[ ]:



