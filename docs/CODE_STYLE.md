# How we write code here

We want this project to be easy to read, even for someone who is learning Python.

## Our simple rules

1. Give every file one main job.
2. Give every function one small job.
3. Use names that explain what a thing does.
4. Add a short comment when a step might be confusing.
5. Avoid clever one-line tricks.
6. Keep passwords and tokens out of source code.
7. Write a test when you add an important rule.

## Example

Hard to understand:

```python
x = [p for p in posts if p.ok and p.url]
```

Easier to understand:

```python
ready_posts = []

for post in posts:
    if post.is_approved and post.video_url:
        ready_posts.append(post)
```

Both examples do the same kind of job. The second one is longer, but easier for a beginner to follow.

## Before changing a file

Ask yourself: "Can I explain what this file does in one sentence?"

If not, the file may be doing too many jobs. Split it into smaller pieces.
