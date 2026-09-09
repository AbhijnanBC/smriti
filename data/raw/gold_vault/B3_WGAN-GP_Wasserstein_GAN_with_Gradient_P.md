# B3. WGAN-GP: Wasserstein GAN with Gradient Penalty

**Source:** arXiv (Gulrajani et al., 2017)

The Wasserstein GAN (WGAN) improved the stability of GAN training by using the Wasserstein distance as the loss function. However, it requires clipping the weights of the discriminator, which can lead to undesirable artifacts. The WGAN-GP (Gradient Penalty) variant replaces weight clipping with a gradient penalty term that enforces the Lipschitz constraint more effectively.

In the context of financial time series modeling, WGAN-GP has been successfully used to generate synthetic data that captures the statistical properties of real market data. For example, an LSTM-based WGAN-GP can learn the distribution of price movements and generate realistic sequences that are visually indistinguishable from the original data.

The generator and discriminator are trained adversarially, with the gradient penalty encouraging the discriminator to have gradients of norm 1 everywhere. This stabilizes training and allows the use of deeper networks, making WGAN-GP a powerful tool for generative modeling across domains.
