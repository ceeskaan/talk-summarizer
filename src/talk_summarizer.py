from argparse import ArgumentParser

import pytube

from nltk import sent_tokenize
from summarizer import Summarizer
from youtube_transcript_api import YouTubeTranscriptApi

from utils import download_video, get_word_timestamps, get_sentence_timestamps, timestamps_to_summary


parser = ArgumentParser(description='Generate audiovisual summary based on its transcription')
parser.add_argument('url', type=str, help = 'YouTube video url to be summarized')
parser.add_argument('filename', type=str, help = 'Name of file to be saved')
parser.add_argument('n_clips', type=int, help = 'Length of summary as a percentage of total video')
args = parser.parse_args()


def talk_summarizer(url, save_as='video', n_clips=5):
    
    # Download video
    print('Downloading video...')
    download_video(url, save_as)
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
    summary = model(transcript, num_sentences=n_clips)
    summary_sent_list = sent_tokenize(summary)
    
    # 4. CONTENT PROCESSING: 
    print("Processing video...")
    selected_clips = [sentence_timestamps[sent_list.index(summary_sent)] for summary_sent in summary_sent_list]
    timestamps_to_summary(f'{args.name}.mp4', f'{args.name}_summary.mp4', selected_clips)
    
    return None
    
        
if __name__ == "__main__":
    talk_summarizer(args.url, args.filename, args.n_clips)