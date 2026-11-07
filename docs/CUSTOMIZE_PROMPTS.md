# Customize Prompts, Post Types, and Audio 🎨🔊

This guide is for anyone who wants the robot to make a different kind of post.

You do **not** need to understand Python to change the creative instructions. You can change the words in the prompt files and choose different post and audio styles.

## First, understand the three choices

A Reel has three separate creative parts:

1. **Post type:** What kind of video are we making?
2. **Image prompt:** What should the dog and the scene look like?
3. **Audio type:** What should people hear?

These choices work together, but they are not the same thing.

For example:

- Post type: wholesome dog moment
- Image prompt: a golden retriever waiting at the door in warm evening light
- Audio type: gentle, licensed background music

That makes a very different Reel from a funny dog meme with a dramatic sound effect.

---

## 1. Where do I change the prompts?

Open this folder in the project:

`config/`

The main creative instruction file is:

`config/content_brief.md`

Open it with any text editor. Change the instructions, save the file, and keep a copy of the original if you want to go back.

**Important:** The current project has a written content brief, but the automatic AI prompt-generation system is not connected yet. Editing this file changes the instructions that the future generator should follow; it does not magically generate new pictures by itself today.

## 2. Choose a post type

A post type tells the content generator what kind of story to create.

Here are some examples you can use or change:

| Post type | What it means | Example idea |
|---|---|---|
| Dog comedy | A funny situation | A pug steals a chair |
| POV | A scene shown from someone's point of view | POV: your dog heard the snack packet |
| Meme | A familiar internet-style joke | Dog looking guilty beside a broken pillow |
| Wholesome | Sweet, warm, happy moments | Puppy greeting its owner |
| Cinematic | Movie-like visuals | Dog walking through rain in dramatic light |
| Action | Energetic adventure | Corgi running through a field |
| Educational | A simple dog fact or tip | Why dogs tilt their heads |
| Reaction | A dog reacting to something | Dog sees a cucumber |
| Roast / satire | A playful joke about an idea or public topic | A dog reacts to an absurdly expensive computer |
| Story | A tiny beginning, middle, and ending | Dog guards a toy, then falls asleep |

You can invent your own post type. For example: `medieval_dog_adventure`, `office_dog`, or `detective_dog`.

### Example: change the post type

Suppose you want cinematic dog videos instead of memes.

Write an instruction like this in your creative brief:

```text
POST TYPE: CINEMATIC DOG SHORT

Make a tiny movie scene starring a dog.
Use dramatic but believable lighting.
Give the dog a clear action and emotion.
Use interesting camera angles and a detailed background.
Do not add meme text or random props.
Every video should feel like a different movie scene.
```

If you want a mixture, tell the generator how often to use each type:

```text
POST TYPE MIX:
- 40% dog comedy
- 25% POV
- 15% wholesome
- 10% cinematic
- 10% reaction
```

The percentages should add up to 100%.

---

## 3. Write better image prompts

An image prompt tells the image generator what to draw.

A useful prompt answers these questions:

- **Dog:** What breed, size, age, and coat?
- **Action:** What is the dog doing?
- **Place:** Where is the dog?
- **Mood:** Funny, cute, dramatic, mysterious, or something else?
- **Camera:** Close-up, wide shot, low angle, or eye-level?
- **Light:** Morning sun, studio light, neon, or soft indoor light?
- **Shape:** Vertical 9:16 for a Reel.
- **Things to avoid:** Extra legs, strange paws, text errors, watermarks, or duplicate dogs.

### Weak prompt

```text
Make a funny dog.
```

### Better prompt

```text
Create a photorealistic vertical 9:16 image of a small black pug
sitting proudly in an oversized office chair. The pug is staring
directly at the camera as if it owns the office. A tiny empty
coffee cup sits on the desk. Warm office lighting, realistic fur,
natural dog anatomy, eye-level camera, clean background.

Do not add words, logos, watermarks, extra legs, or extra dogs.
```

### Reusable image prompt template

Copy this and fill in the blanks:

```text
Create a [visual style] vertical 9:16 image.

MAIN CHARACTER:
A [breed / kind of dog] with [fur colour and special features].

ACTION:
The dog is [one clear action].

LOCATION:
The scene takes place in [place and background details].

MOOD:
The feeling should be [funny / cute / dramatic / mysterious].

CAMERA:
Use a [close-up / wide shot / low angle / eye-level] camera view.

LIGHTING:
Use [lighting description].

QUALITY:
Detailed fur, natural dog anatomy, realistic paws, clear subject,
good composition, and enough room around the dog.

AVOID:
No unwanted text, watermark, logo, extra limbs, distorted paws,
or accidental duplicate animals.
```

Make one main action the centre of the picture. Too many actions in one prompt can confuse an image generator.

---

## 4. Choose an audio type

Audio is a separate choice from the image and post type.

| Audio type | What people hear | Example |
|---|---|---|
| Silent | No sound | A clean visual joke |
| Supplied account sound | An audio file you provide | Your saved “What da dog doin” sound |
| Voiceover | A person or generated voice speaking | A narrator tells the joke |
| Sound effects | Small sounds that match the action | Footsteps, bark, door creak |
| Ambient | Background sounds from a place | Rain, birds, street noise |
| Licensed music | Music you have permission to use | A track licensed for social posts |
| Original audio | Audio you created yourself | Your own recording |

### Example: use a supplied sound

Put the audio file in a folder such as:

`assets/audio/`

Then set its path in the post JSON:

```json
{
  "audio_path": "assets/audio/what-da-dog-doin.mp3"
}
```

The file must actually exist at that location.

### Example: make a silent Reel

Use:

```json
{
  "audio_path": null
}
```

### Example: use a voiceover or sound effect

Put the audio file in `assets/audio/` and set `audio_path` to its file path, just like the supplied sound example.

**Audio file note:** FFmpeg supports many audio formats, but MP3 or WAV is a sensible starting choice. The current renderer uses one audio file for the video. It does not yet mix a voiceover, music, and sound effects into separate tracks automatically.

Only use audio you own, created yourself, or have permission to use. A sound being available on the internet does not automatically mean it is free to reuse.

---

## 5. Change the caption style

The caption is the text shown with the Reel. It is not the same as words drawn inside the image.

You can ask for different caption styles:

**Funny:**
```text
Write one short joke about what the dog is doing.
```

**Wholesome:**
```text
Write a warm, friendly caption. Keep it simple.
```

**Cinematic:**
```text
Write a short movie-style line. Do not explain the whole scene.
```

**Educational:**
```text
Write one accurate dog fact in simple language.
Do not invent scientific facts.
```

You can also set rules:

- Maximum caption length.
- Whether emojis are allowed.
- Whether hashtags are included.
- Whether the caption asks a question.
- Whether the tone is funny, friendly, serious, or dramatic.

---

## 6. Complete example: make a wholesome Reel

Here is one complete creative brief you can copy and edit:

```text
POST TYPE:
Wholesome dog moment.

IMAGE:
A small golden retriever puppy sitting beside a window.
Soft morning sunlight falls on its fur.
The puppy looks curious and happy.
Photorealistic, vertical 9:16, natural dog anatomy.

VIDEO:
Make a gentle 9-second vertical video from the image.
Use a slow camera movement.
Do not add flashing effects or fast cuts.

AUDIO:
Use a gentle audio file supplied by the account owner.
If no audio file is supplied, make the video silent.
Do not choose random music.

CAPTION:
Write one warm sentence.
Use no more than three hashtags.

SAFETY:
Do not add logos, watermarks, fake claims, or unwanted text.
Ask for human approval before publishing.
```

## 7. Complete example: make a funny meme Reel

```text
POST TYPE:
Funny dog meme.

IMAGE:
A sleepy bulldog sitting at a desk with a tiny laptop.
The bulldog looks extremely serious but is clearly falling asleep.
Photorealistic fur, funny expression, vertical 9:16.

VIDEO:
Make a 7-second video.
Use a slow zoom toward the dog's sleepy face.

AUDIO:
Use the account's supplied funny sound.
If it is missing, leave the Reel silent.

CAPTION:
Write one short joke about the dog looking busy.

SAFETY:
No fake logos, no watermarks, no extra limbs.
Human approval is required before publishing.
```

---

## 8. What can I change right now, and what needs more code?

This is important. We should not pretend a setting works if the robot has not been taught to use it yet.

| Customization | Current support |
|---|---|
| Edit the written creative brief | Yes |
| Change a post's caption | Yes, in its post JSON |
| Select a local audio file | Yes, through `audio_path` |
| Make a silent video | Yes, set `audio_path` to null |
| Change video length between 6 and 12 seconds | Yes |
| Change the post type through an automatic menu | Not built yet |
| Automatically write image prompts with AI | Not connected yet |
| Automatically generate new images | Not connected yet |
| Mix several audio tracks and add timed sound effects | Not built yet |
| Automatically choose music from a licensed music library | Not built yet |

The goal is to turn these choices into simple settings later, so someone can choose a post type and audio type without editing Python code.

## 9. A few rules for good results

1. Describe one clear idea per Reel.
2. Keep the dog as the main subject.
3. Change the breed, location, action, camera angle, and lighting between posts.
4. Do not reuse the same prompt with only one word changed.
5. Make sure audio matches the joke or mood.
6. Watch the finished video before approving it.
7. Keep publishing switched off until the account and video have been checked.

**The simple rule:** Change the post type to change the kind of story. Change the image prompt to change what the picture looks like. Change the audio type to change what people hear.
