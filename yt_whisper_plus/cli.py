import os
import whisper
from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE
import argparse
import warnings
import yt_dlp
from .utils import slugify, str2bool, write_srt, write_vtt
import tempfile
import concurrent.futures
import re

whisper_accepted_params = [
    "video",
    "model",
    "format",
    "output_dir",
    "format",
    "verbose",
    "task",
    "language",
    "break-lines",
]


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("video", nargs="+", type=str, help="video URLs to transcribe")
    parser.add_argument(
        "--video_type",
        default="video",
        choices=["video", "playlists"],
        help="name of the media type to use.",
    )
    parser.add_argument(
        "--title_model",
        default="slugify",
        choices=["yt_dlp", "slugify"],
        help="name of the title model to use",
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=whisper.available_models(),
        help="name of the Whisper model to use",
    )
    parser.add_argument(
        "--format",
        default="vtt",
        choices=["vtt", "srt"],
        help="the subtitle format to output",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default=".",
        help="directory to save the outputs",
    )
    parser.add_argument(
        "--verbose",
        type=str2bool,
        default=False,
        help="Whether to print out the progress and debug messages",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        choices=sorted(LANGUAGES.keys())
        + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]),
        help="language spoken in the audio, skip to perform language detection",
    )

    parser.add_argument(
        "--break-lines",
        type=int,
        default=0,
        help="Whether to break lines into a bottom-heavy pyramid shape if line length exceeds N characters. 0 disables line breaking.",
    )

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    subtitles_format: str = args.pop("format")
    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection."
        )
        args["language"] = "en"

    model = whisper.load_model(model_name)

    urls = args.pop("video")
    print("Getting audio...:" + str(urls))
    if args["video_type"] == "playlists":
        urls = get_playlist_urls(urls[0])

    audios = get_audio(urls)
    break_lines = args.pop("break_lines")
    title_model = args.pop("title_model")

    for title, audio_path in audios.items():
        warnings.filterwarnings("ignore")

        if title_model == "slugify":
            formatted_title = slugify(title)
        else:
            formatted_title = title

        output_filepath = os.path.join(
            output_dir, f"{formatted_title}.{subtitles_format}"
        )
        if os.path.exists(output_filepath):
            print(f"File {output_filepath} already exists. Skipping...")
            continue

        filtered_args = {k: v for k, v in args.items() if k in whisper_accepted_params}

        result = model.transcribe(audio_path, **filtered_args)
        warnings.filterwarnings("default")

        if subtitles_format == "vtt":
            vtt_path = os.path.join(output_dir, f"{formatted_title}.vtt")
            with open(vtt_path, "w", encoding="utf-8") as vtt:
                write_vtt(result["segments"], file=vtt, line_length=break_lines)

            print("Saved VTT to", os.path.abspath(vtt_path))
        else:
            srt_path = os.path.join(output_dir, f"{formatted_title}.srt")
            with open(srt_path, "w", encoding="utf-8") as srt:
                write_srt(result["segments"], file=srt, line_length=break_lines)

            print("Saved SRT to", os.path.abspath(srt_path))


def get_playlist_urls(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        print(f"Found playlist \"{result['title']}\"....")
        print(f"Found {len(result['entries'])} videos in playlist.")

        if "entries" in result:
            return [entry["url"] for entry in result["entries"]]
        else:
            return []


def sanitize_filename(title):
    replacements = {
        "<": "＜",
        ">": "＞",
        ":": "：",
        '"': "＂",
        "/": "／",
        "\\": "＼",
        "|": "｜",
        "?": "？",
        "*": "＊",
    }

    for half, full in replacements.items():
        title = title.replace(half, full)

    return title


def download_audio(url, temp_dir):
    ydl_opts = {
        "quiet": True,
        "verbose": False,
        "format": "bestaudio",
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "preferredcodec": "mp3",
                "preferredquality": "192",
                "key": "FFmpegExtractAudio",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        print(f"Downloaded video \"{result['title']}\". Generating subtitles...")
        formatted_title = sanitize_filename(f"{result['title']} [{result['id']}]")
        return formatted_title, os.path.join(temp_dir, f"{result['id']}.mp3")


def get_audio(urls):
    temp_dir = tempfile.gettempdir()

    paths = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(download_audio, url, temp_dir): url for url in urls
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, path = future.result()
                paths[title] = path
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")

    return paths


if __name__ == "__main__":
    main()
