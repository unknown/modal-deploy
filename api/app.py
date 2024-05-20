import json
from fastapi.responses import StreamingResponse
from client import ModalClient
from token_flow import TokenFlow

import modal

app = modal.App("modal-deploy")
image = modal.Image.debian_slim().pip_install("grpcio>=1.59.0")


def new_token(client: ModalClient):
    token_flow = TokenFlow(client)
    _, web_url, code = token_flow.start()

    yield json.dumps({"web_url": web_url, "code": code})

    result = None
    for _ in range(5):
        result = token_flow.finish()
        if result is not None:
            break

    if result is None:
        yield json.dumps({"error": "Timeout waiting for token flow to complete"})
        return

    yield json.dumps({"token_id": result.token_id, "token_secret": result.token_secret})


@app.function(image=image)
@modal.web_endpoint()
def new_token_endpoint():
    client = ModalClient()
    return StreamingResponse(new_token(client), media_type="text/event-stream")
