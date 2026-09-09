# B2. StyleGAN2 Style Space Analysis and Disentanglement

**Source:** arXiv / Computer Vision Foundation

Beyond improving image quality, StyleGAN2 also introduced a new concept called the "style space" (or W+ space) that provides greater disentanglement of visual attributes. Researchers have analyzed this space using models pretrained on various datasets and found that certain dimensions correspond to specific semantic attributes.

The modulation of channel-wise variances via weight modulation allows for finer control over individual features without affecting others. This disentanglement is crucial for applications such as image editing, where users want to modify one aspect of an image (e.g., smile) while leaving others unchanged.

StyleGAN2 also demonstrated that the intermediate latent space is more suitable for style mixing and inversion than the original latent space (Z). Inversion methods can recover a latent vector from a real image, enabling realistic image editing and manipulation.
