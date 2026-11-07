# THE DAWG AGENT 🐶

**A simple robot that helps make dog videos and prepare them for Instagram.**

Imagine you have a little helper:
1. You give it a dog picture.
2. It turns that picture into a short vertical video.
3. It checks that the video is okay.
4. It sends the video to Cloudinary, which gives us a link.
5. It can publish the video to Instagram when we turn that feature on.

That is what this project is for.

> **Important:** The robot is not running on the internet yet. This repository contains its code. Publishing is OFF by default, so it cannot accidentally post anything.

## Start here

If you are new to this project, read these in order:

1. [Start here: run the project](docs/START_HERE.md)
2. [How the robot works](docs/HOW_IT_WORKS.md)
3. [How to add a dog post](docs/ADD_A_POST.md)
4. [What each folder does](docs/PROJECT_MAP.md)
5. [Fix common problems](docs/TROUBLESHOOTING.md)

## What can it do today?

| Part | What it does |
|---|---|
| Post queue | Remembers which dog posts we want to make |
| Video maker | Turns one picture into a 9:16 MP4 video |
| Video checker | Checks that the video was created correctly |
| Cloudinary | Uploads the video and gives us a public link |
| Instagram connector | Talks to Instagram's official publishing API |
| Scheduler | Looks for posts that are ready to publish |
| API | Lets another program control the robot |

## What does it need?

- Python 3.11 or newer
- FFmpeg (a tool that makes videos)
- A Cloudinary account and upload preset
- Instagram professional account + Meta API access, only when we are ready to publish

## Safety rules

- Instagram publishing starts **OFF**.
- A post must be approved before it can move forward.
- The default limit is 3 posts per day.
- The default gap between posts is 3 hours.
- Posts are allowed only between 7 AM and 10 PM India time.
- Never put passwords or access tokens in GitHub.

## Project status

This is an early version. The code has been added, but it still needs to be run and tested in a real environment. It is not deployed and it does not publish by itself yet.
