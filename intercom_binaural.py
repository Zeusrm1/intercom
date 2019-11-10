# Exploiting binaural redundancy.

# Binaural Issue #45
# Current Version 1.2 - Status: Working (with -s 2048 in windows)
#
#1.3    -   make copy of indata instead of reference
#1.2    -   comments inside code
#1.1    -   cleanup
#1.0    -   implemented R=R-L and restore R=R+L

import numpy as np
from intercom_bitplanes import Intercom_bitplanes

if __debug__:
    import sys
    
class Intercom_binaural(Intercom_bitplanes):

    def init(self, args):
        #NOCHANGE_PARENT initialize and config stream
        Intercom_bitplanes.init(self, args)
        if self.number_of_channels == 2:
            self.record_send_and_play = self.record_send_and_play_stereo

    def record_send_and_play_stereo(self, indata, outdata, frames, time, status):
        #make copy of original indata
        binaural_data=np.copy(indata)
        #subtract left channel from right channel R=R-L
        binaural_data[:,1]=binaural_data[:,1]-binaural_data[:,0]
        
        #send changed data
        self.send(binaural_data)

        #NOCHANGE_PARENT increase recorded chunk number
        self.recorded_chunk_number = (self.recorded_chunk_number + 1) % self.MAX_CHUNK_NUMBER

        #NOCHANGE_PARENT get chunk from buffer
        chunk = self._buffer[self.played_chunk_number % self.cells_in_buffer]

        #restore binaural data R=R+L
        chunk[:,1] = chunk[:,1]+chunk[:,0]

        #NOCHANGE_PARENT replace played chunk with silence
        self._buffer[self.played_chunk_number % self.cells_in_buffer] = self.generate_zero_chunk()

        #NOCHANGE_PARENT increase played chunk number
        self.played_chunk_number = (self.played_chunk_number + 1) % self.cells_in_buffer

        #NOCHANGE_PARENT play chunk
        outdata[:] = chunk

        if __debug__:
            sys.stderr.write("."); sys.stderr.flush()
        

if __name__ == "__main__":
    intercom = Intercom_binaural()
    parser = intercom.add_args()
    args = parser.parse_args()
    intercom.init(args)
    intercom.run()
