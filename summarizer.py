import os 

import tiktoken
import spacy
import openai
from transcript import YoutubeAPI

class SummarizerAI:

    def __init__(self) -> None:
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        # Load the spaCy English model
        self.nlp = spacy.load("en_core_web_sm")
        # Initialize the OpenAI API client
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def text_to_chunks_with_summaries(self,text, max_chunk_tokens=16000):
        # Initialize a list to store the text chunks and their summaries
        chunk_summaries = []

        # Tokenize the input text into sentences
        doc = self.nlp(text)

        current_chunk = ""
        current_chunk_tokens = 0

        for sentence in doc.sents:
            sentence_tokens = len(self.encoding.encode(sentence.text))

            # If adding this sentence to the current chunk doesn't exceed the max_chunk_tokens
            if current_chunk_tokens + sentence_tokens <= max_chunk_tokens:
                if current_chunk:
                    current_chunk += " "  # Add a space between sentences
                current_chunk += sentence.text
                current_chunk_tokens += sentence_tokens
            else:
                # If adding this sentence would exceed the max_chunk_tokens, start a new chunk
                # Generate a summary for the current chunk
                summary = self.generate_summary(current_chunk)

                chunk_summaries.append({
                    'chunk': current_chunk,
                    'summary': summary
                })

                current_chunk = sentence.text
                current_chunk_tokens = sentence_tokens

        # Add the last chunk and generate its summary
        if current_chunk:
            summary = self.generate_summary(current_chunk)

            chunk_summaries.append({
                'chunk': current_chunk,
                'summary': summary
            })

        return chunk_summaries

    def generate_summary(self,chunk):
        conversation = [
            {"role": "system", "content": "You are a helpful assistant that summarizes text. Break down the content into groups by main points and give me a explaination of the main points. Teach me on the main points using the content and some of your own knowledge"},
            {"role": "user", "content": chunk}
        ]

        # Request a summary from GPT-3 using the conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",  # Use the gpt-3.5-turbo engine
            messages=conversation,
        )
        return response['choices'][0]['message']['content']
    def text_to_summary(self,text,max_token=16000):

        chuck_summaries = self.text_to_chunks_with_summaries(text,max_chunk_tokens=max_token)
        full_summary = []
        for summary in chuck_summaries:
            full_summary.append(summary['summary'])
        
        return "".join(full_summary)
if __name__ == "__main__":
    youtube = YoutubeAPI()
    text = youtube.get_transcript_as_text("https://www.youtube.com/watch?v=kBbv2_9vcC0&ab_channel=MatthewBerman")
    summaryAI = SummarizerAI()
    summary = summaryAI.text_to_chunks_with_summaries(text)

    for chunk_summary in summary:
        print("Chunk:")
        print(chunk_summary['chunk'])
        print("Summary:")
        print(chunk_summary['summary'])
        print()  # Add a separator between chunks