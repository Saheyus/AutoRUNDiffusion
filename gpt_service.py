from concurrent import futures
import grpc
import gpt_service_pb2
import gpt_service_pb2_grpc

class GPTServicer(gpt_service_pb2_grpc.GPTServiceServicer):
    def ProcessText(self, request, context):
        # Implement your script here. For example:
        result = process_text(request.text)  # Assume process_text is your script function
        return gpt_service_pb2.ProcessReply(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpt_service_pb2_grpc.add_GPTServiceServicer_to_server(GPTServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
