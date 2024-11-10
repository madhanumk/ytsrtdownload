from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi
from django.http import JsonResponse
from urllib.parse import urlparse, parse_qs
from datetime import timedelta
from django.core.files.base import ContentFile
from .models import Youtube_Video
import yt_dlp


# Create your views here.


def index(request):
    id = "AJtDXIazrMo"
    srt = YouTubeTranscriptApi.list_transcripts(id)
    print(srt)

    return render(request, 'index.html',)


def get_video_title(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,  # Suppress output except for errors
        'force_generic_extractor': True,  # Force the generic extractor for reliability
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict.get('title', None)
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import timedelta
from django.http import JsonResponse
from django.core.files.base import ContentFile
from urllib.parse import urlparse, parse_qs
from .models import Youtube_Video

def get_video_title(video_id):
    import yt_dlp

    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict.get('title', None)



def format_srt_time(seconds):
    """Converts time in seconds to SRT timestamp format HH:MM:SS,MMM."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)

    # Return time in the SRT format: HH:MM:SS,MMM
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def ajax_view(request):
    if request.method == 'POST':
        input_data = request.POST.get('inputData')
        parsed_url = urlparse(input_data)
        query_params = parse_qs(parsed_url.query)

        # Get the 'v' parameter value
        video_id = query_params.get('v', [None])[0]
        print(video_id)

        try:
            # Fetch the transcript from YouTube
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

            # Sort the transcript to ensure subtitles are in order
            transcript_data.sort(key=lambda x: x['start'])

            # Convert transcript data to SRT format
            srt_content = ""
            for i, entry in enumerate(transcript_data):
                start_time = format_srt_time(entry['start'])
                end_time = format_srt_time(entry['start'] + entry['duration'])

                srt_content += f"{i + 1}\n"
                srt_content += f"{start_time} --> {end_time}\n"
                srt_content += f"{entry['text']}\n\n"

            # Create the Youtube_Video instance
            title = get_video_title(video_id)
            youtube_video = Youtube_Video(
                video_id=video_id,
                video_name=title,
                data=transcript_data  # Store original data as JSON
            )

            # Save the SRT content as a file
            srt_filename = f"{video_id}.srt"
            youtube_video.srt.save(srt_filename, ContentFile(srt_content), save=True)

            # Save the model instance
            youtube_video.save()
            print("Transcript saved successfully.")

            # Construct download URL
            srt_url = youtube_video.srt.url  # URL of the saved SRT file

            return JsonResponse({
                'status_code': 200,
                'message': 'Transcript saved successfully!',
                'video_name': title,
                'srt_url': srt_url
            })

        except Exception as e:
            print(f"An error occurred: {e}")

        return JsonResponse({'status_code': 200, 'message': 'Data received successfully!'})
    
    return JsonResponse({'status_code': 400, 'message': 'Invalid request'}, status=400)
    