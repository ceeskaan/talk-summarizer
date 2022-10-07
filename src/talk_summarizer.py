from argparse import ArgumentParser

import pytube

from nltk import sent_tokenize
from summarizer import Summarizer
from youtube_transcript_api import YouTubeTranscriptApi

from utils import download_video, get_word_timestamps, get_sentence_timestamps, timestamps_to_summary


parser = ArgumentParser(description='Generate audiovisual summary based on its transcription')
parser.add_argument('url', type=str, help = 'YouTube video url to be summarized')
parser.add_argument('--filename', type=str, help = 'Name of file to be saved', default='video')
parser.add_argument('--ratio', type=float, help = 'Length of summary', default=0.2)
args = parser.parse_args()


def talk_summarizer(url:str, save_as:str, ratio:float) -> None:
    """
    Produces a summary video for a given YouTube url
    
    Args:
        url {str}               -- YouTube url
        save_as {str}           -- Desired name/location of output .mp4 file 
        ratio {lst}             -- Length of summary as a percentage of total video
        
    
    Returns:
        None
    """
    
    # Download video
    print('Downloading video...')
    video = download_video(url, save_as)
    video_id = pytube.YouTube(url).video_id
    
    # 1. SPEECH-TO-TEXT
    response = YouTubeTranscriptApi.get_transcript(video_id)
    
    # 2. TEXT PROCESSING: Process transcript and get sentence timestamps
    transcript = ' '.join([res['text'].replace('\n', ' ') for res in response])
    word_timestamps = get_word_timestamps(response)
    sent_list = sent_tokenize(transcript)
    sentence_timestamps = get_sentence_timestamps(sent_list, word_timestamps)
    
    # 3. SUMMARIZATION: BERT extractive summarizer
    model = Summarizer()
    print("Summarizing...")
    summary = model(transcript, ratio=ratio)
    summary_sent_list = sent_tokenize(summary)
    print(f"Summary: {summary_sent_list}")
    
    # 4. CONTENT PROCESSING: 
    print("Processing video...")
    selected_clips = [sentence_timestamps[sent_list.index(summary_sent)] for summary_sent in summary_sent_list]
    timestamps_to_summary(video, save_as, selected_clips)
    
    return None
    
        
if __name__ == "__main__":
    talk_summarizer(args.url, args.filename, args.ratio)