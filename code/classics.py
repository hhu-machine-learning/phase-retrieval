import numpy as np

def fienup_phase_retrieval(mag, init_phi=None, mask=None, threshhold=0, beta=0.8, 
                           steps=200, mode='hybrid', verbose=False):
    """
    Implementation of Fienup's phase-retrieval methods. This function
    implements the input-output, the output-output and the hybrid method.
    
    Note: Mode 'output-output' and beta=1 results in 
    the Gerchberg-Saxton algorithm.
    
    Parameters:
        mag: Measured magnitudes of Fourier transform
        mask: Binary array indicating where the image should be
              if padding is known
        beta: Positive step size
        steps: Number of iterations
        mode: Which algorithm to use
              (can be 'input-output', 'output-output' or 'hybrid')
        verbose: If True, progress is shown
    
    Returns:
        x: Reconstructed image
    
    Author: Tobias Uelwer
    Date: 30.12.2018
    
    GS-Algorithm included by Alexander Oberstrass
    Date: 22.02.2020
    
    References:
    [1] E. Osherovich, Numerical methods for phase retrieval, 2012,
        https://arxiv.org/abs/1203.4756
    [2] J. R. Fienup, Phase retrieval algorithms: a comparison, 1982,
        https://www.osapublishing.org/ao/abstract.cfm?uri=ao-21-15-2758
    [3] https://github.com/cwg45/Image-Reconstruction
    """
    
    assert beta > 0, 'step size must be a positive number'
    assert steps > 0, 'steps must be a positive number'
    assert mode == 'input-output' or mode == 'output-output'\
        or mode == 'hybrid' or mode == 'gs',\
    'mode must be \'input-output\', \'output-output\' or \'hybrid\''
    
    if mask is None:
        mask = np.ones(mag.shape)
        
    assert mag.shape == mask.shape, 'mask and mag must have same shape'
    
    # sample random phase and initialize image x
    if init_phi is None:
        init_phi = 2*np.pi*np.random.rand(*mag.shape)
 
    y_hat = mag*np.exp(1j * init_phi)
    x = np.zeros(mag.shape)
    
    # previous iterate
    x_p = None
    
    constraint_numbers = []
    errors = []
        
    # main loop
    for i in range(1, steps+1):
        # show progress
        if i % 100 == 0 and verbose: 
            print("step", i, "of", steps)
        
        # inverse fourier transform
        y = np.real(np.fft.ifft2(y_hat))
        
        # previous iterate
        if x_p is None:
            x_p = y
        else:
            x_p = x 
        
        # updates for elements that satisfy object domain constraints
        if mode == "output-output" or mode == "hybrid" or mode == 'gs':
            x = y
            
        # find elements that violate object domain constraints 
        # or are not masked
        indices = np.logical_or(np.logical_and(y < threshhold, mask), 
                                np.logical_not(mask))
        
        # compute signal domain error (for all expect gs)
        if mode != 'gs':
            errors.append(np.sum(x[indices] ** 2))
        
        if i % 100 == 0 and verbose: 
            print(np.sum(indices), "open constraints")
        
        # updates for elements that violate object domain constraints
        if mode == "hybrid" or mode == "input-output":
            x[indices] = x_p[indices]-beta*y[indices] 
        elif mode == "output-output":
            x[indices] = y[indices]-beta*y[indices]
        elif mode == 'gs':
            x[indices] = 0
        
        # fourier transform
        x_hat = np.fft.fft2(x)
        
        # compute magn error (only meaningful for gs
        if mode == 'gs':
            errors.append(np.mean((np.abs(x_hat) - mag) ** 2))
        
        # satisfy fourier domain constraints
        # (replace magnitude with input magnitude)
        y_hat = mag*np.exp(1j*np.angle(x_hat))
        
    return x, errors
