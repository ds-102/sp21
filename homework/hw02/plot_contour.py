
# You don't have to understand how this function works.
def plot_contour(mean_vector, covariance_matrix):
    """
    Displays a contour plot for the bivariate normal with the given mean/covariance.
    
    Assumes that the first dimension is coeffs for ideology
    and the second dimension is coeffs for '18 margin
    """
    σ_x1 = np.sqrt(covariance_matrix[0, 0])
    σ_x2 = np.sqrt(covariance_matrix[1, 1])
    μ_x1, μ_x2 = mean_vector
    
    x1 = np.linspace(μ_x1 - 2.5 * σ_x1, μ_x1 + 2.5 * σ_x1, 200)
    x2 = np.linspace(μ_x2 - 2.5 * σ_x2, μ_x2 + 2.5 * σ_x2, 200)
    dist = stats.multivariate_normal(mean_vector, covariance_matrix)
    X1, X2 = np.meshgrid(x1, x2)
    pdf_values = dist.pdf(np.dstack([X1, X2]))
    plt.figure(figsize=(4, 4))
    plt.contour(X1, X2, pdf_values)
    plt.xlabel('$\\beta$ for Ideology')
    plt.ylabel('$\\beta$ for Dem18Margin')
    plt.axis([-0.8, 0.5, -0.2, 1.3])