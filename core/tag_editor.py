from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
from mutagen.mp3 import MP3

class TagEditor:
    @staticmethod
    def load_tags(file_path):
        tags = {
            "title": "",
            "artist": "",
            "album": "",
            "genre": "",
            "bpm": "",
            "mood": "",
            "comment": "",
            "cover": None
        }
        try:
            audio = MP3(file_path, ID3=EasyID3)
            tags["title"] = audio.get("title", [""])[0]
            tags["artist"] = audio.get("artist", [""])[0]
            tags["album"] = audio.get("album", [""])[0]
            tags["genre"] = audio.get("genre", [""])[0]
            tags["bpm"] = audio.get("bpm", [""])[0]
            tags["mood"] = audio.get("mood", [""])[0]
            tags["comment"] = audio.get("comment", [""])[0]

            try:
                id3 = ID3(file_path)
                for tag in id3.values():
                    if tag.FrameID == "APIC":
                        tags["cover"] = tag.data
                        break
            except ID3NoHeaderError:
                pass
        except Exception:
            pass
        return tags

    @staticmethod
    def save_tags(file_path, tags):
        try:
            try:
                audio = MP3(file_path, ID3=EasyID3)
            except ID3NoHeaderError:
                audio = MP3(file_path)
                audio.add_tags(ID3=EasyID3)

            audio["title"] = tags.get("title", "")
            audio["artist"] = tags.get("artist", "")
            audio["album"] = tags.get("album", "")
            audio["genre"] = tags.get("genre", "")
            if tags.get("bpm"):
                audio["bpm"] = str(tags["bpm"])
            if tags.get("mood"):
                audio["mood"] = tags.get("mood", "")
            audio["comment"] = tags.get("comment", "")
            audio.save()

            if tags.get("cover"):
                try:
                    id3 = ID3(file_path)
                except ID3NoHeaderError:
                    id3 = ID3()
                id3.delall("APIC")
                id3.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=tags["cover"]
                ))
                id3.save(file_path)
        except Exception as e:
            print(f"Ошибка при сохранении тегов: {e}")
