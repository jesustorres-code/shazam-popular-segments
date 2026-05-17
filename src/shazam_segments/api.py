from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from . import __version__
from .workflow import create_case, extract_case, list_cases, list_clips, search_metadata


app = FastAPI(
    title="Shazam Popular Segments API",
    version=__version__,
    description="API for resolving song metadata and extracting Shazam Popular Segment clips.",
)


class MetadataResponse(BaseModel):
    provider: str
    title: str | None = None
    artist: str | None = None
    durationSeconds: int | None = None
    isrc: str | None = None
    preview: str | None = None
    deezerId: int | None = None
    trackId: int | None = None
    url: str | None = None


class CaseCreateRequest(BaseModel):
    query: str
    provider: Literal["deezer", "itunes"] = "deezer"
    casesDir: str = "data/cases"
    slug: str | None = None
    segmentStart: str | None = None
    segmentEnd: str | None = None


class CaseExtractRequest(BaseModel):
    casePath: str
    audio: str | None = None
    outputsDir: str = "outputs/clips"
    videoSeconds: float = Field(default=7, gt=0)
    downloadDir: str = "outputs/downloads"


class RunRequest(BaseModel):
    query: str
    provider: Literal["deezer", "itunes"] = "deezer"
    segmentStart: str
    segmentEnd: str
    casesDir: str = "data/cases"
    outputsDir: str = "outputs/clips"
    downloadDir: str = "outputs/downloads"
    slug: str | None = None
    videoSeconds: float = Field(default=7, gt=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    index_path = Path(__file__).parent / "static" / "index.html"
    return index_path.read_text(encoding="utf-8")


@app.get("/metadata", response_model=MetadataResponse)
def metadata(query: str, provider: Literal["deezer", "itunes"] = "deezer"):
    try:
        result = search_metadata(provider, query)
    except Exception as exc:  # pragma: no cover - defensive API wrapper
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="No result found")
    return result


@app.post("/cases")
def post_case(request: CaseCreateRequest):
    try:
        return create_case(
            request.query,
            provider=request.provider,
            cases_dir=request.casesDir,
            slug=request.slug,
            segment_start=request.segmentStart,
            segment_end=request.segmentEnd,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/cases")
def get_cases(casesDir: str = "data/cases"):
    return {"cases": list_cases(casesDir)}


@app.post("/extract")
def post_extract(request: CaseExtractRequest):
    try:
        return extract_case(
            request.casePath,
            audio=request.audio,
            outputs_dir=request.outputsDir,
            video_seconds=request.videoSeconds,
            download_dir=request.downloadDir,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/run")
def post_run(request: RunRequest):
    try:
        created = create_case(
            request.query,
            provider=request.provider,
            cases_dir=request.casesDir,
            slug=request.slug,
            segment_start=request.segmentStart,
            segment_end=request.segmentEnd,
        )
        extracted = extract_case(
            created["case"],
            outputs_dir=request.outputsDir,
            video_seconds=request.videoSeconds,
            download_dir=request.downloadDir,
        )
        return {"case": created, "extract": extracted}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/clips")
def get_clips(outputsDir: str = "outputs/clips"):
    return {"clips": list_clips(outputsDir)}


@app.get("/clips/{clip_name}")
def get_clip_file(clip_name: str, outputsDir: str = "outputs/clips"):
    clip_path = Path(outputsDir) / clip_name
    root = Path(outputsDir).resolve()
    resolved = clip_path.resolve()
    if root not in resolved.parents or not resolved.is_file():
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(resolved, media_type="audio/mpeg", filename=resolved.name)
