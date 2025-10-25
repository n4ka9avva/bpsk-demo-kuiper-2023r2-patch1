import numpy as np
from gnuradio import gr
import pmt

class blk(gr.basic_block):
    """CCSDS Telecommand Deframer (PDU)"""

    def __init__(self):
        gr.basic_block.__init__(self,
            name="CCSDS Telecommand Deframer (PDU)",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern('pdu_in'))
        self.message_port_register_out(pmt.intern('pdu_out'))
        self.set_msg_handler(pmt.intern('pdu_in'), self.handle_pdu)

    def handle_pdu(self, pdu):
        meta = pmt.car(pdu)
        data = bytes(pmt.u8vector_elements(pmt.cdr(pdu)))

        if len(data) < 6:
            return  # 不正フレーム（ヘッダ不足）

        # Primary Header除去
        header = data[:5]
        payload = data[5:]

        # Parse header
        frame_len = int.from_bytes(header[2:4], 'big') & 0x3FF # LSB 10bit
        frame_seq = header[4] 

        # meta情報にAPIDなどを追加（任意）
        meta = pmt.dict_add(meta, pmt.intern("frame_len"), pmt.from_long(frame_len))
        meta = pmt.dict_add(meta, pmt.intern("frame_seq"), pmt.from_long(frame_seq))

        out_pdu = pmt.cons(meta, pmt.init_u8vector(len(payload), list(payload)))
        self.message_port_pub(pmt.intern('pdu_out'), out_pdu)
