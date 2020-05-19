function dens = dmvt_ls (y, mu, Sigma, lambda, nu)
    % This function computes Density/CDF of Skew-T with scale location.
    % y must be a matrix where each row has 
    %    a multivariate vector of dimension 
    %    ncol(y) = p , nrow(y) = sample size.
    % mu, lambda: must be of the vector type of 
    %             the same dimension equal to ncol(y) = p
    % lambda: 1 x p
    % Sigma: Matrix p x p
    nrow = @(x) size(x,1); 
    ncol = @(x) size(x,2);
    n = nrow(y);
    p = ncol(y);
    mahalanobis_d = (pdist2(y,mu,'mahalanobis',Sigma)).^2;
    denst = (gamma((p + nu)./2)./(gamma(nu./2) .* pi.^(p./2))) .* ...
            nu.^(-p./2) .* det(Sigma).^(-1/2) .* ...
            (1 + mahalanobis_d./nu).^(-(p + nu)./2);
    dens = 2 .* (denst) .* tcdf(sqrt((p + nu)./(mahalanobis_d + nu)) .* sum(repmat(lambda / matrix_sqrt(Sigma), n, 1) .* (y - mu), 2), nu + p);
end