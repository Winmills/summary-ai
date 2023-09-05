import unittest
from unittest.mock import patch
from ..transcript import get_youtube_transcripts  

def test_youtube_links():
    random_texts = [
        'https://www.youtube.com/shorts/FUVDVAtoRAQ',
        'https://www.youtube.com/watch?v=abcd123456 hello',
        'https://youtu.be/xyz987654 yo',
        'https://www.youtube.com/embed/ouM8z-4Uw4A hi',
        'https://www.youtube.com/watch?v=wxyz123456&t=30s 123',
        'https://www.youtube.com/watch?v=G_IQwt9ceN8&themeRefresh=1 hii',
        'https://www.youtube.com/watch?v=G_IQwt9ceN8&themeRefresh=1 uhhhu',
        'https://m.youtube.com/watch?v=6MFMju-rdUQ 23324',
        'youtube.com whatever',
        'http://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index',
        'http://www.youtube.com/user/IngridMichaelsonVEVO#p/a/u/1/QdK8U-VIH_o',
        '   http://www.youtube.com/v/0zM3nApSvMg?fs=1&amp;hl=en_US&amp;rel=0',
        'http://www.youtube.com/watch?v=0zM3nApSvMg#t=0m10s',
        '   http://www.youtube.com/embed/0zM3nApSvMg?rel=0',
        'http://www.youtube.com/watch?v=0zM3nApSvMg',
        '   http://youtu.be/0zM3nApSvMg'
    ]

    # print('Current Date: 2023-09-02')
    # results = [get_youtube_video_id(text) for text in random_texts]
    # for result in results:
    #     print(result)
    # print('----')

class TestGetYoutubeTranscripts(unittest.TestCase):

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_success(self, mock_initialize_youtube_api):
        # Mock the YouTube API response for successful transcript retrieval
        mock_api_instance = mock_initialize_youtube_api.return_value
        mock_api_instance.captions.return_value().list.return_value.execute.return_value = {
            'items': [{'id': 'caption_id'}]
        }

        # Provide a valid video ID
        video_ids = ['valid_video_id']
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the transcripts were retrieved successfully
        self.assertEqual(len(transcripts), 1)
        self.assertIn('valid_video_id', transcripts)
        self.assertTrue(transcripts['valid_video_id'].startswith('<tt'))

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_no_captions(self, mock_initialize_youtube_api):
        # Mock the YouTube API response for a video with no available captions
        mock_api_instance = mock_initialize_youtube_api.return_value
        mock_api_instance.captions.return_value().list.return_value.execute.return_value = {'items': []}

        # Provide a valid video ID
        video_ids = ['valid_video_id_without_captions']
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the function handles no captions gracefully
        self.assertEqual(len(transcripts), 1)
        self.assertIn('valid_video_id_without_captions', transcripts)
        self.assertEqual(transcripts['valid_video_id_without_captions'], 'No captions available for this video.')

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_error_handling(self, mock_initialize_youtube_api):
        # Mock the YouTube API to raise an exception when requesting transcripts
        mock_api_instance = mock_initialize_youtube_api.return_value
        mock_api_instance.captions.return_value().list.side_effect = Exception("API error")

        # Provide a valid video ID
        video_ids = ['valid_video_id_with_error']
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the function handles errors gracefully
        self.assertEqual(len(transcripts), 1)
        self.assertIn('valid_video_id_with_error', transcripts)
        self.assertTrue(transcripts['valid_video_id_with_error'].startswith('Error:'))

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_multiple_videos(self, mock_initialize_youtube_api):
        # Mock the YouTube API to return transcripts for multiple videos
        mock_api_instance = mock_initialize_youtube_api.return_value
        mock_api_instance.captions.return_value().list.return_value.execute.return_value = {
            'items': [{'id': 'caption_id_1'}, {'id': 'caption_id_2'}]
        }

        # Provide multiple valid video IDs
        video_ids = ['video_id_1', 'video_id_2']
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the function retrieves transcripts for all provided videos
        self.assertEqual(len(transcripts), 2)
        self.assertIn('video_id_1', transcripts)
        self.assertIn('video_id_2', transcripts)

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_empty_video_ids(self, mock_initialize_youtube_api):
        # Provide an empty list of video IDs
        video_ids = []
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the function handles empty video IDs gracefully
        self.assertEqual(len(transcripts), 0)

    @patch('your_script.initialize_youtube_api')
    def test_get_youtube_transcripts_invalid_api_key(self, mock_initialize_youtube_api):
        # Mock the YouTube API to raise an exception for invalid API key
        mock_api_instance = mock_initialize_youtube_api.return_value
        mock_api_instance.captions.return_value().list.side_effect = Exception("Invalid API key")

        # Provide a valid video ID
        video_ids = ['valid_video_id_with_invalid_api_key']
        transcripts = get_youtube_transcripts(video_ids)

        # Assert that the function handles invalid API keys gracefully
        self.assertEqual(len(transcripts), 1)
        self.assertIn('valid_video_id_with_invalid_api_key', transcripts)
        self.assertTrue(transcripts['valid_video_id_with_invalid_api_key'].startswith('Error:'))

if __name__ == '__main__':
    unittest.main()
