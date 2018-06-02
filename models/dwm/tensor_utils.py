import torch
import torch.nn.functional as F
import numpy as np

def normalize(x):
    """
    Normalizes the input torch tensor along the last dimension using the max of the one norm
    The normalization is "fuzzy" to prevent divergences
    
    :param x: All inputs  [BATCH_SIZE x A x B ..]
    :return:  normalized x [BATCH_SIZE x A x B ..]
    """

    return x / torch.max(torch.sum(x, dim=-1, keepdim=True), torch.Tensor([1e-12]))

def sim(query, data, l2_normalize=False, aligned=True):
    """
    Batch dot-product similarity computed using matrix multiplication
    the hidden shapes must be broadcastable (numpy style)
    
    :param query: the input data to be compared  [BATCH_SIZE x h X p ] p = N if aligned is True and p = M if aligned is False
    :param data: Input state  [BATCH_SIZE x CONTENT_SIZE x MEMORY_SIZE]
    :param l2_normalize: boolean, determines where to normalize the query and the data before the dot product
    :param aligned: boolean, determines whether to transpose data along the last two dimensions 
    :return:  out[...,i,j] = sum_k q[...,i,k] * data_gen[...,j,k] for the default options
    """

    # data_gen.shape = hidden_shape_1 x M x N
    # query.shape = hidden_shape_2 x h x p, where:
    #        p = N if aligned is True and p = M if aligned is False
    # out[...,i,j] = sum_k q[...,i,k] * data_gen[...,j,k] for the default options

    if aligned:  # transpose last 2 dims to enable matrix multiplication
        data = torch.transpose(data, -1, -2)

    assert query.size()[-1] == data.size()[-2]

    if l2_normalize:
        query = F.normalize(query, dim=-1)
        data = F.normalize(data, dim=-2)

    return torch.matmul(query, data)


# Batch outer product of two vectors
# the hidden shapes must be broadcastable (numpy style)
def outer_prod(x, y):
    """
    Batch outer product of two vectors (along the last two dimensions)
    the hidden shapes must be broadcastable (numpy style)
    
    
    :param x: input one  [BATCH_SIZE x A ]
    :param y: Input two  [BATCH_SIZE x B]
    :return: Outer product [BATCH_SIZE x A x B]
    """

    return x[..., :, None] * y[..., None, :]


def circular_conv(x, f):
    """
    Batch 1D circular convolution with matching hidden shapes
    
    :param x: input [batch_size, num_head, num_addresses]
    :param f: shift array  [batch_size, num_heads, shift_size]
    :return: Circular convolution [batch_size, num_head, num_addresses]
    """

    # computes y[...,i] = sum_{j=-ceil(s/2)+1}^{floor(s/2)} x[...,i-j] * f[...,j]

    # check if number of addresses (x represents the attention) is larger than the filer size
    f_last = f.size()[-1]
    assert (f_last >= 3) and (f_last <= x.size()[-1]), "filter size constraint violated"

    # check the number of heads and batch_size is the same for the filter and the attention
    f_other = f.size()[:-1]
    assert f_other == x.size()[:-1], "hidden shapes should match"

    y = x.clone()
    ind_left = f_last // 2
    ind_right = f_last - ind_left - 1
    # padding to wrap x with itself
    x = torch.cat([x[..., -ind_left:], x, x[..., :ind_right]], dim=-1)

    # loop over indices in the hidden shape
    for ix in np.ndindex(f_other):
        y[ix] = F.conv1d(x[ix][None, None, :], f[ix][None, None, :])
    return y

