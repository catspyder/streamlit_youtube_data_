
import googleapiclient.discovery 
import googleapiclient.errors
import json
import pymongo 
import pandas as pd
# import pandas as pd
# from mysql import connector


class Youtube:
  
  channels={}
  playlists={}
  comments={}
  videos={}
  channelName=''
  # api_key = "AIzaSyCJiX5JoPW95K1-FfWmzN7jPN-JxxyOgeo"
  api_key = "AIzaSyABUcsP6P3gSV_cYZSku1t5CSO3qfa3QRg"
#   api_key="AIzaSyAN_z0QMyM7LsdAbSkFs7WJFxye4jK-lA4"


  
    
  def get_channel(self):
    
    raw_data=self.youtube.channels().list(part='contentDetails,snippet,statistics',id=self.channelId).execute()
    data=raw_data['items'][0]
    channel_data={}
    channel_data['channelName']=data['snippet']['title']
    self.channelName=data['snippet']['title']
    channel_data['subscriberCount']=data['statistics']['subscriberCount']
    channel_data['channelId']=data['id']
    channel_data['channelDescription']=data['snippet']['description']
    channel_data['viewCount']=data['statistics']['viewCount']
    channel_data['playlistId']=data['contentDetails']['relatedPlaylists']['uploads']
    # channel_data['videos']={}
    self.channels=channel_data


  def get_videos(self):
    self.channels['videos']={}

    video_ids=[]
    next_page_token=None
    while True:
    # Make the API request
      response = self.youtube.search().list(
          part="id",
          channelId=self.channelId,
          maxResults=50,  # Adjust as needed
          pageToken=next_page_token
      ).execute()

      # Collect video IDs from the API response
      for item in response["items"]:
         if item['id']['kind']=='youtube#video':

          video_ids.append(item["id"]['videoId'])

          # video_ids.append(item["id"]["videoId"])

      # Check if there are more pages of results
      next_page_token = response.get("nextPageToken")
      if not next_page_token:
          break


  # Output the retrieved video IDs
    for video_id in video_ids:
      video=self.youtube.videos().list(part='contentDetails,snippet,statistics',id=video_id).execute()['items'][0]
      videoData={}
      videoData['videoId']=video_id
      videoData['duration']= video['contentDetails']['duration']
      videoData['viewCount']=video['statistics']['viewCount'] 
      try:
        videoData['commentCount']=video['statistics']['commentCount']
      except KeyError:
        videoData['commentCount']=0
      videoData['favouriteCount']=video['statistics']['favoriteCount'] 
      videoData['likeCount']=video['statistics']['likeCount']
      videoData['videoName']= video['snippet']['title']
      videoData['videoDescription']= video['snippet']['description']
      try:
        videoData['tags']= video['snippet']['tags']
      except KeyError:
        videoData['tags'] =  []
      # print(video['snippet']) #debugging
      videoData['thumbnail']=video['snippet']['thumbnails']['default']['url']
      videoData['publishedAt']=video['snippet']['publishedAt']
      videoData['captionStatus']=video['contentDetails']['caption']
      next_page_token = None
      comments_dict = {}
      try:


          # Retrieve all comments for the video
        while True:
            # Make the API request
            response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50, 
                pageToken=next_page_token
            ).execute()

            # Collect comments and their information from the API response
            for item in response["items"]:
                comment_id = item["id"]
                comment = item["snippet"]["topLevelComment"]["snippet"]['textDisplay']
                author = comment["authorDisplayName"]
                published_at = comment["publishedAt"]
                comments_dict[comment_id] = {
                    'commentContent':comment,
                    'commentId':comment_id,
                  
                    "commentAuthor": author,
                    "published_at": published_at
                }

          
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
      except Exception:
        comments_dict={'no_comments':'disabled'}
          
      videoData['comments']=comments_dict 
      self.comments[video_id]=comments_dict
      self.channels['videos'][video_id]=videoData
      self.videos[video_id]= videoData
    
    
    
    
 
  def get_playlists(self):
    list_of_data=[]
    next_page_token = None
    while True:
      data=self.youtube.playlists().list(part='contentDetails,snippet,id',
                                            channelId=self.channelId,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
      list_of_data.append(data['items'])
      next_page_token = data.get('nextPageToken')
      if not next_page_token:
           break
    for j in range(len(list_of_data)):
      list_item=list_of_data[j]


      for i in range(len(list_item)):
        data=list_item[i]
        playlist_data={}
        playlist_data['playlistName']=data['snippet']['title']
        playlist_data['channelId']=data['snippet']['channelId']
        playlist_data['playlistId']=data['id']
        self.playlists[playlist_data['playlistName']]=playlist_data
    self.channels['playlists']=self.playlists
  def save_to_mongo(self):
      client = pymongo.MongoClient('mongodb+srv://josjoe1999:qDe18Qg3WTOLGLoh@mycluster.bfyyqll.mongodb.net/')
      db = client['Youtube']
      collection = db['channels']
      filter={'channelName':self.channelName}
      result = collection.replace_one(filter,self.channels,upsert=True)

      # collection=db['comments']
      # result = collection.insert_one(self.comments)
      # collection=db['videos']
      # result = collection.insert_one(self.videos)
      # collection=db['playlists']
      # result = collection.insert_one(self.playlists)
      client.close()
  def save_to_sql(self):
     dfChannels=pd.DataFrame.from_dict(ytt.channels[ytt.channelName],orient='index')
     dfPlaylists=pd.DataFrame.from_dict(ytt.playlists,orient='index')
     dfComments=pd.DataFrame.from_dict(ytt.playlists,orient='index')
     dfVideos=pd.DataFrame.from_dict(ytt.videos,orient='index')
     



  def __init__(self,channelId):
    self.channelId=channelId
    self.youtube=googleapiclient.discovery.build('youtube','v3',developerKey=self.api_key)
    self.get_channel()

    self.get_playlists()

    self.get_videos()
    # self.save_to_mongo()
    # self.load_to_pymongo
        

import streamlit as st 
ytt=Youtube(st.text_input('channelId'))
st.write(ytt.channels)
st.button('save to mongodb',on_click=ytt.save_to_mongo())
