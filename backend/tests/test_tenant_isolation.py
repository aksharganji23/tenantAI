def test_document_listing_isolation(client, technova_user_token, greenleaf_user_token):
    # TechNova listing
    tn_resp = client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert tn_resp.status_code == 200
    tn_docs = tn_resp.json()
    assert len(tn_docs) > 0
    tn_titles = [d["title"] for d in tn_docs]
    assert any("UltraBook" in t for t in tn_titles)
    # Must NOT contain GreenLeaf document
    assert not any("Refund" in t for t in tn_titles)

    # GreenLeaf listing
    gl_resp = client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"}
    )
    assert gl_resp.status_code == 200
    gl_docs = gl_resp.json()
    assert len(gl_docs) > 0
    gl_titles = [d["title"] for d in gl_docs]
    assert any("Refund" in t for t in gl_titles)
    # Must NOT contain TechNova document
    assert not any("UltraBook" in t for t in gl_titles)


def test_cross_tenant_document_read_rejected(client, technova_user_token, greenleaf_user_token):
    # Get TechNova's document ID
    tn_resp = client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    tn_doc_id = tn_resp.json()[0]["id"]

    # GreenLeaf user attempts direct IDOR read on TechNova's document
    idor_resp = client.get(
        f"/api/v1/documents/{tn_doc_id}",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"}
    )
    # Must return 404 Not Found to prevent leaking document existence
    assert idor_resp.status_code == 404
    assert idor_resp.json()["detail"] == "Document not found"


def test_cross_tenant_document_delete_rejected(client, technova_user_token, greenleaf_user_token):
    # Get TechNova's document ID
    tn_resp = client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    tn_doc_id = tn_resp.json()[0]["id"]

    # GreenLeaf user attempts malicious DELETE on TechNova's document
    del_resp = client.delete(
        f"/api/v1/documents/{tn_doc_id}",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"}
    )
    assert del_resp.status_code == 404

    # Verify TechNova document was NOT deleted
    verify_resp = client.get(
        f"/api/v1/documents/{tn_doc_id}",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert verify_resp.status_code == 200


def test_cross_tenant_conversation_isolation(client, technova_user_token, greenleaf_user_token):
    # TechNova creates a conversation
    chat_resp = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": f"Bearer {technova_user_token}"},
        json={"message": "What is the UltraBook battery capacity?"}
    )
    assert chat_resp.status_code == 200
    conv_id = chat_resp.json()["conversation_id"]

    # GreenLeaf user attempts to read TechNova's conversation history
    gl_conv_resp = client.get(
        f"/api/v1/chat/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"}
    )
    assert gl_conv_resp.status_code == 404

    # GreenLeaf user attempts to send a message into TechNova's conversation
    gl_post_resp = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"},
        json={
            "conversation_id": conv_id,
            "message": "Can I hijack this thread?"
        }
    )
    assert gl_post_resp.status_code == 404


def test_cross_tenant_vector_search_leak_prevention(client, greenleaf_user_token):
    """
    GreenLeaf user asks specifically for confidential TechNova UltraBook hardware details.
    RAG vector search MUST NEVER return TechNova's chunks.
    The response must admit that no info is found in GreenLeaf's workspace.
    """
    resp = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": f"Bearer {greenleaf_user_token}"},
        json={"message": "What is the BIOS password reset procedure for the UltraBook Pro X15?"}
    )
    assert resp.status_code == 200
    data = resp.json()

    # Citations must be completely empty or belong ONLY to GreenLeaf
    for citation in data.get("citations", []):
        assert citation["document_title"] != "TechNova UltraBook Pro X15 Hardware Manual"

    # Answer should state it cannot find information in GreenLeaf Retail
    content = data["content"]
    assert "could not find information" in content.lower() or "greenleaf" in content.lower()
