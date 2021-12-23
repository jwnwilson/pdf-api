def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "pdf generator service"}


def test_create_pdf_task(client):
    response = client.post("/")
    assert response.status_code == 200
    assert response.json() == {"message": "pdf generator service"}
