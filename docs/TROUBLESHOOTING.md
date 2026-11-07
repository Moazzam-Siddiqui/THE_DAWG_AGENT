# Something is not working?

Here are common problems and what they mean.

## "python is not recognized"

Python may not be installed, or Windows may not know where it is. Install Python 3.11+ and reopen the terminal.

## "ffmpeg was not found"

Install FFmpeg. Then close and reopen the terminal and run:

```bash
ffmpeg -version
```

## "No such file or directory"

The picture path is wrong. Check:
- Is the picture inside `assets/inbox/`?
- Does the file name match exactly?
- Did you spell the path correctly in the JSON file?

## "Post already exists"

Every post needs a unique ID. Change the `id` in your JSON file.

## "Post must be approved"

The robot will not move a post forward until it has approval. This is a safety rule.

## The video has no sound

The video maker does not invent sound. Give it an audio file using `audio_path`, or leave it as null for a silent video.

Only use audio you have permission to use.

## Instagram publishing does not work

Check these things:
1. Is `PUBLISH_ENABLED=true` set intentionally?
2. Is the Instagram account a professional account?
3. Is it connected to a Facebook Page?
4. Are the Meta permissions correct?
5. Is the access token still valid?
6. Can Instagram access the Cloudinary video URL?

Do not paste your access token into a GitHub issue or chat.

## Still stuck?

Read the error message from the terminal. It usually tells you which step failed. Share the error text, but remove passwords and tokens first.
