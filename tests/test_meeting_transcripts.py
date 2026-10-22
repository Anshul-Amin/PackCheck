"""Tests for meeting transcripts extraction and document priority hierarchy resolution."""

from src.packcheck.qa import answer_packaging_question
from src.packcheck.transcripts.extractor import extract_meeting_transcript, parse_speaker_turns


def test_transcript_speaker_turn_parsing():
    sample = """
    [00:01:12] Sarah Jenkins (SJ): Welcome everyone.
    [00:02:40] Dave Chen (DC): The title is shifted +76 points rightward.
    """
    turns = parse_speaker_turns(sample)
    assert len(turns) == 2
    assert turns[0].speaker == "Sarah Jenkins"
    assert turns[0].role == "SJ"
    assert turns[1].speaker == "Dave Chen"
    assert "+76 points" in turns[1].text


def test_transcript_conflict_detection_written_spec_precedence():
    sample = """
    PACKAGING ALIGNMENT MEETING
    ATTENDEES:
    - Sarah Jenkins (Regulatory)
    - Marcus Vance (Brand)
    - Dave Chen (Agency)

    [00:05:00] Marcus Vance (MV): We want to add Made with 12% Real Wild Honey on the front banner.
    [00:06:00] Sarah Jenkins (SJ): Written formulation sheet says 8.5% Honey. Written spec takes precedence.
    [00:10:00] Dave Chen (DC): Imported Nutrition Facts from last season: Cholesterol 45mg 26% DV.
    [00:12:00] Elena Rostova (ER): 166 was the calorie count for a 30g snack pouch... copy-paste error.
    """
    doc = extract_meeting_transcript(sample, filename="test_meeting.txt")
    assert len(doc.attendees) == 3
    assert len(doc.conflicts_with_written_docs) >= 2

    # Verify honey conflict rule
    honey_conflicts = [c for c in doc.conflicts_with_written_docs if "honey" in c.topic.lower()]
    assert len(honey_conflicts) == 1
    assert honey_conflicts[0].resolution_status == "WRITTEN_SPEC_PREVAILS"
    assert "8.5%" in honey_conflicts[0].written_document_value

    # Verify cholesterol conflict rule
    chol_conflicts = [
        c for c in doc.conflicts_with_written_docs if "cholesterol" in c.topic.lower()
    ]
    assert len(chol_conflicts) == 1
    assert chol_conflicts[0].resolution_status == "WRITTEN_SPEC_PREVAILS"


def test_qa_assistant_with_global_and_transcript_context():
    sample_ts = """
    [00:01:00] Sarah Jenkins: We cannot claim 12% honey when written spec says 8.5%.
    """
    doc = extract_meeting_transcript(sample_ts, filename="sample.txt")

    # Ask about fail testcases
    ans1 = answer_packaging_question(
        question="what is the real reason behind the fail testcases",
        transcript=doc,
        scope="global",
    )
    assert "Analysis of Packaging Audit Failures" in ans1 or "Regulatory Impact" in ans1

    # Ask about meeting transcript
    ans2 = answer_packaging_question(
        question="what was discussed in the meeting transcript?",
        transcript=doc,
        scope="global",
    )
    assert "Meeting" in ans2 or "Transcript" in ans2

    # Ask about conflict priority
    ans3 = answer_packaging_question(
        question="what is the priority rule between transcripts and written documents?",
        transcript=doc,
        scope="global",
    )
    assert "Tier 1" in ans3 or "Precedence" in ans3 or "WRITTEN" in ans3
