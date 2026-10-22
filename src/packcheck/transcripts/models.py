"""Data models for meeting transcripts and authority priority resolution."""

from pydantic import BaseModel, Field


class TranscriptSpeakerTurn(BaseModel):
    """A single speaker utterance in a packaging meeting transcript."""

    timestamp: str = ""
    speaker: str = ""
    role: str = ""
    text: str = ""


class TranscriptConflict(BaseModel):
    """Conflict between meeting dialogue and written approved documents."""

    topic: str
    transcript_quote: str
    written_document_value: str
    authority_rule: str = "Written specification documents (Content Sheet / FDA rules) take strict precedence over verbal discussions."
    resolution_status: str  # "WRITTEN_SPEC_PREVAILS" or "WAIVER_PERMITTED"
    explanation: str


class TranscriptDecision(BaseModel):
    """An agreed packaging decision or design waiver made in the meeting."""

    category: str  # "design_waiver", "formulation", "action_item", "regulatory"
    decision: str
    speaker_or_owner: str
    impact_on_artwork: str


class MeetingTranscriptDoc(BaseModel):
    """Structured extraction of a packaging meeting transcript."""

    filename: str = ""
    title: str = "Packaging Alignment & Pre-Press Meeting"
    meeting_date: str = ""
    attendees: list[str] = Field(default_factory=list)
    speaker_turns: list[TranscriptSpeakerTurn] = Field(default_factory=list)
    key_decisions: list[TranscriptDecision] = Field(default_factory=list)
    conflicts_with_written_docs: list[TranscriptConflict] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    raw_text: str = ""
