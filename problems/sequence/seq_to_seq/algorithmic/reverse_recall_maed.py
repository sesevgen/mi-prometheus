#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""serial_recall_original.py: Original serial recall problem (a.k.a. copy task)"""
__author__      = "Ryan L. McAvoy"

import torch
import numpy as np
from utils import augment, add_ctrl
from algorithmic_sequential_problem import AlgorithmicSequentialProblem
from algorithmic_sequential_problem import DataTuple, AuxTuple


@AlgorithmicSequentialProblem.register
class ReverseRecallMaed(AlgorithmicSequentialProblem):
    """   
    Class generating sequences of random bit-patterns and targets forcing the system to learn serial recall problem (a.k.a. copy task).
    The formulation follows the original copy task from NTM paper, where:
    1) There are two markers, indicating
    - beginning of storing/memorization and
    - beginning of recalling from memory.
    2) For other elements of the sequence the command bits are set to zero
    3) Minor modification I: the target contains only data bits (command bits are skipped)
    4) Minor modification II: generator returns a mask, which can be used for filtering important elements of the output.
    
    TODO: sequences of different lengths in batch (filling with zeros?)
    """
    def __init__(self,  params):
        """ 
        Constructor - stores parameters.
        
        :param params: Dictionary of parameters.
        """
        # Retrieve parameters from the dictionary.
        self.batch_size = params['batch_size']
        # Number of bits in one element.
        self.control_bits = params['control_bits']
        self.data_bits = params['data_bits']
        assert self.control_bits >=2, "Problem requires at least 2 control bits (currently %r)" % self.control_bits
        assert self.data_bits >=2, "Problem requires at least 1 data bit (currently %r)" % self.data_bits
        # Min and max lengts (number of elements).
        self.min_sequence_length = params['min_sequence_length']
        self.max_sequence_length = params['max_sequence_length']

        # Parameter  denoting 0-1 distribution (0.5 is equal).
        self.bias = params['bias']
        self.dtype = torch.FloatTensor

    def generate_batch(self):
        """Generates a batch  of size [BATCH_SIZE, 2*SEQ_LENGTH+2, CONTROL_BITS+DATA_BITS].
        Additional elements of sequence are  start and stop control markers, stored in additional bits.
       
        : returns: Tuple consisting of: input [BATCH_SIZE, 2*SEQ_LENGTH+2, CONTROL_BITS+DATA_BITS], 
        output [BATCH_SIZE, 2*SEQ_LENGTH+2, DATA_BITS],
        mask [BATCH_SIZE, 2*SEQ_LENGTH+2]

        TODO: every item in batch has now the same seq_length.
        """

        # define control channel markers
        pos = [0, 0, 0]
        ctrl_data = [0, 0, 0]
        ctrl_inter = [0, 1, 0]
        ctrl_y = [0, 0, 1]
        ctrl_dummy = [1, 1, 1]
        ctrl_start = [1, 0, 0]
        # assign markers
        markers = ctrl_data, ctrl_dummy, pos

        # Set sequence length
        seq_length = np.random.randint(self.min_sequence_length, self.max_sequence_length+1)

        # Generate batch of random bit sequences [BATCH_SIZE x SEQ_LENGTH X DATA_BITS]
        bit_seq = np.random.binomial(1, self.bias, (self.batch_size, seq_length, self.data_bits))

        #Generate target by indexing through the array
        target_seq = np.array(np.fliplr(bit_seq))


        #  generate subsequences for x and y
        x = [np.array(bit_seq)]
        # data of x and dummies
        xx = [ augment(seq, markers, ctrl_start=ctrl_start, add_marker_data=True, add_marker_dummy = False) for seq in x ]       

        # data of x
        data_1 = [arr for a in xx for arr in a[:-1]]


        # this is a marker between sub sequence x and dummies
        #inter_seq = [add_ctrl(np.zeros((self.batch_size, 1, self.data_bits)), ctrl_inter, pos)]
       
        #dummies output
        markers2 = ctrl_dummy, ctrl_dummy, pos
        yy = [ augment(np.zeros(target_seq.shape), markers2, ctrl_start=ctrl_inter, add_marker_data=True, add_marker_dummy = False)]
        data_2 = [arr for a in yy for arr in a[:-1]]
 
         
        #add dummies to target
        seq_length_tdummies = seq_length+2
        dummies_target = np.zeros([self.batch_size, seq_length_tdummies, self.data_bits], dtype=np.float32)
        targets = np.concatenate((dummies_target, target_seq), axis=1)

        inputs = np.concatenate(data_1 + data_2, axis=1)

        # PyTorch variables
        inputs = torch.from_numpy(inputs).type(self.dtype)
        targets = torch.from_numpy(targets).type(self.dtype)
        # TODO: batch might have different sequence lengths
        mask_all = inputs[..., 0:self.control_bits] == 1
        mask = mask_all[..., 0]
        for i in range(self.control_bits):
            mask = mask_all[..., i] * mask
        # TODO: fix the batch indexing
        # rest channel values of data dummies
        #inputs[:, mask[0], 0:self.control_bits] = ctrl_dummy
        # TODO: fix the batch indexing
        # rest channel values of data dummies

        inputs[:, mask[0], 0:self.control_bits] = torch.tensor(ctrl_y).type(self.dtype)

        # Return data tuple.
        data_tuple = DataTuple(inputs, targets)
        aux_tuple = AuxTuple(mask)

        return data_tuple, aux_tuple

    # method for changing the maximum length, used mainly during curriculum learning
    def set_max_length(self, max_length):
        self.max_sequence_length = max_length

if __name__ == "__main__":
    """ Tests sequence generator - generates and displays a random sample"""
    
    # "Loaded parameters".
    params = {'control_bits': 3, 'data_bits': 8, 'batch_size': 1, 
        'min_sequence_length': 1, 'max_sequence_length': 10,  'bias': 0.5, 'seq_start':0, 'skip_step': 2}
    # Create problem object.
    problem = ReverseRecallMaed(params)
    # Get generator
    generator = problem.return_generator()
    # Get batch.
    data_tuple, aux_tuple = next(generator)
    # Display single sample (0) from batch.
    problem.show_sample(data_tuple, aux_tuple)