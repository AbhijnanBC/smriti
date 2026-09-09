# B5. U-Net: Convolutional Network for Medical Image Segmentation

**Source:** arXiv (Ronneberger et al., 2015)

U-Net is a convolutional neural network designed for biomedical image segmentation. It was developed to work with very few training images (as low as 30) and still produce accurate segmentations. The architecture consists of two paths:

- **Contracting Path (Encoder):** A typical convolutional network that extracts features at multiple scales. It reduces the spatial resolution while increasing the number of feature channels.
- **Expanding Path (Decoder):** Uses up-convolutional layers to increase the spatial resolution, while concatenating feature maps from the corresponding encoder levels. This allows the network to combine high-level semantic information with fine-grained spatial details.

The U-like shape, with skip connections that bridge the encoder and decoder, enables precise localization. U-Net has become the de facto standard for medical image segmentation in tasks such as brain tumor segmentation, lung nodule detection, and cell counting.
