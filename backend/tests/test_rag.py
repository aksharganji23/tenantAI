def test_technova_rag_query_with_citations(client, technova_user_token):
    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": f"Bearer {technova_user_token}"},
        json={"message": "What is the warranty coverage for the battery?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert len(data["content"]) > 0
    assert len(data["citations"]) > 0
    # First citation must be the TechNova manual
    lead_citation = data["citations"][0]
    assert "UltraBook" in lead_citation["document_title"]
    assert lead_citation["page_number"] >= 1
    assert "excerpt" in lead_citation
    assert data["latency_ms"] >= 0


def test_greenleaf_rag_query_with_citations(client, greenleaf_user_token):
    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"},
        json={"message": "What is the return window for purchases?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert len(data["content"]) > 0
    assert len(data["citations"]) > 0
    lead_citation = data["citations"][0]
    assert "Refund" in lead_citation["document_title"]
    assert "30" in data["content"] or "return" in data["content"].lower()
