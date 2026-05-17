# API

Stage 4 adds a small HTTP API around the CLI workflow.

## Install

```bash
python3 -m pip install --user '.[api]'
```

## Run

```bash
shazam-segment serve --host 0.0.0.0 --port 8000
```

Local development without installing:

```bash
PYTHONPATH=src python3 -m shazam_segments.cli serve --host 127.0.0.1 --port 8000
```

## Endpoints

### Health

```bash
curl http://127.0.0.1:8000/health
```

### Metadata

```bash
curl 'http://127.0.0.1:8000/metadata?query=EL%20DE%20LA%20TINTA%20Sahir%20Montoya%20holanda&provider=deezer'
```

### Create Case

```bash
curl -X POST http://127.0.0.1:8000/cases \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "EL DE LA TINTA Sahir Montoya holanda",
    "provider": "deezer",
    "segmentStart": "00:00",
    "segmentEnd": "00:05"
  }'
```

### Extract Case

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H 'Content-Type: application/json' \
  -d '{
    "casePath": "data/cases/el-de-la-tinta-holanda/metadata.json",
    "videoSeconds": 7
  }'
```

## Current Limitations

- Jobs are synchronous.
- Generated clips are written to local disk.
- No authentication yet.
- No queue or persistent job database yet.
