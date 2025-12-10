import os
import random
import re
import time
import whisper
import yt_dlp

class Downloader():
    def __init__(self, url="", folder_path="", filename=""):
        self.url = url
        self.folder_path = folder_path
        self.filename = filename

        self.title = ""
        self.duration = 0
        self.langs = []
        self.has_cc = False


    def _find_matching_lang_codes(self, preferred_short_codes):
        matches = []
        available = list(self.langs)
        for short in preferred_short_codes:
            # exact match first
            if short in available and short not in matches:
                matches.append(short)
                continue
            # then prefix match (e.g. pt-BR matches 'pt')
            for code in available:
                if code.startswith(short) and code not in matches:
                    matches.append(code)
        return matches


    def _download_with_retries(self, ydl, url, max_attempts=6, base_wait=2, max_wait=300):
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                ydl.download(url)
                return
            except Exception as e:
                txt = str(e)
                is_429 = ("429" in txt) or ("Too Many Requests" in txt) or ("rate limit" in txt.lower())
                m = re.search(r'Retry-After:\s*(\d+)', txt, re.IGNORECASE)

                if m: retry_after = int(m.group(1))
                else: retry_after = None

                if not is_429 or (attempt == max_attempts):
                    raise e
                
                if retry_after is not None:
                    wait = retry_after
                else:
                    wait = min(base_wait * (2 ** (attempt - 1)), max_wait)
                    wait = wait + random.uniform(0, 1.0)
                time.sleep(wait)

    def check_url(self):
        if self.url.startswith("http://") or self.url.startswith("https://"):
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(self.url, download=False)
                    self.title = info.get('title', 'Unknown Title')
                    self.title = self.title.replace("/", "_").replace("\\", "_")
                    self.duration = info.get('duration', 0)
                    self.subs = info.get('subtitles', {})
                    self.autos = info.get('automatic_captions', {})
                    self.langs = set(list(self.subs.keys()) + list(self.autos.keys()))
                    self.has_cc = bool(self.langs)
                    return True, "Valid URL: Information extracted successfully"
                except Exception:
                    return False, "Invalid URL: Unable to extract information"
        else:
            return False, "Invalid URL: It needs to start with http:// or https://"


    def download_video(self):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.folder_path, self.filename),
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self._download_with_retries(ydl, [self.url])


    def download_audio(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.folder_path, self.filename),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self._download_with_retries(ydl, [self.url])


    def transcribe_audio(self, exclude_cc=False):
        if self.has_cc and not exclude_cc:
            preferred_order = ['pt', 'en']
            selected_codes = self._find_matching_lang_codes(preferred_order)
            if not selected_codes: selected_codes = list(self.langs)
            manual = any(code in self.subs for code in selected_codes)
            auto = any(code in self.autos for code in selected_codes)
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': manual,
                'writeautomaticsub': auto,
                'subtitlesformat': 'vtt',
                'subtitleslangs': selected_codes,
                'outtmpl': os.path.join(self.folder_path, self.filename),
                'quiet': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._download_with_retries(ydl, [self.url])
        else:
            self.download_audio()

            model = whisper.load_model("base")
            result = model.transcribe(os.path.join(self.folder_path, self.filename + '.mp3'), fp16=False, language='pt' if 'pt' in self.langs else 'en')

            with open(os.path.join(self.folder_path, self.filename + ".txt"), "w", encoding="utf-8") as f:
                f.write(result['text'])
