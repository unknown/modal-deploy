import grpc

from modal_proto import api_pb2_grpc


class ModalClient:
    def __init__(self):
        self._channel = grpc.secure_channel(
            "api.modal.com:443", grpc.ssl_channel_credentials()
        )
        self._stub = api_pb2_grpc.ModalClientStub(self._channel)

    @property
    def stub(self):
        return self._stub
