# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gpt_service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11gpt_service.proto\x12\nGPTService\"\x1e\n\x0eProcessRequest\x12\x0c\n\x04text\x18\x01 \x01(\t\"\x1e\n\x0cProcessReply\x12\x0e\n\x06result\x18\x01 \x01(\t2S\n\nGPTService\x12\x45\n\x0bProcessText\x12\x1a.GPTService.ProcessRequest\x1a\x18.GPTService.ProcessReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gpt_service_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_PROCESSREQUEST']._serialized_start=33
  _globals['_PROCESSREQUEST']._serialized_end=63
  _globals['_PROCESSREPLY']._serialized_start=65
  _globals['_PROCESSREPLY']._serialized_end=95
  _globals['_GPTSERVICE']._serialized_start=97
  _globals['_GPTSERVICE']._serialized_end=180
# @@protoc_insertion_point(module_scope)