# B1. StyleGAN2 -- Improvements in Generative Adversarial Networks

**Source:** NVIDIA Research / arXiv (Karras et al., 2019)

The style-based GAN architecture (StyleGAN) introduced a novel generator design that enables unprecedented control over the generated images. However, StyleGAN exhibited characteristic artifacts, such as water droplets and texture noise, which limited its practical applications.

StyleGAN2 addresses these issues with several key improvements:

- **Redesign of Generator Normalization:** The original AdaIN (adaptive instance normalization) was replaced with a weight-modulation and demodulation approach that eliminates the need for regularized normalization, reducing artifacts and improving image quality.
- **Revisiting Progressive Growing:** Progressive growing, which incrementally increases resolution during training, was found to cause some artifacts. StyleGAN2 instead uses a skip-connection architecture and a new regularizer, removing progressive growing entirely.
- **Path Length Regularizer:** This regularizer encourages the mapping from latent vectors to images to be well-conditioned, making the generator easier to invert and improving the quality of interpolations.

The improved model sets a new state of the art in unconditional image generation on several benchmark datasets, producing images with superior fidelity and fewer artifacts. Additionally, the path length regularizer enables easier manipulation of the latent space, allowing users to control specific features (e.g., age, pose, hair color) in the generated images.
