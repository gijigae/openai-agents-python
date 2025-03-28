import curses
import time

import numpy as np
import numpy.typing as npt
import sounddevice as sd


def _record_audio(screen: curses.window) -> npt.NDArray[np.float32] | None:
    screen.nodelay(True)  # Non-blocking input
    screen.clear()
    screen.addstr(
        "Press <spacebar> to START talking, press again to STOP. Press <return> to exit.\n"
    )
    screen.refresh()

    recording = False
    audio_buffer: list[npt.NDArray[np.float32]] = []
    terminate = False

    def _audio_callback(indata, frames, time_info, status):
        if status:
            screen.addstr(f"Status: {status}\n")
            screen.refresh()
        if recording:
            audio_buffer.append(indata.copy())

    # Open the audio stream with the callback.
    with sd.InputStream(samplerate=24000, channels=1, dtype=np.float32, callback=_audio_callback):
        while not terminate:
            key = screen.getch()
            
            if key == ord(" "):  # Spacebar pressed
                recording = not recording
                if recording:
                    screen.clear()
                    screen.addstr("Recording... Press <spacebar> again to stop.\n")
                    screen.refresh()
                else:
                    screen.clear()
                    screen.addstr("Processing...\n")
                    screen.refresh()
                    # Only break the loop if we've collected some audio data
                    if audio_buffer:
                        break
                    else:
                        screen.clear()
                        screen.addstr("No audio recorded. Press <spacebar> to try again or <return> to exit.\n")
                        screen.refresh()
            elif key == 10 or key == 13:  # Enter/Return key
                recording = False
                terminate = True
                screen.clear()
                screen.addstr("Conversation terminated.\n")
                screen.refresh()
                return None  # Signal to terminate conversation
            
            time.sleep(0.01)

    # Combine recorded audio chunks.
    if audio_buffer:
        audio_data = np.concatenate(audio_buffer, axis=0)
        # Ensure we have valid audio data
        if len(audio_data) > 0:
            return audio_data
    
    # If we reach here without valid audio data, return an empty array
    return np.empty((0, 1), dtype=np.float32)


def record_audio():
    """
    Record audio from the microphone using a toggle approach.
    Press spacebar to start recording, press again to stop.
    Press return to exit the conversation.
    
    Returns:
        numpy array of audio data or None if conversation was terminated
    """
    # Using curses to record audio in a way that:
    # - doesn't require accessibility permissions on macos
    # - doesn't block the terminal
    audio_data = curses.wrapper(_record_audio)
    
    # Additional validation to ensure we're not sending empty audio
    if audio_data is not None and (len(audio_data) == 0 or np.all(audio_data == 0)):
        print("Warning: No audio detected. Please try again.")
        return np.empty((24000, 1), dtype=np.float32)  # Return 1 second of silence instead of empty
        
    return audio_data


class AudioPlayer:
    def __enter__(self):
        self.stream = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()

    def add_audio(self, audio_data: npt.NDArray[np.int16]):
        self.stream.write(audio_data)
