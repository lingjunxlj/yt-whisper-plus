# Automatic YouTube subtitle generation

Base on [yt-whisper](https://github.com/m1guelpf/yt-whisper)

This repository uses `yt-dlp` and [OpenAI's Whisper](https://github.com/openai/whisper) to generate subtitle files for any youtube video.

## Installation

Please install whisper first.

    pip install git+https://github.com/openai/whisper.git 

To get started, you'll need Python 3.7 or newer. Install the binary by running the following command:

    pip install git+https://github.com/lingjunxlj/yt-whisper-plus

You'll also need to install [`ffmpeg`](https://ffmpeg.org/), which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg
```

## Usage

### Basic conditions

The following command will generate a VTT file from the specified YouTube video

    yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

The following command will generate a VTT file list from the specified YouTube playlist.

    yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --video_type playlists

The default setting (which selects the `small` model) works well for transcribing English. You can optionally use a bigger model for better results (especially with other languages). The available models are `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large`.

    yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --model medium

The following command specifies the return format of the file name, [yt_dlp] returns the original format of the video, and [slugify] returns the format after slugify. Note: The original format may contain special characters, which can cause file generation to fail.

    yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --title_model slugify

Adding `--task translate` will translate the subtitles into English:

    yt_whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --task translate

Run the following to view all available options:

    yt_whisper --help



## License

This script is open-source and licensed under the MIT License. For more details, check the [LICENSE](LICENSE) file.
