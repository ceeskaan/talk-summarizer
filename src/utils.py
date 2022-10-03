import os

import pytube

from pytube.cli import on_progress
from moviepy.editor import VideoFileClip, concatenate_videoclips


def download_video(url:str, filename:str) -> str:
    """
    Download YouTube video by given url
    
    Args:
        url {str}        -- YouTube URL
        save_as {str}    -- Filename to be saved
        
    Returns:
        List of timestamps for every sentence
    """
    
    try: 
        yt = pytube.YouTube(url, on_progress_callback=on_progress) 
    except: 
        print("Connection Error") # To handle exception 
    video_path = yt.streams.filter(progressive=True, file_extension='mp4')\
                           .order_by('resolution').desc().first().download()
    
    # Rename path
    new_path = video_path.split('/')
    new_filename = filename + '.mp4'
    new_path[-1]= new_filename
    new_path='/'.join(new_path)
    os.rename(video_path, new_path)
        
    return new_path

def get_word_timestamps(response:list) -> list:
    """ 
    Fetches timestamps for every word from YouTube transcript API
    
    Args:
        response {list}          -- Youtube Transcript API response

    Returns:
        List of word timestamps
    """
   
    word_timestamps = []
    for res in response:
        for words in res['text'].split():
            word_timestamps.append([res['start'] , res['start'] + res['duration']])
    return word_timestamps
 
def get_sentence_timestamps(sent_list:list, word_timestamps:list) -> list:
    """
    Fetches timestamps for every sentence
    
    Args:
        tokenized {str}          -- List of sentences
        word_timestamps {str}    -- List of word timestamps
        
    Returns:
        List of timestamps for every sentence
    """
    
    sentence_timestamps = []
    idx = 0
    for sentence in sent_list:
        start = []
        end = []
        for word in sentence.split():
            start.append(word_timestamps[idx][0])
            end.append(word_timestamps[idx][1])
            idx += 1
        sentence_timestamps.append([start[0], end[-1]])
    return sentence_timestamps

def timestamps_to_summary(original:str, save_as:str, summary:list) -> None:
    """
    Fetches clips from video based on timestamps and concatenates them
    
    Args:
        original {str}          -- Name/location of original .mp4 video
        save_as {str}           -- Desired name/location of output .mp4 file 
        summary {lst}           -- List of selected sentence timestamps
        
    
    Returns:
        None
    """
    
    clip = VideoFileClip(original)
    outputs = [clip.subclip(i[0], i[1]) for i in summary]
    summary = concatenate_videoclips(outputs) 
    summary.write_videofile(save_as)
    
    clip.close()