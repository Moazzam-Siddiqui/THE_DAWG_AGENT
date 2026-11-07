# Customization boundaries

THE DAWG AGENT is distributed under a restrictive personal, non-commercial licence. Recipients may customize only the supported choices for:

1. Image-generation type/provider/model.
2. Publishing type/provider/platform.
3. Asset type/source/format.

Changing prompts, captions, roast logic, workflows, source code, scheduling logic, approval logic, or other application behavior is not permitted for recipients under the licence. The owner may change these project internals.

The current local agent does not call ChatGPT or another image-generation API. ChatGPT remains the campaign's image generator; generated images are handed to the local agent through the Google Drive for desktop synced incoming folder.

The current caption is a configured default, not an AI-generated roast. The audio file is supplied by the owner and selected through `AUDIO_SOURCE_PATH`. The application does not provide a prompt editor or audio catalogue.
