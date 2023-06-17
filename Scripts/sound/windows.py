import sounddevice as sd
import queue
import sys
import soundfile as sf

from ..decorators import thread


def callback(outdata, frames: int, time, status: sd.CallbackFlags, q: queue.Queue, blocksize: int):
    assert frames == blocksize
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty as e:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort from e
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data


@thread()
def play(filename: str):
    block_size = 2048
    buffer_size = 20

    q = queue.Queue(maxsize=buffer_size)

    with sf.SoundFile(filename) as f:
        for _ in range(buffer_size):
            data = f.buffer_read(block_size,  dtype='float32')
            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue
        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=block_size,
            channels=f.channels, dtype='float32',
            callback=lambda o, f, t, s: callback(o, f, t, s, q, block_size),
        )
        with stream:
            timeout = block_size * buffer_size / f.samplerate
            data = b'x' # make sure that data is not unbound
            while data:
                data = f.buffer_read(block_size,  dtype='float32')
                q.put(data, timeout=timeout)
