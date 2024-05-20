from client import ModalClient
from modal_proto import api_pb2


class TokenFlow:
    def __init__(self, client: ModalClient):
        self.stub = client.stub

    def start(self):
        req = api_pb2.TokenFlowCreateRequest(
            utm_source="modal-deploy",
            localhost_port=None,
            next_url=None,
        )
        resp = self.stub.TokenFlowCreate(req)
        self.token_flow_id = resp.token_flow_id
        self.wait_secret = resp.wait_secret
        return (resp.token_flow_id, resp.web_url, resp.code)

    def finish(self, timeout: float = 40.0, grpc_extra_timeout: float = 5.0):
        req = api_pb2.TokenFlowWaitRequest(
            token_flow_id=self.token_flow_id,
            timeout=timeout,
            wait_secret=self.wait_secret,
        )
        resp = self.stub.TokenFlowWait(req, timeout=(timeout + grpc_extra_timeout))
        if not resp.timeout:
            return resp
        else:
            return None
