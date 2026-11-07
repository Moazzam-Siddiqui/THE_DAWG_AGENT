# How the robot works

Think of the robot as a small video factory.

## The journey of one dog picture

```text
DOG PICTURE
    |
    v
POST QUEUE
"We want to make a video from this picture."
    |
    v
APPROVAL
"A person says this post is okay."
    |
    v
VIDEO MAKER
"Turn the picture into a 9:16 MP4."
    |
    v
VIDEO CHECKER
"Is the video there? Is it the right shape?"
    |
    v
CLOUDINARY
"Put the video online and give us its link."
    |
    v
SCHEDULE
"Wait until the chosen date and time."
    |
    v
INSTAGRAM
"Publish the Reel."
```

## What is a queue?

A queue is a waiting list.

Each post has a name (its ID) and a status. The status tells us what happened to it.

| Status | Meaning |
|---|---|
| draft | We have an idea, but nobody approved it |
| approved | A person said it is okay |
| rendered | The video file was made |
| uploaded | The video is online and has a link |
| scheduled | It is waiting for its publish time |
| published | Instagram says it was published |
| failed | Something went wrong too many times |

## What is an API?

An API is a set of doors that another program can use to talk to our robot. For example, the API can create a post or ask the robot to render a video.

## What is a worker?

The worker is the robot's clock watcher. It wakes up regularly, checks whether an approved post is due, and publishes it if publishing is enabled.

## What is Cloudinary?

Instagram needs to be able to reach the video on the internet. Cloudinary stores the video and gives us a web link. The robot gives that link to Instagram.

## What is a token?

A token is like a password that lets the robot use an account. Tokens must stay private. Put them in your local `.env` file or a secure hosting secret store. Never put them in a code file or GitHub.

## Why does approval exist?

A computer can make mistakes. Approval lets a person check the picture, caption, and video before anything is sent to Instagram.
