# Generate song

Endpoint  
POST `/v1/song/generate`

Description  
Generate song based on the input by the user.

## Authorization
- Scheme: BearerAuth
- Type: HTTP (bearer)
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "lyrics": "string",
  "model": "string",
  "n": 0,
  "prompt": "string",
  "reference_id": "string",
  "vocal_id": "string",
  "melody_id": "string",
  "stream": true
}
```

### Field details
- lyrics (string)
  - Required: Yes when using lyrics-based generation
  - Max length: 3000 characters
- model (string)
  - Valid values: `auto`, `mureka-6`, `mureka-7.5`, `mureka-o1`
  - Notes:
    - `auto` selects the latest regular model (excluding `mureka-o1`)
    - Fine-tuned models are supported; when using a fine-tuned model, only `prompt` or `reference_id` control options are available
- n (integer)
  - Default: 2
  - Max: 3
  - How many songs to generate for each request (billing scales with n)
- prompt (string)
  - Max length: 1024 characters
  - Controls music generation via textual prompt
  - When `prompt` is provided, do not include other control options (`reference_id`, `vocal_id`, `melody_id`)
- reference_id (string)
  - Controls generation by referencing a music file uploaded via Files Upload API (for reference purpose)
  - When `reference_id` is provided, do not include `prompt` or `melody_id`
- vocal_id (string)
  - Controls generation using a voice uploaded via Files Upload API (for vocal purpose)
  - When `vocal_id` is provided, do not include `prompt` or `melody_id`
- melody_id (string)
  - Controls generation using a melody uploaded via Files Upload API (for melody purpose)
  - When `melody_id` is provided, do not include `prompt`, `reference_id`, or `vocal_id`
- stream (boolean)
  - If true, the task will include a streaming phase
  - During streaming, you can obtain `stream_url` to play the generated song while generation progresses
  - Not supported when `model` is `mureka-o1`

## Responses
Status: `200 OK`  
Description: Asynchronous task information for generating songs. Use `song/query/{task_id}` to poll for task information.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "created_at": 0,
  "finished_at": 0,
  "model": "string",
  "status": "string",
  "failed_reason": "string",
  "choices": [
    {
      "index": 0,
      "id": "string",
      "url": "string",
      "flac_url": "string",
      "stream_url": "string",
      "duration": 0,
      "lyrics_sections": [
        {
          "section_type": "string",
          "start": 0,
          "end": 0,
          "lines": [
            {
              "start": 0,
              "end": 0,
              "text": "string",
              "words": [
                {
                  "start": 0,
                  "end": 0,
                  "text": "string"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Status values
- `preparing`
- `queued`
- `running`
- `streaming`
- `succeeded`
- `failed`
- `timeouted`
- `cancelled`

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/song/generate \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "[Verse]\nIn the stormy night, I wander alone\nLost in the rain, feeling like I have been thrown\nMemories of you, they flash before my eyes\nHoping for a moment, just to find some bliss",
    "model": "auto",
    "prompt": "r&b, slow, passionate, male vocal",
    "n": 2,
    "stream": false
  }'
```

## Notes & Constraints
- Provide either `prompt` or one of (`reference_id`, `vocal_id`, `melody_id`)—do not combine them.
- When using `auto`, it routes to the latest regular model (not `mureka-o1`).
- Streaming mode (`stream: true`) is unavailable for `mureka-o1`.
- Validate inputs:
  - `lyrics` must not be empty when present
  - `lyrics` length ≤ 3000
  - `prompt` length ≤ 1024
- Log the `trace_id` returned by errors to assist troubleshooting.


# Generate instrumental

Endpoint  
POST `/v1/instrumental/generate`

Description  
Generate instrumental based on the input by the user.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "model": "string",
  "n": 0,
  "prompt": "string",
  "instrumental_id": "string",
  "stream": true
}
```

### Field details
- model (string)  
  - Valid values: `auto`, `mureka-6`, `mureka-7.5`  
  - Notes:
    - `auto` selects the latest version of the regular model
- n (integer, int32)  
  - Default: 2  
  - Maximum: 3  
  - Number of instrumentals to generate per request (billing scales with `n`)
- prompt (string)  
  - Max length: 1024 characters  
  - Controls instrumental generation via textual prompt  
  - When `prompt` is selected, do not include other control options (`instrumental_id`)
- instrumental_id (string)  
  - Controls generation by referencing music uploaded via the Files Upload API (for instrumental purpose)  
  - When `instrumental_id` is selected, do not include `prompt`
- stream (boolean)  
  - If `true`, the task will include a streaming phase  
  - During streaming, you can obtain `stream_url` to play the generated instrumental while generation progresses

## Responses
Status: `200 OK`  
Description: Asynchronous task information for generating instrumental. Use `instrumental/query/{task_id}` to poll for task information.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "created_at": 0,
  "finished_at": 0,
  "model": "string",
  "status": "string",
  "failed_reason": "string",
  "choices": [
    {
      "index": 0,
      "id": "string",
      "url": "string",
      "flac_url": "string",
      "stream_url": "string",
      "duration": 0
    }
  ]
}
```

### Status values
- `preparing`
- `queued`
- `running`
- `streaming`
- `succeeded`
- `failed`
- `timeouted`
- `cancelled`

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/instrumental/generate \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "prompt": "r&b, slow, passionate, male vocal",
    "n": 2,
    "stream": false
  }'
```

## Notes & Constraints
- Provide either `prompt` or `instrumental_id`—do not combine them.  
- `auto` picks the latest regular model version.  
- Streaming mode adds `streaming` status and returns `stream_url` during generation.  
- Validate inputs:
  - `prompt` length ≤ 1024  
  - `n` ≤ 3  
- Log the `trace_id` for easier troubleshooting when errors occur.

# Query task

Endpoint  
GET `/v1/song/query/{task_id}`

Description  
Query information about the song generation task.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Parameters

### Path
- task_id (string, required)  
  - The `task_id` of the song generation task.  
  - Example: `435134`

## Responses
Status: `200 OK`  
Description: Asynchronous task information for generating songs.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "created_at": 0,
  "finished_at": 0,
  "model": "string",
  "status": "string",
  "failed_reason": "string",
  "choices": [
    {
      "index": 0,
      "id": "string",
      "url": "string",
      "flac_url": "string",
      "stream_url": "string",
      "duration": 0
    }
  ]
}
```

### Status values
- `preparing`
- `queued`
- `running`
- `streaming`
- `succeeded`
- `failed`
- `timeouted`
- `cancelled`

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/song/query/435134 \
  -H "Authorization: Bearer $MUREKA_API_KEY"
```

## Notes
- Use the task `id` returned by `/v1/song/generate` to poll status and retrieve results.  
- During `streaming`, `stream_url` may be present for progressive playback.  
- On failure, check `failed_reason` and log any `trace_id` returned by the API in error responses.


# Query task (Instrumental)

Endpoint  
GET `/v1/instrumental/query/{task_id}`

Description  
Query information about the instrumental generation task.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Parameters

### Path
- task_id (string, required)  
  - The `task_id` of the instrumental generation task.  
  - Example: `435134`

## Responses
Status: `200 OK`  
Description: Asynchronous task information for generating instrumentals.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "created_at": 0,
  "finished_at": 0,
  "model": "string",
  "status": "string",
  "failed_reason": "string",
  "choices": [
    {
      "index": 0,
      "id": "string",
      "url": "string",
      "flac_url": "string",
      "stream_url": "string",
      "duration": 0
    }
  ]
}
```

### Status values
- `preparing`
- `queued`
- `running`
- `streaming`
- `succeeded`
- `failed`
- `timeouted`
- `cancelled`

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/instrumental/query/435134 \
  -H "Authorization: Bearer $MUREKA_API_KEY"
```

## Notes
- Use the task `id` returned by `/v1/instrumental/generate` to poll status and retrieve results.  
- During `streaming`, `stream_url` may be present for progressive playback.  
- On failure, check `failed_reason` and log any `trace_id` returned by the API in error responses.


# Query billing

Endpoint  
GET `/v1/account/billing`

Description  
Query the account's billing information.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Responses
Status: `200 OK`  
Description: The account's billing information.  
Content-Type: `application/json`

### Response schema
```json
{
  "account_id": 0,
  "balance": 0,
  "total_recharge": 0,
  "total_spending": 0,
  "concurrent_request_limit": 0
}
```

### Field details
- account_id (integer, int64)  
  - Account ID
- balance (integer, int64)  
  - The account balance, in cents
- total_recharge (integer, int64)  
  - The account's total recharge amount, in cents
- total_spending (integer, int64)  
  - The account's total spending amount, in cents
- concurrent_request_limit (integer, int64)  
  - The account's maximum concurrent requests

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/account/billing \
  -H "Authorization: Bearer $MUREKA_API_KEY"
```

## Notes
- All monetary values are returned in cents.  
- Ensure the Bearer token is valid; otherwise the request will be rejected.


# Generate lyrics

Endpoint  
POST `/v1/lyrics/generate`

Description  
Generate lyrics from the prompt.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "prompt": "string"
}
```

### Field details
- prompt (string, required)  
  - The prompt to generate lyrics for.

## Responses
Status: `200 OK`  
Description: The generated title and lyrics.  
Content-Type: `application/json`

### Response schema
```json
{
  "title": "string",
  "lyrics": "string"
}
```

### Field details
- title (string)  
  - The title generated based on the prompt.
- lyrics (string)  
  - The lyrics generated based on the prompt.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/lyrics/generate \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Embrace of Night"
  }'
```

## Notes
- Ensure your Bearer token is valid.  
- Provide a clear, concise prompt to guide lyrical style and content.


# Extend lyrics

Endpoint  
POST `/v1/lyrics/extend`

Description  
Continue writing lyrics from existing lyrics.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "lyrics": "string"
}
```

### Field details
- lyrics (string, required)  
  - Lyrics to be continued.

## Responses
Status: `200 OK`  
Description: The extended lyrics.  
Content-Type: `application/json`

### Response schema
```json
{
  "lyrics": "string"
}
```

### Field details
- lyrics (string)  
  - The lyrics extended based on the input lyrics.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/lyrics/extend \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "[Verse]\nIn the stormy night, I wander alone\nLost in the rain, feeling like I have been thrown\nMemories of you, they flash before my eyes\nHoping for a moment, just to find some bliss"
  }'
```

## Notes
- Ensure your Bearer token is valid.  
- Provide sufficiently rich input lyrics to guide the continuation style and structure.


# Extend song

Endpoint  
POST `/v1/song/extend`

Description  
Extend the song based on the input lyrics.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "song_id": "string",
  "upload_audio_id": "string",
  "lyrics": "string",
  "extend_at": 0
}
```

### Field details
- song_id (string)  
  - Song ID for extending, generated by the `song/generate` API.  
  - Mutually exclusive with `upload_audio_id`.
- upload_audio_id (string)  
  - Upload ID of the song to be extended, generated by the `files/upload` API (purpose: audio).  
  - Only supports songs generated within the last month.  
  - Mutually exclusive with `song_id`.
- lyrics (string, required)  
  - The lyrics to be extended.
- extend_at (integer, int64, required)  
  - Extending start time (milliseconds).  
  - If greater than song duration, defaults to song duration.  
  - Valid range: `[8000, 420000]`.

## Responses
Status: `200 OK`  
Description: Asynchronous task information for extending song. Use `song/query/{task_id}` to poll for task information.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "created_at": 0,
  "finished_at": 0,
  "model": "string",
  "status": "string",
  "failed_reason": "string",
  "choices": [
    {
      "index": 0,
      "id": "string",
      "url": "string",
      "flac_url": "string",
      "stream_url": "string",
      "duration": 0,
      "lyrics_sections": [
        {
          "section_type": "string",
          "start": 0,
          "end": 0,
          "lines": [
            {
              "start": 0,
              "end": 0,
              "text": "string",
              "words": [
                {
                  "start": 0,
                  "end": 0,
                  "text": "string"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Status values
- `preparing`
- `queued`
- `running`
- `streaming`
- `succeeded`
- `failed`
- `timeouted`
- `cancelled`

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/song/extend \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_audio_id": "43543541",
    "lyrics": "[Verse]\nIn the stormy night, I wander alone\nLost in the rain, feeling like I have been thrown\nMemories of you, they flash before my eyes\nHoping for a moment, just to find some bliss",
    "extend_at": 12234
  }'
```

## Notes & Constraints
- Provide either `song_id` or `upload_audio_id`—do not combine them.  
- `upload_audio_id` accepts only songs generated within the last month.  
- `extend_at` must be within `[8000, 420000]` ms; if above the song duration, it defaults to the duration.  
- Validate inputs and log any error `trace_id` for troubleshooting.


# Describe song

Endpoint  
POST `/v1/song/describe`

Description  
Understand and describe the input song.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "url": "string"
}
```

### Field details
- url (string, required)  
  - The URL of the song to be processed.  
  - Supported formats: `mp3`, `m4a`.  
  - Base64 data URL also supported (max 10 MB), e.g.  
    `data:audio/mp3;base64,AAAAGGZ...`

## Responses
Status: `200 OK`  
Description: The description of the song.  
Content-Type: `application/json`

### Response schema
```json
{
  "instrument": ["string"],
  "genres": ["string"],
  "tags": ["string"],
  "description": "string"
}
```

### Field details
- instrument (string[])  
  - List of instruments used in the song.
- genres (string[])  
  - List of song genres.
- tags (string[])  
  - List of song tags.
- description (string)  
  - Overall description of the song.

## Sample requests (cURL)

Use a standard URL:
```bash
curl https://api.mureka.ai/v1/song/describe \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://cdn.mureka.cn/1.mp3"
  }'
```

Use a URL in base64 format on macOS:
```bash
echo -n '{"url": "data:audio/mp3;base64,'"$(base64 -i test.mp3)"'"}' | \
  curl https://api.mureka.ai/v1/song/describe \
    -H "Authorization: Bearer $MUREKA_API_KEY" \
    -H "Content-Type: application/json" \
    -d @-
```

Use a URL in base64 format on Linux:
```bash
echo -n '{"url": "data:audio/mp3;base64,'"$(base64 -w 0 test.mp3)"'"}' | \
  curl https://api.mureka.ai/v1/song/describe \
    -H "Authorization: Bearer $MUREKA_API_KEY" \
    -H "Content-Type: application/json" \
    -d @-
```

## Notes & Constraints
- Ensure the audio is accessible and within the 10 MB limit for base64 data URLs.  
- Use supported formats (`mp3`, `m4a`) for best results.  
- Validate and log errors with any provided `trace_id` for troubleshooting.



# Stem song

Endpoint  
POST `/v1/song/stem`

Description  
Stem the song based on the input song (separate tracks and return a ZIP).

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "url": "string"
}
```

### Field details
- url (string, required)  
  - The URL of the song to be processed.  
  - Supported formats: `mp3`, `m4a`.  
  - Base64 data URL also supported (max 10 MB), e.g.  
    `data:audio/mp3;base64,AAAAGGZ...`

## Responses
Status: `200 OK`  
Description: Stem information.  
Content-Type: `application/json`

### Response schema
```json
{
  "zip_url": "string",
  "expires_at": 0
}
```

### Field details
- zip_url (string)  
  - The URL of the ZIP file containing all the split song tracks.
- expires_at (integer, int64)  
  - The Unix timestamp (in seconds) when the URL expires.

## Sample requests (cURL)

Use a standard URL:
```bash
curl https://api.mureka.ai/v1/song/stem \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://cdn.mureka.ai/1.mp3"
  }'
```

Use a URL in base64 format on macOS:
```bash
echo -n '{"url": "data:audio/mp3;base64,'"$(base64 -i test.mp3)"'"}' | \
  curl https://api.mureka.ai/v1/song/stem \
    -H "Authorization: Bearer $MUREKA_API_KEY" \
    -H "Content-Type: application/json" \
    -d @-
```

Use a URL in base64 format on Linux:
```bash
echo -n '{"url": "data:audio/mp3;base64,'"$(base64 -w 0 test.mp3)"'"}' | \
  curl https://api.mureka.ai/v1/song/stem \
    -H "Authorization: Bearer $MUREKA_API_KEY" \
    -H "Content-Type: application/json" \
    -d @-
```

## Notes & Constraints
- Ensure the audio is accessible and within the 10 MB limit for base64 data URLs.  
- Use supported formats (`mp3`, `m4a`).  
- Download the `zip_url` before `expires_at` to avoid broken links.  
- Log any error `trace_id` for troubleshooting.


# Create upload

Endpoint  
POST `/v1/uploads/create`

Description  
Creates an intermediate upload object that you can add parts to.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "upload_name": "string",
  "purpose": "string",
  "bytes": 0
}
```

### Field details
- upload_name (string, required)  
  - Give a name for this upload, or the name of the large file to upload.
- purpose (string)  
  - The intended purpose of this upload.  
  - Valid values: `fine-tuning`
- bytes (integer, int64)  
  - The total size of this upload.  
  - If not provided, the size will not be checked at the end.

## Responses
Status: `200 OK`  
Description: Task information for creating upload.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "upload_name": "string",
  "purpose": "string",
  "bytes": 0,
  "created_at": 0,
  "expires_at": 0,
  "status": "string",
  "parts": ["string"]
}
```

### Field details
- id (string)  
  - Task ID of the asynchronous task.
- upload_name (string)  
  - The name of the upload.
- purpose (string)  
  - The intended purpose of the upload.
- bytes (integer, int64)  
  - The total size of this upload.
- created_at (integer, int64)  
  - Unix timestamp (seconds) when the task was created.
- expires_at (integer, int64)  
  - Unix timestamp (seconds) when the task expires.
- status (string)  
  - Current status of the task.  
  - Valid values: `pending`, `completed`, `cancelled`
- parts (string[])  
  - List of parts included in this upload (only populated when status is `completed`).

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/uploads/create \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_name": "my.mp3",
    "purpose": "fine-tuning",
    "bytes": 12345678
  }'
```

## Notes & Workflow
- Use the returned `id` to add file parts via `/v1/uploads/add-part`, puis finalisez avec `/v1/uploads/complete`.  
- If `bytes` is omitted, final size checking is skipped at completion.  
- Log any error `trace_id` for troubleshooting.


# Add upload part

Endpoint  
POST `/v1/uploads/add`

Description  
Adds a part to an upload object. A part represents a portion (chunk) of a large file. Maximum size per part: up to 10 MB.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `multipart/form-data`  
Post data according to the multipart/form-data specification. Do not use JSON.

### Fields
- file (string, required, binary)  
  - The File object (not a file name) to be uploaded.  
  - For purpose `fine-tuning`: supported formats `mp3`, `m4a`.  
  - Audio duration must be between 30 seconds and 270 seconds.
- upload_id (string, required)  
  - The ID of the Upload object this part is added to.

## Responses
Status: `200 OK`  
Description: The uploaded part object.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "upload_id": "string",
  "created_at": 0
}
```

### Field details
- id (string)  
  - The upload part ID, which can be referenced in API endpoints.
- upload_id (string)  
  - The ID of the Upload object that this Part was added to.
- created_at (integer, int64)  
  - The Unix timestamp (in seconds) when the part was created.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/uploads/add \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -F upload_id="1436211" \
  -F file="@mydata.mp3"
```

## Notes & Constraints
- Use multipart/form-data; JSON bodies are not accepted for this endpoint.  
- Each part must be ≤ 10 MB.  
- For `fine-tuning` purpose: ensure audio is `mp3` or `m4a`, with duration in [30s, 270s].  
- After adding all parts, call `/v1/uploads/complete` to finalize the upload and list part IDs.


# Complete upload

Endpoint  
POST `/v1/uploads/complete`

Description  
Completes the Upload.  
If the upload was created with a specified `bytes` value, completion will verify that the total size of all parts matches `bytes`.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "upload_id": "string",
  "part_ids": ["string"]
}
```

### Field details
- upload_id (string, required)  
  - The ID of the Upload object to complete.
- part_ids (string[])  
  - Ordered list of part IDs.  
  - If omitted or empty, all parts previously added via `uploads/add` are used in the order they were added.

## Responses
Status: `200 OK`  
Description: The upload object with status completed.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "upload_name": "string",
  "purpose": "string",
  "bytes": 0,
  "created_at": 0,
  "expires_at": 0,
  "status": "string",
  "parts": ["string"]
}
```

### Field details
- id (string)  
  - Task ID of the asynchronous task.
- upload_name (string)  
  - The name of the upload.
- purpose (string)  
  - The intended purpose of the upload.
- bytes (integer, int64)  
  - Total size of the upload.
- created_at (integer, int64)  
  - Unix timestamp (seconds) when the task was created.
- expires_at (integer, int64)  
  - Unix timestamp (seconds) when the task expires.
- status (string)  
  - Current status of the task.  
  - Valid values: `pending`, `completed`, `cancelled`
- parts (string[])  
  - List of parts included in this upload (populated when status is `completed`).

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/uploads/complete \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "1436211"
  }'
```

## Notes & Workflow
- If `bytes` was set at creation, ensure the sum of part sizes equals `bytes` before completion.  
- Provide `part_ids` only if you need a custom order or subset; otherwise the service uses all added parts in insertion order.  
- After completion, use the resulting upload ID in endpoints that accept references (e.g., `reference_id`, `vocal_id`, `melody_id`, `instrumental_id`).


# Create fine-tuning task

Endpoint  
POST `/v1/finetuning/create`

Description  
Creates a fine-tuning task which begins the process of creating a new model from a given dataset.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "upload_id": "string",
  "suffix": "string"
}
```

### Field details
- upload_id (string, required)  
  - The ID of the upload object with status `completed`.  
  - Dataset guidance: upload 100–200 songs in a consistent style, each 2–4 minutes long.  
  - Training duration correlates with total audio length (e.g., 200 × 4 min ≈ ~3 hours).
- suffix (string, required)  
  - A string up to 32 characters appended to your fine-tuned model name.  
  - Allowed characters: lowercase letters, numbers, hyphens.  
  - Example: suffix `"my-model"` → model like `lora:mureka-6:4354198:my-model`.

## Responses
Status: `200 OK`  
Description: The fine-tuning task object.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "upload_id": "string",
  "model": "string",
  "created_at": 0,
  "finished_at": 0,
  "status": "string",
  "failed_reason": "string",
  "fine_tuned_model": "string"
}
```

### Field details
- id (string)  
  - Task ID of the asynchronous fine-tuning task.
- upload_id (string)  
  - The ID of the upload object.
- model (string)  
  - The base model that is being fine-tuned.
- created_at (integer, int64)  
  - Unix timestamp (seconds) when the task was created.
- finished_at (integer, int64)  
  - Unix timestamp (seconds) when the task was finished.
- status (string)  
  - Current status of the task.  
  - Valid values: `preparing`, `queued`, `running`, `succeeded`, `failed`, `timeouted`, `cancelled`
- failed_reason (string)  
  - The reason for failure (when status is `failed`).
- fine_tuned_model (string)  
  - The name of the fine-tuned model.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/finetuning/create \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "1436211",
    "suffix": "my-model"
  }'
```

## Notes & Workflow
- Prepare dataset via Uploads: `uploads/create` → `uploads/add` (chunks ≤ 10 MB) → `uploads/complete` (get `upload_id`).  
- Ensure audio consistency (style, length 2–4 min, count 100–200) for effective fine-tuning.  
- After `succeeded`, use `fine_tuned_model` with compatible endpoints (prompt or reference-only control as noted in generation docs).  
- Log `trace_id` from error responses to speed up troubleshooting.

# Query fine-tuning task

Endpoint  
GET `/v1/finetuning/query/{task_id}`

Description  
Query information about the fine-tuning task.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Parameters

### Path
- task_id (string, required)  
  - The `task_id` of the fine-tuning task.  
  - Example: `435134`

## Responses
Status: `200 OK`  
Description: Asynchronous task information for fine-tuning task.  
Content-Type: `application/json`

### Response schema
```json
{
  "id": "string",
  "upload_id": "string",
  "model": "string",
  "created_at": 0,
  "finished_at": 0,
  "status": "string",
  "failed_reason": "string",
  "fine_tuned_model": "string"
}
```

### Field details
- id (string)  
  - Task ID of the asynchronous fine-tuning task.
- upload_id (string)  
  - The ID of the upload object.
- model (string)  
  - The base model that is being fine-tuned.
- created_at (integer, int64)  
  - Unix timestamp (seconds) when the task was created.
- finished_at (integer, int64)  
  - Unix timestamp (seconds) when the task was finished.
- status (string)  
  - Current status of the task.  
  - Valid values: `preparing`, `queued`, `running`, `succeeded`, `failed`, `timeouted`, `cancelled`
- failed_reason (string)  
  - The reason for the failure.
- fine_tuned_model (string)  
  - The name of the fine-tuned model.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/finetuning/query/1436211 \
  -H "Authorization: Bearer $MUREKA_API_KEY"
```

## Notes
- Poll this endpoint using the task `id` returned by `/v1/finetuning/create` until `status` becomes `succeeded` or `failed`.  
- When `status` is `succeeded`, use `fine_tuned_model` with supported generation endpoints (subject to control option constraints).


# Create speech

Endpoint  
POST `/v1/tts/generate`

Description  
Generate audio from the input text.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "text": "string",
  "voice": "string",
  "voice_id": "string"
}
```

### Field details
- text (string, required)  
  - The text to generate audio for.  
  - Maximum length: 500 characters.
- voice (string)  
  - Predefined voice to use.  
  - Valid values: `Ethan`, `Victoria`, `Jake`, `Luna`, `Emma`.  
  - When `voice` is selected, do not include `voice_id`.
- voice_id (string)  
  - Reference a custom voice uploaded via the Files Upload API (voice purpose).  
  - When `voice_id` is selected, do not include `voice`.

## Responses
Status: `200 OK`  
Description: The audio content.  
Content-Type: `application/json`

### Response schema
```json
{
  "url": "string",
  "expires_at": 0
}
```

### Field details
- url (string)  
  - The URL of the generated audio file.
- expires_at (integer, int64)  
  - The Unix timestamp (in seconds) when the URL expires.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/tts/generate \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, my name is Emma.",
    "voice": "Emma"
  }'
```

## Notes & Constraints
- Choose either `voice` or `voice_id`—do not combine them.  
- Ensure your Bearer token is valid.  
- Download the audio before `expires_at` to avoid broken links.

# Create podcast

Endpoint  
POST `/v1/tts/podcast`

Description  
Transform two-voice scripts into ready-to-publish podcast-style audio conversations that sound natural.

## Authorization
- Scheme: BearerAuth  
- Type: HTTP (bearer)  
- Header: `Authorization: Bearer <MUREKA_API_KEY>`

## Request Body
Content-Type: `application/json`

### Schema
```json
{
  "conversations": [
    {
      "text": "string",
      "voice": "string"
    }
  ]
}
```

### Field details
- conversations (object[], required)  
  - Array of conversation turns.  
  - Maximum length: 10 items.  
  - Each item:
    - text (string): content to speak
    - voice (string): speaker voice (e.g., `Luna`, `Jake`, etc.)

## Responses
Status: `200 OK`  
Description: The audio content.  
Content-Type: `application/json`

### Response schema
```json
{
  "url": "string",
  "expires_at": 0
}
```

### Field details
- url (string)  
  - The URL of the generated podcast audio file.
- expires_at (integer, int64)  
  - The Unix timestamp (in seconds) when the URL expires.

## Sample request (cURL)
```bash
curl https://api.mureka.ai/v1/tts/podcast \
  -H "Authorization: Bearer $MUREKA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [{
      "text": "Hello, my name is Luna.",
      "voice": "Luna"
    },{
      "text": "Hello, my name is Jake.",
      "voice": "Jake"
    },{
      "text": "Great to be here!",
      "voice": "Luna"
    },{
      "text": "Likewise—let’s start.",
      "voice": "Jake"
    }]
  }'
```

## Notes & Constraints
- Provide clear, alternating turns for a natural dialogue.  
- Keep the array within 10 conversation items.  
- Download the audio before `expires_at` to avoid broken links.  
- Ensure your Bearer token is valid.

