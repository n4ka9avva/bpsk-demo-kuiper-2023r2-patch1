#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import iio
import bpsk_demo_rx_parse_telecmd as parse_telecmd  # embedded python block
import threading




class bpsk_demo_rx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.upsampling = upsampling = 50
        self.sps = sps = 4
        self.baud_rate = baud_rate = 9600
        self.samp_rate = samp_rate = baud_rate*sps*upsampling
        self.nfilts = nfilts = 16
        self.Alpha = Alpha = 0.35
        self.thresh = thresh = 0
        self.sync_loop_bw = sync_loop_bw = 5.0e-3
        self.rx_gain = rx_gain = 50
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts, 1.0/float(sps), Alpha, 11*sps*nfilts)
        self.lpf_taps = lpf_taps = firdes.low_pass(1, samp_rate, samp_rate/4, 3e3, window.WIN_HAMMING, 6.76)
        self.lo = lo = 2.4e9
        self.fll_loop_bw = fll_loop_bw = 60.0e-3
        self.costas_loop_bw = costas_loop_bw = 60.0e-3
        self.const = const = digital.constellation_bpsk().base()
        self.const.set_npwr(1.0)

        ##################################################
        # Blocks
        ##################################################

        self.pdu_tagged_stream_to_pdu_0_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_2 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.parse_telecmd = parse_telecmd.blk()
        self.iio_fmcomms2_source_0 = iio.fmcomms2_source_fc32('ip:127.0.0.1', [True, True, False, False], int(256e3))
        self.iio_fmcomms2_source_0.set_len_tag_key('packet_len')
        self.iio_fmcomms2_source_0.set_frequency(int(lo))
        self.iio_fmcomms2_source_0.set_samplerate(int(samp_rate))
        if True:
            self.iio_fmcomms2_source_0.set_gain_mode(0, 'manual')
            self.iio_fmcomms2_source_0.set_gain(0, rx_gain)
        if False:
            self.iio_fmcomms2_source_0.set_gain_mode(1, 'slow_attack')
            self.iio_fmcomms2_source_0.set_gain(1, 64)
        self.iio_fmcomms2_source_0.set_quadrature(True)
        self.iio_fmcomms2_source_0.set_rfdc(True)
        self.iio_fmcomms2_source_0.set_bbdc(True)
        self.iio_fmcomms2_source_0.set_filter_params('Auto', 'C:\\Users\\yutan\\WorkSpace\\ADALM-PLUTO-Examples\\designed filter\\lpf_EPB-7.5kSSB-62k.txt', 0, 0)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(upsampling, lpf_taps, lo, samp_rate)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_MOD_MUELLER_AND_MULLER,
            sps,
            sync_loop_bw,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            32,
            rrc_taps)
        self.digital_map_bb_0 = digital.map_bb([0,1])
        self.digital_fll_band_edge_cc_0 = digital.fll_band_edge_cc(sps, Alpha, 44, fll_loop_bw)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.digital_crc_check_0 = digital.crc_check(16, 0x1021, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, True, 0)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(costas_loop_bw, 2, False)
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts('access_key',
          thresh, 'packet_len')
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(const)
        self.blocks_tagged_stream_align_0 = blocks.tagged_stream_align(gr.sizeof_char*1, 'packet_len')
        self.blocks_tag_debug_1 = blocks.tag_debug(gr.sizeof_char*1, '', "frame_len")
        self.blocks_tag_debug_1.set_display(True)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_char*1, '', "frame_seq")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_repack_bits_bb_1_0_0 = blocks.repack_bits_bb(1, 8, "packet_len", True, gr.GR_MSB_FIRST)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_agc_xx_0 = analog.agc_cc((1e-4), 1.0, 1.0, 2.0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.digital_crc_check_0, 'fail'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.digital_crc_check_0, 'ok'), (self.parse_telecmd, 'pdu_in'))
        self.msg_connect((self.parse_telecmd, 'pdu_out'), (self.pdu_pdu_to_tagged_stream_2, 'pdus'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0_0, 'pdus'), (self.digital_crc_check_0, 'in'))
        self.connect((self.analog_agc_xx_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0_0, 0), (self.pdu_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_tagged_stream_align_0, 0), (self.blocks_repack_bits_bb_1_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_tagged_stream_align_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_fll_band_edge_cc_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.digital_fll_band_edge_cc_0, 0))
        self.connect((self.iio_fmcomms2_source_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_2, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_2, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_2, 0), (self.blocks_tag_debug_1, 0))


    def get_upsampling(self):
        return self.upsampling

    def set_upsampling(self, upsampling):
        self.upsampling = upsampling
        self.set_samp_rate(self.baud_rate*self.sps*self.upsampling)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.Alpha, 11*self.sps*self.nfilts))
        self.set_samp_rate(self.baud_rate*self.sps*self.upsampling)
        self.digital_symbol_sync_xx_0.set_sps(self.sps)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_samp_rate(self.baud_rate*self.sps*self.upsampling)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lpf_taps(firdes.low_pass(1, self.samp_rate, self.samp_rate/4, 3e3, window.WIN_HAMMING, 6.76))
        self.iio_fmcomms2_source_0.set_samplerate(int(self.samp_rate))

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.Alpha, 11*self.sps*self.nfilts))

    def get_Alpha(self):
        return self.Alpha

    def set_Alpha(self, Alpha):
        self.Alpha = Alpha
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.Alpha, 11*self.sps*self.nfilts))

    def get_thresh(self):
        return self.thresh

    def set_thresh(self, thresh):
        self.thresh = thresh

    def get_sync_loop_bw(self):
        return self.sync_loop_bw

    def set_sync_loop_bw(self, sync_loop_bw):
        self.sync_loop_bw = sync_loop_bw
        self.digital_symbol_sync_xx_0.set_loop_bandwidth(self.sync_loop_bw)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.iio_fmcomms2_source_0.set_gain(0, self.rx_gain)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps

    def get_lpf_taps(self):
        return self.lpf_taps

    def set_lpf_taps(self, lpf_taps):
        self.lpf_taps = lpf_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.lpf_taps)

    def get_lo(self):
        return self.lo

    def set_lo(self, lo):
        self.lo = lo
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.lo)
        self.iio_fmcomms2_source_0.set_frequency(int(self.lo))

    def get_fll_loop_bw(self):
        return self.fll_loop_bw

    def set_fll_loop_bw(self, fll_loop_bw):
        self.fll_loop_bw = fll_loop_bw
        self.digital_fll_band_edge_cc_0.set_loop_bandwidth(self.fll_loop_bw)

    def get_costas_loop_bw(self):
        return self.costas_loop_bw

    def set_costas_loop_bw(self, costas_loop_bw):
        self.costas_loop_bw = costas_loop_bw
        self.digital_costas_loop_cc_0.set_loop_bandwidth(self.costas_loop_bw)

    def get_const(self):
        return self.const

    def set_const(self, const):
        self.const = const
        self.digital_constellation_decoder_cb_0.set_constellation(self.const)




def main(top_block_cls=bpsk_demo_rx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
