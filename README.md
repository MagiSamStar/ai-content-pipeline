## Social Media Agent 

An experimental LangGraph pipeline for transforming a spiritual reading into
structured social media content, visual direction, generated imagery, and
optional Canva and video outputs.

## Workflow

The pipeline is organized into focused modules:

1. `reading_agent.py` structures the source reading.
2. `content_agent.py` creates captions, reflections, quotes, and ChakraScope
   content using the brand guides.
3. `visual_agent.py` creates image and video direction.
4. `image_generator.py`, `canva.py`, and `higgsfield.py` connect to optional
   external creative services.
5. `output.py` saves runtime reading packages locally.

The full local workflow also uses proprietary creative guidance files that are
intentionally excluded from this public portfolio repository. They must be
provided locally before running the complete pipeline.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in only the credentials for the services you intend to use. Never commit
`.env` or `.canva_token.json`.

## Run

The example input is stored in `examples/sample_input.md` and is loaded by the
existing `main.py` entry point:

```powershell
python main.py
```

Running the workflow may call configured model, image, Canva, and video
services and may create local files under `outputs/` and `readings/`. Those
runtime directories are intentionally ignored by Git.

Importing `main.py` does not invoke the workflow; execution occurs only when
the file is run directly.

## External services

- OpenAI-compatible access is used by the reading and image agents.
- Ollama can serve as a local content-model option and fallback. It is not a
  fallback for visual media generation; image and video generation use the
  configured external services.
- Canva requires OAuth configuration and may open a browser during first-time
  authorization.
- Higgsfield is optional and requires `HF_KEY`.

Full end-to-end execution requires the private creative guidance files, valid
credentials, and, when using the local content option, a running Ollama
service with the configured model available.

## Example

See [`examples/sample_output.md`](examples/sample_output.md) for a sanitized,
fictional example of the structured output. No generated media or private
readings are included in this repository.

## License

No license has been selected for this project yet.
