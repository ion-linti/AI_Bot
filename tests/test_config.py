from app.config.sources_loader import load_sources

def test_load_sources():
    srcs = load_sources()
    assert len(srcs) >= 6
    ids = {s.id for s in srcs}
    assert "bens" in ids and "arxiv_ai" in ids
