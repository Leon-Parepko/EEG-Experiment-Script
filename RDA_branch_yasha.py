import asyncio
import json
import struct

from asyncio import StreamReader, StreamWriter
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Generator, Self, TypeAlias

import aiofiles


Microseconds: TypeAlias = float


class MessageType(Enum):
    START = 1
    DATA16BIT = 2
    END = 3
    DATA = 4


@dataclass
class Marker:
    position: int
    points: int
    channel: int
    type_name: str
    description: str

    @classmethod
    def list_from_bytes(cls, raw_data: bytes, count: int) -> list[Self]:
        MIN_SIZE_OFFSET = 16  # four longs

        markers: list[Self] = []

        offset = 0
        for _ in range(count):
            length, position, points, channel = struct.unpack('<LLLl', raw_data[offset:offset + MIN_SIZE_OFFSET])
            type_name, description, *_ = raw_data[offset + MIN_SIZE_OFFSET:offset + length].split(b'\x00')
            
            markers.append(cls(position, points, channel, type_name, description))

            offset += length
        
        return markers
    
    @staticmethod
    def list_to_file_file_format(markers: list[Self], block_id: int) -> Generator[str, None, None]:
        for marker in markers:
            yield f'{block_id},{marker.position},{marker.points},{marker.channel},{marker.type_name.decode()},{marker.description.decode()};\n'


@dataclass
class DataBlock:
    block_id: int
    points: list[float]
    markers: list[Marker]

    @classmethod
    def from_bytes(cls, raw_data: bytes, channels_count: int) -> Self:
        MIN_SIZE_OFFSET = 12  # three unsigned longs
        FLOAT_SIZE = 4

        block_id, points_count, markers_count = struct.unpack('<LLL', raw_data[:MIN_SIZE_OFFSET])

        points_raw_string = raw_data[MIN_SIZE_OFFSET:MIN_SIZE_OFFSET + points_count * channels_count * FLOAT_SIZE]
        points = list(struct.unpack(f'<{"f" * points_count * channels_count}', points_raw_string))

        if markers_count:
            markers_raw_string = raw_data[MIN_SIZE_OFFSET + points_count * channels_count * FLOAT_SIZE:]
            markers = Marker.list_from_bytes(markers_raw_string, markers_count)
        else:
            markers = []

        return cls(block_id, points, markers)
    
    def to_file_format(self, channels_count: int) -> Generator[str, None, None]:
        for i in range(0, len(self.points), channels_count):
            yield f'{self.block_id},{",".join(map(str, self.points[i:i + channels_count]))};\n'


@dataclass
class HeaderPayload:
    guid: list[int]  # from docs: 128-bit constant for unique identification.
    message_length: int
    message_type: MessageType

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> Self:
        *guid, message_length, message_type = struct.unpack('<llllLL', raw_data)
        return cls(guid, message_length, message_type)


@dataclass
class PropertiesPayload:
    sampling_interval: Microseconds
    resolutions: tuple[float, ...]
    channel_names: tuple[str, ...]

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> Self:
        MIN_SIZE_OFFSET = 12  # one unsigned long plus one double
        DOUBLE_SIZE = 8  # double as C type

        channels_count, sampling_interval = struct.unpack('<Ld', raw_data[:MIN_SIZE_OFFSET])

        resolutions_raw_string = raw_data[MIN_SIZE_OFFSET:MIN_SIZE_OFFSET + DOUBLE_SIZE * channels_count]
        resolutions = struct.unpack(f'<{"d" * channels_count}', resolutions_raw_string)

        channel_names = map(bytes.decode, raw_data[MIN_SIZE_OFFSET + DOUBLE_SIZE * channels_count:].split(b'\x00'))
        channel_names = tuple(filter(bool, channel_names))

        return cls(sampling_interval, resolutions, channel_names)


class FileWritter:
    def __init__(self, data_blocks_filename: Path, properties_filename: Path, markers_filename: Path):
        self.data_blocks_filename = data_blocks_filename
        self.properties_filename = properties_filename
        self.markers_filename = markers_filename

        self.filenames: list[Path] = [data_blocks_filename, properties_filename, markers_filename]
        self.files: dict[Path, aiofiles.threadpool.binary.AsyncBufferedIOBase] = {}

        self.properties: PropertiesPayload | None = None
    
    async def __aenter__(self) -> Self:
        for filename in self.filenames:
            self.files[filename] = await aiofiles.open(filename, 'w')

        return self

    async def __aexit__(self, *args) -> None:
        for file in self.files.values():
            await file.close()
    
    async def write_data_block(self, data_block: DataBlock) -> None:
        for line in data_block.to_file_format(len(self.properties.channel_names)):
            await self.files[self.data_blocks_filename].write(line)
        
        for line in Marker.list_to_file_file_format(data_block.markers, data_block.block_id):
            await self.files[self.markers_filename].write(line)
    
    async def write_properties(self, properties: PropertiesPayload) -> None:
        self.properties = properties
        await self.files[self.properties_filename].write(json.dumps(asdict(properties)))


class RDA:
    def __init__(self, host_ip: str, port: int):
        self.host_ip = host_ip
        self.port = port

        self.socket_reader: StreamReader | None = None
        self.socket_writer: StreamWriter | None = None
    
    async def connect(self) -> None:
        self.socket_reader, self.socket_writer = await asyncio.open_connection(self.host_ip, self.port)
    
    async def disconnect(self) -> None:
        self.socket_writer.close()
        await self.socket_writer.wait_closed()
    
    async def run_data_receiver(self) -> None:
        HEADER_SIZE = 24
        properties: PropertiesPayload | None = None
        keep_receiving = True

        await self.connect()

        try:
            async with FileWritter("datablocks.csv", "properties.json", "markers.csv") as file_writter:
                while keep_receiving:
                    header_raw: bytes = await self.socket_reader.read(HEADER_SIZE)
                    header_payload = HeaderPayload.from_bytes(header_raw)

                    data_raw: bytes = await self.socket_reader.read(header_payload.message_length - HEADER_SIZE)

                    match header_payload.message_type:
                        case 1:
                            properties = PropertiesPayload.from_bytes(data_raw)
                            await file_writter.write_properties(properties)
                        case 4:
                            data_block = DataBlock.from_bytes(data_raw, len(properties.channel_names))
                            await file_writter.write_data_block(data_block)
                        case 3:
                            keep_receiving = False
                        case 10000:
                            continue
                        case _:
                            print(f'Received message with wrong type: {header_payload.message_type}')
                            continue

        except asyncio.CancelledError:
            await self.disconnect()


def run_rda(host_ip: str = '100.1.1.3', port: int = 51244):
    rda = RDA(host_ip = host_ip, port=port)
    asyncio.run(rda.run_data_receiver())


if __name__ == '__main__':
    run_rda()
