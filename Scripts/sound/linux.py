import wave
import alsaaudio
from ..decorators import thread


@thread()
def play(filename: str):
    with wave.open(filename, 'rb') as f:
        format = None

        # 8bit is unsigned in wav files
        if f.getsampwidth() == 1:
            format = alsaaudio.PCM_FORMAT_U8
        # Otherwise we assume signed data, little endian
        elif f.getsampwidth() == 2:
            format = alsaaudio.PCM_FORMAT_S16_LE
        elif f.getsampwidth() == 3:
            format = alsaaudio.PCM_FORMAT_S24_3LE
        elif f.getsampwidth() == 4:
            format = alsaaudio.PCM_FORMAT_S32_LE
        else:
            raise ValueError('Unsupported format')

        periodsize = f.getframerate() // 8

        device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize, device='default')
        
        data = f.readframes(periodsize)
        while data:
            # Read data from stdin
            device.write(data)
            data = f.readframes(periodsize)
