function dens = d_mixedmvST (y, pi1, mu, Sigma, lambda, nu)

    % y: the data matrix
    % pi1: must be of the vector type of dimension g
    % mu: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    % Sigma: must be of type list with g entries. Each entry in the list must be an matrix p x p
    % lambda: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    % nu: a number

    g = numel(pi1);
    dens = 0;
    for j = 1 : g
        dens = dens + pi1(j) .* dmvt_ls(y, mu{j}, Sigma{j}, lambda{j}, nu);
    end
end