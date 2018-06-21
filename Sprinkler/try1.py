"""Softmax."""

scores = [3.0, 1.0, 0.2]

import numpy as np

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    denm = sum([np.exp(k) for k in x])
    res = [np.exp(k)/denm for k in x]

    return res  # TODO: Compute and return softmax(x)


print(softmax(scores))

# Plot softmax curves
# import matplotlib.pyplot as plt
# x = np.arange(-2.0, 6.0, 0.1)
# scores = np.vstack([x, np.ones_like(x), 0.2 * np.ones_like(x)])
#
# plt.plot(x, softmax(scores), linewidth=2)
# plt.show()
