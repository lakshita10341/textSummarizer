from transformers import pipeline
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

def get_summary(text):
    # Check if the text is long enough to summarize
    if len(text.split()) < 200:
        return "The text is too short to generate a meaningful summary."
    
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split the text into chunks if it's too long
    max_chunk_length = 1024  # Maximum length the model can handle
    chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=400, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    return " ".join(summaries)

def get_transcript(link):
    video_id = link.split("v=")
    if len(video_id)>1:
        videoId = video_id[1]
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)
            
            # Try to get manual transcript first
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
                # If no manual transcript, get the first available transcript
            transcript = next(iter(transcript_list))
            
            # If the transcript is not in English, translate it
        if transcript.language_code != 'en':
            transcript = transcript.translate('en')
        full_transcript = " ".join(part['text'] for part in transcript.fetch())
        return full_transcript
    else:
        return 0
    
def main():
    st.title("YouTube Video Summarizer App")
    link = st.text_area("Enter the YouTube video link to summarize", height=100)
    if st.button('Start'):
        output = st.empty()
        output.text('Getting transcript...')
        text = get_transcript(link)
        if text.startswith("Error") or text == "Invalid YouTube URL":
            output.text(text)
        else:
            output.text('Generating summary...')
            try:
                summary = get_summary(text)
                output.text(summary)
            except Exception as e:
                output.text(f"An error occurred while generating the summary: {str(e)}")

if __name__ == "__main__":
    main()
