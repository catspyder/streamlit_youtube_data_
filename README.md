# streamlit_youtube_data_

The data is aquired by using google api for youtube. 
Different queries have to made for videos comments playlists and general channel data.
\n The data that is neccessary is extracted from the api response and then stored in dictionaries as key value pairs
all this data is then stored to mongodbsql using its community cloud sql. Then they are converted to dataFrames and saved to postgresql using asqlalchemy
